# journal_engine.py
import logging
from decimal import Decimal
from datetime import datetime, time
from django_ledger.models import (
    EntityModel,
    LedgerModel,
    JournalEntryModel,
    AccountModel,
    TransactionModel,
)
from django.utils import timezone

logger = logging.getLogger(__name__)


class JournalEngine:
    def __init__(self, entity_slug):
        self.entity = EntityModel.objects.get(slug=entity_slug)
        self.ledger = self._get_or_create_ledger()
        self.coa = self.entity.get_default_coa()

    def _get_or_create_ledger(self):
        ledger = LedgerModel.objects.filter(entity=self.entity).first()
        if not ledger:
            ledger = LedgerModel.objects.create(
                entity=self.entity, name="Default Ledger"
            )
        return ledger

    def _get_account(self, code):
        try:
            return AccountModel.objects.get(coa_model=self.coa, code=code)
        except AccountModel.DoesNotExist:
            logger.error(f"Account code '{code}' not found.")
            raise ValueError(
                f"Account code '{code}' does not exist in the Chart of Accounts."
            )

    def _create_journal_entry(self, description, date=None):
        """
        Create a JournalEntryModel with a datetime timestamp.
        If date is a date object, convert to datetime at midnight in the current timezone.
        """
        if date is None:
            dt = timezone.now()
        elif isinstance(date, datetime):
            dt = date
        else:  # assume it's a date object
            # Combine with midnight and make timezone-aware
            dt = datetime.combine(date, time.min)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
        je = JournalEntryModel.objects.create(
            ledger=self.ledger,
            timestamp=dt,
            description=description,
            posted=False,
        )
        return je

    def _post(self, je):
        je.posted = True
        je.save()
        return je

    def record_transaction(
        self,
        amount,
        debit_account_code,
        credit_account_code,
        description="Transaction",
        date=None,
    ):
        je = self._create_journal_entry(description, date)
        debit_account = self._get_account(debit_account_code)
        credit_account = self._get_account(credit_account_code)

        TransactionModel.objects.create(
            journal_entry=je,
            account=debit_account,
            amount=amount,
            tx_type="debit",
        )
        TransactionModel.objects.create(
            journal_entry=je,
            account=credit_account,
            amount=amount,
            tx_type="credit",
        )
        return self._post(je)

    # Other specific methods (record_sale, record_expense, etc.)
    # can also use record_transaction or call _create_journal_entry directly.
    def record_sale(
        self,
        amount,
        cash_account_code="1010",
        revenue_account_code="4010",
        description="Sale",
        date=None,
    ):
        return self.record_transaction(
            amount, cash_account_code, revenue_account_code, description, date
        )

    def record_expense(
        self,
        amount,
        expense_account_code,
        cash_account_code="1010",
        description="Expense",
        date=None,
    ):
        return self.record_transaction(
            amount, expense_account_code, cash_account_code, description, date
        )

    def record_loan_disbursement(
        self,
        amount,
        loan_portfolio_account_code="1080",
        cash_account_code="1010",
        description="Loan Disbursement",
        date=None,
    ):
        return self.record_transaction(
            amount, loan_portfolio_account_code, cash_account_code, description, date
        )

    def record_loan_repayment(
        self,
        amount,
        principal_account_code="1080",
        cash_account_code="1010",
        interest_income_code="4010",
        interest_amount=0,
        description="Loan Repayment",
        date=None,
    ):
        je = self._create_journal_entry(description, date)
        cash = self._get_account(cash_account_code)
        loan_asset = self._get_account(principal_account_code)
        interest_income = self._get_account(interest_income_code)

        TransactionModel.objects.create(
            journal_entry=je, account=cash, amount=amount, tx_type="debit"
        )
        principal = amount - interest_amount
        if principal > 0:
            TransactionModel.objects.create(
                journal_entry=je, account=loan_asset, amount=principal, tx_type="credit"
            )
        if interest_amount > 0:
            TransactionModel.objects.create(
                journal_entry=je,
                account=interest_income,
                amount=interest_amount,
                tx_type="credit",
            )
        return self._post(je)
