# services/interest_accrual_service.py
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from MembersApp.models import Master, Sav_Int_Table
from djan_led.models import EntityConfig
from django_ledger.models import EntityModel
from .journal_engine import JournalEngine

logger = logging.getLogger(__name__)


class InterestAccrualService:
    QUARTER_END_MONTHS = [3, 6, 9, 12]

    def __init__(self, entity_slug, engine=None):
        self.entity = get_object_or_404(EntityModel, slug=entity_slug)
        self.config, _ = EntityConfig.objects.get_or_create(entity=self.entity)
        self.today = timezone.now().date()
        self.application_frequency = (
            self.config.savings_interest_application or "MONTHLY"
        )

        if engine is not None:
            self.engine = engine
        else:
            self.engine = JournalEngine(entity_slug)

    # ---------- helpers ----------
    def get_days_since_last_accrual(self):
        if not self.config.last_interest_accrual_date:
            return 1
        last_date = self.config.last_interest_accrual_date
        if isinstance(last_date, datetime):
            last_date = last_date.date()
        days = (self.today - last_date).days
        return max(days, 1)

    def calculate_interest_for_period(self, member, days):
        # use member rate or config rate
        if member.sav_int_rate and member.sav_int_rate > 0:
            rate = member.sav_int_rate
        else:
            rate = self.config.savings_interest_rate

        if rate <= 0:
            return Decimal("0.00")

        balance = member.sav_avail_bal
        if balance <= 0:
            return Decimal("0.00")

        # daily interest = balance * rate / 365 / 100
        daily = (balance * Decimal(rate)) / Decimal("36500")
        interest = (daily * Decimal(str(days))).quantize(Decimal("0.01"))
        return interest

    def should_apply_interest(self):
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

    def _get_account_codes(self):
        expense_code = getattr(self.config, "interest_expense_account_code", "5020")
        payable_code = getattr(
            self.config, "savings_interest_payable_account_code", "2020"
        )
        return expense_code, payable_code

    def create_interest_application_journal(self, member, amount):
        if amount <= Decimal("0.00"):
            return None
        try:
            expense_code, payable_code = self._get_account_codes()
            description = f"Interest applied - {member.full_name} ({self.application_frequency}) {self.today}"
            journal = self.engine.record_transaction(
                amount=amount,
                debit_account_code=expense_code,
                credit_account_code=payable_code,
                description=description,
                date=self.today,
            )
            logger.info(f"Interest journal created: {journal.uuid}")
            return journal
        except Exception as e:
            logger.error(f"Journal creation failed: {e}")
            raise

    # ---------- main runner ----------
    def run_daily_accrual(self, force_apply=False):
        print("=" * 60)
        print("INTEREST ACCRUAL RUN (saving enabled)")
        print(f"Date: {self.today}, frequency: {self.application_frequency}")
        print("=" * 60)

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
        if days <= 0:
            print("No days to process, exiting.")
            return results

        should_apply = self.should_apply_interest() or force_apply
        results["should_apply"] = should_apply
        print(f"Apply now: {should_apply} (force_apply={force_apply})")

        members = Master.objects.filter(is_deleted=False)
        print(f"Members: {members.count()}")

        with transaction.atomic():
            # ---- Daily accrual & audit ----
            for member in members:
                try:
                    interest = self.calculate_interest_for_period(member, days)
                    print(f"\nMember {member.id}: interest = {interest}")

                    # 1. Create audit record in Sav_Int_Table
                    Sav_Int_Table.objects.create(
                        entity=self.entity,
                        date=self.today,
                        master=member,
                        balance=member.sav_avail_bal,
                        sav_int_rate=member.sav_int_rate
                        or self.config.savings_interest_rate,
                        no_of_days=days,
                        sav_int=interest,
                        last_updated_date=self.today,
                        update_type=self.application_frequency,
                        next_update_date=self.get_next_application_date(),
                        applied=False,  # audit only, not used for application
                    )
                    print(f"  Audit record created")

                    # 2. Accrue to Master
                    member.tot_mnth_sav_int_accrued = (
                        member.tot_mnth_sav_int_accrued or 0
                    ) + interest
                    member.sav_int_accrued_days = (
                        member.sav_int_accrued_days or 0
                    ) + days
                    member.save(
                        update_fields=[
                            "tot_mnth_sav_int_accrued",
                            "sav_int_accrued_days",
                        ]
                    )
                    print(f"  Accrued -> now {member.tot_mnth_sav_int_accrued}")

                    results["accrued"].append(
                        {
                            "member_id": member.id,
                            "member_name": member.full_name,
                            "interest": float(interest),
                            "days": days,
                            "balance": float(member.sav_avail_bal),
                        }
                    )
                    results["total_accrued"] += interest

                except Exception as e:
                    print(f"  ERROR: {e}")
                    import traceback

                    traceback.print_exc()
                    results["failed"].append(
                        {
                            "member_id": member.id,
                            "member_name": member.full_name,
                            "error": str(e),
                        }
                    )

            # ---- Application (if needed) ----
            if should_apply:
                print("\n--- Applying accrued interest ---")
                for member in members:
                    total = member.tot_mnth_sav_int_accrued or Decimal("0.00")
                    if total > Decimal("0.00"):
                        # Update deposit and reset accrual fields
                        member.tot_sav_int = (member.tot_sav_int or 0) + total
                        member.balance = (member.balance or 0) + total
                        member.tot_mnth_sav_int_accrued = Decimal("0.00")
                        member.sav_int_accrued_days = 0
                        member.save()
                        print(
                            f"Member {member.id}: applied {total}, new balance {member.tot_deposits}"
                        )

                        # Create journal entry
                        self.create_interest_application_journal(member, total)

                        results["applied"].append(
                            {
                                "member_id": member.id,
                                "member_name": member.full_name,
                                "amount": float(total),
                                "new_balance": float(member.tot_deposits),
                            }
                        )
                        results["total_applied"] += total
                    else:
                        print(f"Member {member.id}: no accrued interest to apply")

            # ---- Update last accrual date ----
            self.config.last_interest_accrual_date = self.today
            self.config.last_interest_accrual_run = timezone.now()
            self.config.save()
            print("\nUpdated last_interest_accrual_date.")

        print("=" * 60)
        print("FINISHED")
        print(f"Total accrued: {results['total_accrued']}")
        print(f"Total applied: {results['total_applied']}")
        print(f"Errors: {len(results['failed'])}")
        return results

    def get_next_application_date(self):
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
