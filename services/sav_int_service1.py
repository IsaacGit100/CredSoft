from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from MembersApp.models import Master
from django_ledger.models import (
    EntityModel,
    JournalEntryModel,
    TransactionModel,
    AccountModel,
    LedgerModel,
)
from djan_led.models import EntityConfig


class InterestAccrualService:
    QUARTER_END_MONTHS = [3, 6, 9, 12]

    def __init__(self, entity_slug):
        """
        Initialize with entity slug to get entity and its config.
        """
        self.entity = get_object_or_404(EntityModel, slug=entity_slug)
        self.config, _ = EntityConfig.objects.get_or_create(entity=self.entity)
        self.today = timezone.now().date()
        self.application_frequency = (
            self.config.savings_interest_application or "MONTHLY"
        )
        self.savings_calc_type = self.config.savings_calc_type or "Simple_Sav_Interest"

    def get_days_since_last_accrual(self):
        """Calculate number of days since last interest calculation."""
        if not self.config.last_interest_accrual_date:
            return 1
        last_date = self.config.last_interest_accrual_date
        if isinstance(last_date, datetime):
            last_date = last_date.date()
        days = (self.today - last_date).days
        return max(days, 1)

    def calculate_interest_for_period(self, member, days):
        """Calculate interest for a number of days using member's daily_interest property."""
        # Use member's rate if set, else fallback to entity config
        if member.sav_int_rate and member.sav_int_rate > 0:
            int_rate = member.sav_int_rate
        else:
            int_rate = self.config.savings_interest_rate

        if int_rate <= 0:
            return Decimal("0.00")

        # Daily interest is already computed in member model; if not, compute
        if hasattr(member, "daily_interest"):
            daily = member.daily_interest
        else:
            # Fallback: calculate daily = (balance * rate) / 365 / 100
            daily = (member.sav_avail_bal * Decimal(int_rate)) / Decimal("36500")

        if daily <= Decimal("0.00"):
            return Decimal("0.00")

        return (daily * Decimal(str(days))).quantize(Decimal("0.01"))

    def should_apply_interest(self):
        """Check if interest should be applied based on frequency."""
        if self.application_frequency == "DAILY":
            return True
        elif self.application_frequency == "MONTHLY":
            next_day = self.today + timedelta(days=1)
            return next_day.month != self.today.month
        elif self.application_frequency == "QUARTERLY":
            next_day = self.today + timedelta(days=1)
            is_quarter_end = self.today.month in self.QUARTER_END_MONTHS
            is_last_day = next_day.month != self.today.month
            return is_quarter_end and is_last_day
        elif self.application_frequency == "YEARLY":
            return self.today.month == 12 and self.today.day == 31
        return False

    def apply_interest_to_deposit(self, member):
        """Apply accrued interest to member's deposit balance."""
        if not member.sav_int_accrued or member.sav_int_accrued <= Decimal("0.00"):
            return False

        interest_amount = member.sav_int_accrued
        member.tot_deposits = (member.tot_deposits or 0) + interest_amount
        member.sav_int_accrued = Decimal("0.00")
        member.tot_interest_accrued = (
            member.tot_interest_accrued or 0
        ) + interest_amount
        member.save()

        self.create_interest_application_journal(member, interest_amount)
        return True

    def create_interest_application_journal(self, member, interest_amount):
        """Create journal entry using django‑ledger."""
        try:
            # Get ledger for the entity
            ledger = LedgerModel.objects.filter(entity=self.entity).first()
            if not ledger:
                ledger = LedgerModel.objects.create(
                    entity=self.entity, name="Default Ledger"
                )

            # Find accounts using AccountModel
            # Savings account (liability – interest payable to members)
            # Interest expense account (expense)
            coa = self.entity.get_default_coa()
            if not coa:
                raise ValueError("No Chart of Accounts for entity")

            # We'll try to get accounts by code; you can adjust codes
            savings_account = AccountModel.objects.get(
                coa_model=coa, code="20101001"
            )  # adjust code
            interest_expense = AccountModel.objects.get(
                coa_model=coa, code="50103001"
            )  # adjust code

            # Create Journal Entry (draft)
            je = JournalEntryModel.objects.create(
                ledger=ledger,
                timestamp=self.today,
                description=f"Interest application - {member.full_name} ({self.application_frequency})",
                posted=False,
            )

            # Debit interest expense
            TransactionModel.objects.create(
                journal_entry=je,
                account=interest_expense,
                amount=interest_amount,
                tx_type="debit",
            )
            # Credit savings account (liability)
            TransactionModel.objects.create(
                journal_entry=je,
                account=savings_account,
                amount=interest_amount,
                tx_type="credit",
            )

            # Post the entry
            je.posted = True
            je.save()

            return je

        except AccountModel.DoesNotExist as e:
            print(f"Account not found: {e}")
            return None
        except Exception as e:
            print(f"Error creating journal: {e}")
            return None
        
    def run_daily_accrual(self, dry_run=False):
        """Main method to run daily interest accrual and application."""
        results = {
            "accrued": [],
            "applied": [],
            "failed": [],
            "total_accrued": Decimal("0.00"),
            "total_applied": Decimal("0.00"),
            "days_since_last": 0,
            "application_frequency": self.application_frequency,
            "should_apply": False,
        }

        days = self.get_days_since_last_accrual()
        results["days_since_last"] = days

        should_apply = self.should_apply_interest()
        results["should_apply"] = should_apply

        if days <= 0:
            return results

        members = Master.objects.filter(is_deleted=False)

        with transaction.atomic():
            for member in members:
                try:
                    interest = self.calculate_interest_for_period(member, days)

                    if interest > Decimal("0.00"):
                        member.sav_int_accrued = (
                            member.sav_int_accrued or 0
                        ) + interest
                        member.save()

                        results["accrued"].append(
                            {
                                "member_id": member.id,
                                "member_name": member.full_name,
                                "interest": interest,
                                "daily_rate": (
                                    float(member.daily_interest)
                                    if hasattr(member, "daily_interest")
                                    else 0
                                ),
                                "days": days,
                                "accrued_balance": float(member.sav_int_accrued),
                                "current_balance": float(member.sav_avail_bal),
                                "effective_rate": float(
                                    self.config.savings_interest_rate
                                ),
                            }
                        )
                        results["total_accrued"] += interest

                        if should_apply:
                            self.apply_interest_to_deposit(member)
                            results["applied"].append(
                                {
                                    "member_id": member.id,
                                    "member_name": member.full_name,
                                    "interest": interest,
                                    "frequency": self.application_frequency,
                                    "new_balance": float(member.sav_avail_bal),
                                }
                            )
                            results["total_applied"] += interest
                    else:
                        results["accrued"].append(
                            {
                                "member_id": member.id,
                                "member_name": member.full_name,
                                "interest": Decimal("0.00"),
                                "days": days,
                                "note": "No interest (rate or balance zero)",
                                "daily_rate": (
                                    float(member.daily_interest)
                                    if hasattr(member, "daily_interest")
                                    else 0
                                ),
                                "balance": float(member.sav_avail_bal),
                                "rate": float(self.config.savings_interest_rate),
                            }
                        )

                except Exception as e:
                    results["failed"].append(
                        {
                            "member_id": member.id,
                            "member_name": member.full_name,
                            "error": str(e),
                        }
                    )

            # Update last accrual date and time in EntityConfig
            self.config.last_interest_accrual_date = self.today
            self.config.last_interest_accrual_run = timezone.now()
            self.config.save()

        return results

    def get_next_application_date(self):
        """Calculate next interest application date."""
        today = self.today
        if self.application_frequency == "DAILY":
            return today + timedelta(days=1)
        elif self.application_frequency == "MONTHLY":
            return today + relativedelta(months=1)
        elif self.application_frequency == "QUARTERLY":
            if today.month < 3:
                return date(today.year, 3, 31)
            elif today.month < 6:
                return date(today.year, 6, 30)
            elif today.month < 9:
                return date(today.year, 9, 30)
            elif today.month < 12:
                return date(today.year, 12, 31)
            else:
                return date(today.year + 1, 3, 31)
        elif self.application_frequency == "YEARLY":
            return date(today.year, 12, 31)
        return today + timedelta(days=30)
