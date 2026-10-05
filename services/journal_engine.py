# services/journal_engine.py

import logging
from datetime import datetime, time, date
from django.utils import timezone
from django_ledger.models import (
    EntityModel,
    LedgerModel,
    JournalEntryModel,
    AccountModel,
    TransactionModel,
)

logger = logging.getLogger(__name__)


class JournalEngine:
    """
    Thin wrapper around django_ledger for creating balanced journal entries.
    All accounting flows through this class – no direct django_ledger calls
    from views or services.
    """

    def __init__(self, entity_slug):
        self.entity = EntityModel.objects.get(slug=entity_slug)
        self.ledger = self._get_or_create_ledger()
        self.coa = self.entity.get_default_coa()
        if not self.coa:
            raise ValueError(
                f"Entity '{entity_slug}' has no default Chart of Accounts."
            )

    # 
    def _get_or_create_ledger(self):
        ledger, _ = LedgerModel.objects.get_or_create(
            entity=self.entity,
            defaults={"name": "Default Ledger"},
        )
        return ledger

    def _get_account(self, code):
        if not code:
            raise ValueError("Account code is empty.")
        try:
            return AccountModel.objects.get(coa_model=self.coa, code=code)
        except AccountModel.DoesNotExist:
            raise ValueError(
                f"Account code '{code}' not found in COA for entity {self.entity.slug}."
            )

    def _coerce_datetime(self, value):
        if value is None:
            return timezone.now()
        if isinstance(value, datetime):
            return value if timezone.is_aware(value) else timezone.make_aware(value)
        if isinstance(value, date):
            dt = datetime.combine(value, time.min)
            return timezone.make_aware(dt)
        raise TypeError(f"Invalid date value: {value!r}")

    def _create_je(self, description, dt):
        return JournalEntryModel.objects.create(
            ledger=self.ledger,
            timestamp=self._coerce_datetime(dt),
            description=description,
            posted=False,
        )

    def _post(self, je):
        je.posted = True
        je.save()
        return je

    #
    def record_transaction(
        self,
        amount,
        debit_account_code,
        credit_account_code,
        description="Transaction",
        date=None,
    ):
        """
        Create and post a simple two-line journal entry.
        Returns the posted JournalEntryModel.
        """
        amount = abs(amount)
        if amount <= 0:
            raise ValueError(f"Amount must be positive (got {amount}).")

        debit_acc = self._get_account(debit_account_code)
        credit_acc = self._get_account(credit_account_code)

        je = self._create_je(description, date)
        TransactionModel.objects.create(
            journal_entry=je, account=debit_acc, amount=amount, tx_type="debit"
        )
        TransactionModel.objects.create(
            journal_entry=je, account=credit_acc, amount=amount, tx_type="credit"
        )
        self._post(je)
        logger.info(
            f"Journal posted: {je.uuid} Dr {debit_acc.code} / Cr {credit_acc.code} ₵{amount}"
        )
        return je

    def record_receipt(
        self,
        amount,
        cash_account_code,
        credit_account_code,
        description="Receipt",
        date=None,
    ):
        return self.record_transaction(
            amount, cash_account_code, credit_account_code, description, date
        )

    def record_payment(
        self,
        amount,
        debit_account_code,
        cash_account_code,
        description="Payment",
        date=None,
    ):
        return self.record_transaction(
            amount, debit_account_code, cash_account_code, description, date
        )

    def record_loan_repayment(
        self,
        amount,
        cash_account_code="1010",
        principal_account_code="1080",
        interest_income_code="4010",
        interest_amount=0,
        description="Loan Repayment",
        date=None,
    ):
        """Handle split principal/interest repayment."""
        je = self._create_je(description, date)
        cash = self._get_account(cash_account_code)
        loan_asset = self._get_account(principal_account_code)
        interest_income = self._get_account(interest_income_code)

        amount = abs(amount)
        principal = amount - interest_amount
        TransactionModel.objects.create(
            journal_entry=je, account=cash, amount=amount, tx_type="debit"
        )
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
        self._post(je)
        return je
