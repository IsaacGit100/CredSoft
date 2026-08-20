# services/transaction_posting_service.py
import logging
from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from services.journal_engine import JournalEngine  # adjust import path
from RecPayApp.models import Trans
from MembersApp.models import Master
from LoanApp.models import Loan, LoanTransaction, LoanRepayment, Guarantor

logger = logging.getLogger(__name__)


class TransactionPostingService:
    def __init__(self, transaction, user, entity_slug):
        self.transaction = transaction
        self.user = user
        self.entity_slug = entity_slug
        self.results = {
            "success": False,
            "errors": [],
            "journal_entry": None,
            "journal_lines": [],
            "member_update": None,
            "state_trans": None,
            "state_update": None,
        }

    def process(self):
        if self.transaction.status == "POSTED":
            self.results["success"] = True
            self.results["message"] = "Transaction already posted."
            return self.results

        try:
            logger.info(f"POSTING TRANSACTION: {self.transaction.rec_vou_no}")

            with db_transaction.atomic():
                # 1. Initialize the JournalEngine
                engine = JournalEngine(self.entity_slug)

                # 2. Determine account codes
                gl_account_code = self.transaction.ledger_code
                cash_account_code = self._get_cash_account_code()

                if not gl_account_code:
                    error_msg = (
                        f"Transaction {self.transaction.id} has no ledger_code set."
                    )
                    logger.error(error_msg)
                    self.results["errors"].append(error_msg)
                    return self.results

                logger.info(
                    f"Using GL account code: {gl_account_code}, Cash account code: {cash_account_code}"
                )

                # 3. Create and post the journal entry using the engine
                description = (
                    f"{self.transaction.trans_type}: {self.transaction.details or self.transaction.ledger_name} "
                    f"| Voucher: {self.transaction.rec_vou_no}"
                )

                if self.transaction.trans_type == "Receipts":
                    journal = engine.record_transaction(
                        amount=self.transaction.amount,
                        debit_account_code=cash_account_code,
                        credit_account_code=gl_account_code,
                        description=description,
                        date=self.transaction.date,
                    )
                else:  # Payments
                    journal = engine.record_transaction(
                        amount=self.transaction.amount,
                        debit_account_code=gl_account_code,
                        credit_account_code=cash_account_code,
                        description=description,
                        date=self.transaction.date,
                    )

                self.results["journal_entry"] = journal
                self.results["journal_lines"] = list(journal.transactionmodel_set.all())
                logger.info(f"Journal posted: {journal.uuid}")

                # 4. Update Member Balance (business logic)
                member_update = self._update_member_balance()
                self.results["member_update"] = member_update
                logger.info("Updated member balance")

                # 5. Update Loan Table (business logic)
                self._update_loan_table()
                logger.info("Updated loan table")

                # 6. Create State Trans (audit)
                state_trans = self._create_state_trans()
                self.results["state_trans"] = state_trans
                logger.info("Created state transaction record")

                # 7. Create State Update (audit)
                state_update = self._create_state_update(member_update)
                self.results["state_update"] = state_update
                logger.info("Created state update record")

                # 8. Archive journal to state tables (fixed: use .pk)
                self._archive_journal(journal)
                logger.info("Archived journal to state tables")

                # 9. Update Transaction Status
                self.transaction.status = "POSTED"
                self.transaction.posted_at = timezone.now()
                self.transaction.save()
                logger.info("Transaction marked as POSTED")

                self.results["success"] = True
                logger.info(
                    f"SUCCESS: Transaction {self.transaction.rec_vou_no} posted!"
                )
                return self.results

        except Exception as e:
            logger.error(f"ERROR: {str(e)}")
            import traceback

            traceback.print_exc()
            self.results["errors"].append(str(e))
            return self.results

    # ----------------------------------------------------------------------
    # Private helper methods
    # ----------------------------------------------------------------------

    def _get_cash_account_code(self):
        account_map = {
            "Cash": "1010",
            "Cheque": "1020",
            "Transfer": "1020",
        }
        return account_map.get(self.transaction.pay_mode, "1010")

    def _update_member_balance(self):
        if not self.transaction.member:
            return None

        member = Master.objects.select_for_update().get(id=self.transaction.member.id)
        ledger_name = (
            self.transaction.ledger_name.lower() if self.transaction.ledger_name else ""
        )

        old_values = {
            "tot_deposits": member.tot_deposits or 0,
            "tot_deposit_withdrawal": member.tot_deposit_withdrawal or 0,
            "tot_shares": member.tot_shares or 0,
            "tot_shares_withdrawal": member.tot_shares_withdrawal or 0,
            "tot_dividend": member.tot_dividend or 0,
            "tot_dividend_withdrawal": member.tot_dividend_withdrawal or 0,
            "enrollment_fees": member.enrollment_fees or 0,
            "tot_interest_accrued": member.tot_interest_accrued or 0,
            "sav_avail_bal": getattr(member, "sav_avail_bal", 0),
        }

        if "savings deposit" in ledger_name:
            member.tot_deposits = (member.tot_deposits or 0) + self.transaction.amount
        elif "savings withdrawal" in ledger_name:
            member.tot_deposit_withdrawal = (
                member.tot_deposit_withdrawal or 0
            ) + self.transaction.amount
        elif "shares" in ledger_name and "withdrawal" not in ledger_name:
            member.tot_shares = (member.tot_shares or 0) + self.transaction.amount
        elif "shares withdrawal" in ledger_name:
            member.tot_shares_withdrawal = (
                member.tot_shares_withdrawal or 0
            ) + self.transaction.amount
        elif "dividend" in ledger_name and "withdrawal" not in ledger_name:
            member.tot_dividend = (member.tot_dividend or 0) + self.transaction.amount
        elif "dividend withdrawal" in ledger_name:
            member.tot_dividend_withdrawal = (
                member.tot_dividend_withdrawal or 0
            ) + self.transaction.amount
        elif "enrollment fees" in ledger_name:
            member.enrollment_fees = (
                member.enrollment_fees or 0
            ) + self.transaction.amount
        elif "loan_disbursements" in ledger_name:
            member.loan_last_disb_princ = self.transaction.amount
            member.loan_last_disb_date = self.transaction.date
            member.loan_disb_tot = (member.loan_disb_tot or 0) + self.transaction.amount
            member.loan_disb_cnt = (member.loan_disb_cnt or 0) + 1
            member.loan_last_id = self.transaction.loan_id
        elif "loan_repayments" in ledger_name:
            member.loan_last_repayment_amt = self.transaction.amount
            member.loan_last_repayment_date = self.transaction.date
            member.loan_tot_repayment = (
                member.loan_tot_repayment or 0
            ) + self.transaction.amount
            member.loan_repayment_cnt = (member.loan_repayment_cnt or 0) + 1
            member.loan_last_repayment_id = self.transaction.loan_id

        member.balance = member.tot_deposits - member.tot_deposit_withdrawal
        member.save()

        new_values = {
            "tot_deposits": member.tot_deposits or 0,
            "tot_deposit_withdrawal": member.tot_deposit_withdrawal or 0,
            "tot_shares": member.tot_shares or 0,
            "tot_shares_withdrawal": member.tot_shares_withdrawal or 0,
            "tot_dividend": member.tot_dividend or 0,
            "tot_dividend_withdrawal": member.tot_dividend_withdrawal or 0,
            "enrollment_fees": member.enrollment_fees or 0,
            "tot_interest_accrued": member.tot_interest_accrued or 0,
            "sav_avail_bal": getattr(member, "sav_avail_bal", 0),
            "balance": member.balance or 0,
        }

        return {
            "member_id": member.id,
            "member_name": member.full_name,
            "old_values": old_values,
            "new_values": new_values,
            "amount": self.transaction.amount,
            "ledger_name": self.transaction.ledger_name,
        }

    def _create_state_trans(self):
        from services.models import StateTrans

        state_trans = StateTrans.objects.create(
            state_date=timezone.now(),
            rec_vou_no=self.transaction.rec_vou_no,
            trans_no=self.transaction.trans_no,
            date=self.transaction.date,
            trans_type=self.transaction.trans_type,
            amount=self.transaction.amount,
            pay_mode=self.transaction.pay_mode,
            loan=self.transaction.loan,
            master=self.transaction.member,
            non_member_name=self.transaction.non_member_name or "",
            non_member_contact=self.transaction.non_member_contact or "",
            bank_date=self.transaction.bank_date,
            bank=self.transaction.bank or "",
            bank_no=self.transaction.bank_no or "",
            bank_branch=self.transaction.bank_branch or "",
            cheque_date=self.transaction.cheque_date,
            cheque_no=self.transaction.cheque_no or "",
            momo_no=self.transaction.momo_no or "",
            momo_name=self.transaction.momo_name or "",
            ledger_id=self.transaction.ledger_id or "",
            ledger_code=self.transaction.ledger_code or "",
            ledger_name=self.transaction.ledger_name or "",
            purpose=self.transaction.purpose or "",
            details=self.transaction.details or "",
            posted_at=self.transaction.posted_at,
            created_at=self.transaction.created_at,
            created_by=self.transaction.created_by,
            updated_at=self.transaction.updated_at,
            updated_by=self.transaction.updated_by,
            created_by_who_id=self.transaction.created_by_id,
            created_by_name=self.transaction.created_by_name,
            created_by_username=self.transaction.created_by_username,
        )
        return state_trans
    
    def _create_state_update(self, member_update):
        from services.models import StateUpdate
        from django.db import IntegrityError
        import logging
        logger = logging.getLogger(__name__)

        if not member_update:
            return None

        old = member_update["old_values"]
        new = member_update["new_values"]

        # Build the data dictionary
        data = {
            'state_update_date': timezone.now(),
            'trans_amount': self.transaction.amount,
            'ledger_id': self.transaction.ledger_id or "",
            'ledger_code': self.transaction.ledger_code or "",
            'ledger_name': self.transaction.ledger_name or "",
            'old_shares': old.get("tot_shares", 0),
            'new_shares': new.get("tot_shares", 0),
            'old_shares_withdrawal': old.get("tot_shares_withdrawal", 0),
            'new_shares_withdrawal': new.get("tot_shares_withdrawal", 0),
            'old_deposit': old.get("tot_deposits", 0),
            'new_deposit': new.get("tot_deposits", 0),
            'old_deposit_withdrawal': old.get("tot_deposit_withdrawal", 0),
            'new_deposit_withdrawal': new.get("tot_deposit_withdrawal", 0),
            'old_dividend': old.get("tot_dividend", 0),
            'new_dividend': new.get("tot_dividend", 0),
            'old_dividend_withdrawal': old.get("tot_dividend_withdrawal", 0),
            'new_dividend_withdrawal': new.get("tot_dividend_withdrawal", 0),
            'old_enrollment_fees': old.get("enrollment_fees", 0),
            'new_enrollment_fees': new.get("enrollment_fees", 0),
            'old_int_accrued': old.get("tot_interest_accrued", 0),
            'new_int_accrued': new.get("tot_interest_accrued", 0),
            'old_available_balance': old.get("sav_avail_bal", 0),
            'new_available_balance': new.get("sav_avail_bal", 0),
            'created_at': timezone.now(),
            'created_by': self.user,
            'updated_at': timezone.now(),
            'updated_by': self.user,
        }

        # If the model has an 'activity' field (which has a unique constraint), set it
        if hasattr(StateUpdate, 'activity'):
            data['activity'] = f"Update_{self.transaction.rec_vou_no}_{self.transaction.pk}"

        try:
            state_update = StateUpdate.objects.create(**data)
            logger.info(f"StateUpdate created for voucher {self.transaction.rec_vou_no}")
            return state_update
        except IntegrityError as e:
            # If duplicate, we log and return None (or you could update existing)
            logger.warning(f"StateUpdate duplicate or integrity error: {e}")
            # Attempt to find existing by activity and update? For now, we'll skip.
            return None
        
        
    

    def _create_state_update1(self, member_update):
        from services.models import StateUpdate

        if not member_update:
            return None
        old = member_update["old_values"]
        new = member_update["new_values"]
        state_update = StateUpdate.objects.create(
            state_update_date=timezone.now(),
            trans_amount=self.transaction.amount,
            ledger_id=self.transaction.ledger_id or "",
            ledger_code=self.transaction.ledger_code or "",
            ledger_name=self.transaction.ledger_name or "",
            old_shares=old.get("tot_shares", 0),
            new_shares=new.get("tot_shares", 0),
            old_shares_withdrawal=old.get("tot_shares_withdrawal", 0),
            new_shares_withdrawal=new.get("tot_shares_withdrawal", 0),
            old_deposit=old.get("tot_deposits", 0),
            new_deposit=new.get("tot_deposits", 0),
            old_deposit_withdrawal=old.get("tot_deposit_withdrawal", 0),
            new_deposit_withdrawal=new.get("tot_deposit_withdrawal", 0),
            old_dividend=old.get("tot_dividend", 0),
            new_dividend=new.get("tot_dividend", 0),
            old_dividend_withdrawal=old.get("tot_dividend_withdrawal", 0),
            new_dividend_withdrawal=new.get("tot_dividend_withdrawal", 0),
            old_enrollment_fees=old.get("enrollment_fees", 0),
            new_enrollment_fees=new.get("enrollment_fees", 0),
            old_int_accrued=old.get("tot_interest_accrued", 0),
            new_int_accrued=new.get("tot_interest_accrued", 0),
            old_available_balance=old.get("sav_avail_bal", 0),
            new_available_balance=new.get("sav_avail_bal", 0),
            created_at=timezone.now(),
            created_by=self.user,
            updated_at=timezone.now(),
            updated_by=self.user,
        )
        return state_update

    # FIXED: use .pk instead of .id
    
    def _archive_journal(self, journal):
        from services.models import StateJournalEntry, StateJournalLine
        import logging
        logger = logging.getLogger(__name__)

        # Log all values we're about to insert
        journal_pk = journal.pk
        trans_pk = self.transaction.pk
        user_pk = self.user.pk if self.user else None

        logger.info(f"journal.pk: {journal_pk} (type: {type(journal_pk)})")
        logger.info(f"transaction.pk: {trans_pk} (type: {type(trans_pk)})")
        logger.info(f"user.pk: {user_pk} (type: {type(user_pk)})")

        # First attempt: full entry
        try:
            StateJournalEntry.objects.create(
                original_id=journal_pk,
                entry_number=self.transaction.rec_vou_no,
                entry_date=journal.timestamp,
                description=journal.description,
                source_trans_id=trans_pk,
                status="POSTED",
                posted=True,
                posted_at=timezone.now(),
                posted_by_id=user_pk,
            )
            logger.info("StateJournalEntry created with all fields")
        except Exception as e:
            logger.error(f"Failed to create full StateJournalEntry: {e}")
            # Second attempt: without original_id, source_trans_id, posted_by_id
            try:
                StateJournalEntry.objects.create(
                    entry_number=self.transaction.rec_vou_no,
                    entry_date=journal.timestamp,
                    description=journal.description,
                    status="POSTED",
                    posted=True,
                    posted_at=timezone.now(),
                    # set these to None if your model allows, else drop them
                    # original_id=None,
                    # source_trans_id=None,
                    # posted_by_id=None,
                )
                logger.info("StateJournalEntry created without the integer fields (fallback)")
            except Exception as e2:
                logger.error(f"Fallback also failed: {e2}")
                # If that fails, we skip archiving and just log
                logger.warning("Skipping StateJournalEntry creation due to persistent errors")
                # But we still continue to process lines?

        # Now create StateJournalLine entries
        for tx in journal.transactionmodel_set.all():
            try:
                StateJournalLine.objects.create(
                    original_id=tx.pk,
                    journal_entry_number=self.transaction.rec_vou_no,
                    account_code=tx.account.code,
                    member_id=self.transaction.member.pk if self.transaction.member else None,
                    debit=tx.amount if tx.tx_type == "debit" else 0,
                    credit=tx.amount if tx.tx_type == "credit" else 0,
                    line_description=journal.description,
                )
                logger.info(f"StateJournalLine created for tx {tx.pk}")
            except Exception as e:
                logger.error(f"Failed to create StateJournalLine for tx {tx.pk}: {e}")
                # Fallback: without original_id and member_id
                try:
                    StateJournalLine.objects.create(
                        journal_entry_number=self.transaction.rec_vou_no,
                        account_code=tx.account.code,
                        debit=tx.amount if tx.tx_type == "debit" else 0,
                        credit=tx.amount if tx.tx_type == "credit" else 0,
                        line_description=journal.description,
                    )
                    logger.info("StateJournalLine created without original_id/member_id")
                except Exception as e2:
                    logger.error(f"Line fallback also failed: {e2}")
                    logger.warning("Skipping this StateJournalLine")
    
    def _archive_journal1(self, journal):
        from services.models import StateJournalEntry, StateJournalLine

        StateJournalEntry.objects.create(
            original_id=journal.pk,  # <--- changed from journal.id
            entry_number=self.transaction.rec_vou_no,
            entry_date=journal.timestamp,
            description=journal.description,
            source_trans_id=self.transaction.pk,
            status="POSTED",
            posted=True,
            posted_at=timezone.now(),
            posted_by_id=self.user.pk if self.user else None,
        )
        for tx in journal.transactionmodel_set.all():
            StateJournalLine.objects.create(
                original_id=tx.pk,  # <--- changed from tx.id
                journal_entry_number=self.transaction.rec_vou_no,
                account_code=tx.account.code,
                member_id=(
                    self.transaction.member.pk if self.transaction.member else None
                ),
                debit=tx.amount if tx.tx_type == "debit" else 0,
                credit=tx.amount if tx.tx_type == "credit" else 0,
                line_description=journal.description,
            )

    def _update_loan_table(self):
        loan = self.transaction.loan
        if not loan:
            return

        loan = Loan.objects.select_for_update().get(id=loan.id)
        ledger_name = (
            self.transaction.ledger_name.lower() if self.transaction.ledger_name else ""
        )

        if "loan disbursements" in ledger_name and loan.status == "New Loan":
            loan.rec_vou_no = self.transaction.rec_vou_no
            loan.disbursement_date = self.transaction.date
            loan.status = "Active"
            loan.loan_trans_amount = self.transaction.amount
            from dateutil.relativedelta import relativedelta

            loan.next_repayment_date = self.transaction.date + relativedelta(months=1)
            loan.save()
            logger.info(f"Updated Loan {loan.id}: disbursed")
            return

        if "loan repayments" in ledger_name:
            old_balance = loan.loan_balance
            amount = self.transaction.amount
            interest_due = loan.due_interest
            interest_paid = min(amount, interest_due)
            principal_paid = amount - interest_paid

            loan.tot_int = (loan.tot_int or 0) + interest_paid
            loan.last_interest_paid = interest_paid

            if principal_paid > 0:
                if principal_paid >= loan.loan_balance:
                    loan.loan_credit_balance = principal_paid - loan.loan_balance
                    loan.loan_balance = 0
                    loan.status = "Credit"
                else:
                    loan.loan_balance -= principal_paid
                loan.last_repayment_paid = principal_paid
                loan.tot_ded = (loan.tot_ded or 0) + principal_paid
            else:
                loan.last_repayment_paid = 0

            loan.last_repayment_date = self.transaction.date
            loan.last_repayment_amount = amount
            loan.last_payment_date = self.transaction.date

            if loan.loan_balance <= 0 and loan.status not in ("Credit", "Completed"):
                loan.status = "Completed"
                loan.completion_date = self.transaction.date

            loan.save()

            redeemed_details = []
            if principal_paid > 0:
                redeemed_details = self._update_guarantors(principal_paid, loan)

            self._update_loan_repayment_table(loan, old_balance, redeemed_details)
            logger.info(
                f"Loan repayment: interest {interest_paid}, principal {principal_paid}"
            )

    def _update_guarantors(self, principal_paid, loan):
        from LoanApp.models import Guarantor

        guarantors = (
            Guarantor.objects.select_for_update()
            .filter(loan=loan, redeemed_status__in=["", "Partial"])
            .order_by("id")
        )
        remaining = principal_paid
        redeemed_details = []
        for guarantor in guarantors:
            if remaining <= 0:
                break
            guaranteed = guarantor.guaranteed_amount
            redeemed = guarantor.redeemed_amount or 0
            still_owing = guaranteed - redeemed
            if still_owing <= 0:
                continue
            to_redeem = min(remaining, still_owing)
            guarantor.redeemed_amount = redeemed + to_redeem
            remaining -= to_redeem
            if guarantor.redeemed_amount >= guaranteed:
                guarantor.redeemed_status = "Redeemed"
            else:
                guarantor.redeemed_status = "Partial"
            guarantor.save()
            redeemed_details.append(
                {
                    "guarantor_id": guarantor.id,
                    "master_id": guarantor.master.id,
                    "loan_id": loan.id,
                    "master_name": guarantor.master.full_name,
                    "guaranteed_amount": float(guaranteed),
                    "redeemed_amount": float(guarantor.redeemed_amount),
                    "redeemed_in_this_transaction": float(to_redeem),
                }
            )
        return redeemed_details

    def _update_loan_repayment_table(self, loan, old_balance, guarantor_details):
        from LoanApp.models import LoanRepayment
        import json

        LoanRepayment.objects.create(
            loan=loan,
            master=loan.master,
            trans=self.transaction,
            trans_amount=self.transaction.amount,
            trans_date=self.transaction.date,
            old_loan_balance=old_balance,
            new_loan_balance=loan.loan_balance,
            gua_redeemed_details=(
                json.dumps(guarantor_details) if guarantor_details else None
            ),
            interest_paid=loan.last_interest_paid,
            repayment_paid=loan.last_repayment_paid,
            payment_date=self.transaction.date,
            notes=f"Loan repayment for {self.transaction.date}",
            created_by=self.user,
        )


# ----------------------------------------------------------------------
# Helper function
# ----------------------------------------------------------------------
def process_transaction(transaction, user, entity_slug):
    processor = TransactionPostingService(transaction, user, entity_slug)
    return processor.process()
