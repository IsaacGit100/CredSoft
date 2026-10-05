# services/transaction_posting_service.py

"""
Central posting engine.

Every posting flow in CredSoft goes through this one file:

    process_transaction(trans, user)
         TransactionPostingService(trans, user).process()
                creates the journal entry (via JournalEngine / django_ledger)
                marks the Trans as POSTED
                invokes any registered handlers

Handlers come from two registries:

    _POSTING_HANDLERS  — keyed by sub_module OR purpose (specific handlers)
    _MODULE_HANDLERS   — keyed by module (broad, fallback handlers)

Both fire inside the same atomic block. If ANY step raises — including a
handler — the whole posting rolls back: journal, Trans, Master, Loan,
Guarantor, and every other downstream model stay in sync.
"""

import logging
import traceback

from django.db import transaction as db_transaction
from django.utils import timezone

from services.journal_engine import JournalEngine

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Registries
# ----------------------------------------------------------------------
# Each key maps to a *list* of handlers so future code can attach more
# than one handler to the same purpose without stepping on each other.
#
# Example:
#   _POSTING_HANDLERS = {
#       "loan_repayment":  [handle_loan_repayment],
#       "savings_deposit": [handle_savings_deposit],
#   }
#   _MODULE_HANDLERS = {
#       "church": [handle_church_giving],
#   }
#
_POSTING_HANDLERS = {}
_MODULE_HANDLERS = {}


def register_posting_handler(purpose, handler):
    """
    Register a handler for a specific sub_module or purpose.
    Idempotent — registering the same handler twice is a no-op.

    Usage:
        register_posting_handler("loan_repayment", handle_loan_repayment)
    """
    key = (purpose or "").strip().lower()
    if not key:
        raise ValueError("register_posting_handler: purpose cannot be empty")
    if not callable(handler):
        raise ValueError("register_posting_handler: handler must be callable")
    bucket = _POSTING_HANDLERS.setdefault(key, [])
    if handler not in bucket:
        bucket.append(handler)


def register_module_handler(module, handler):
    """
    Register a handler that fires for EVERY posted Trans on a module,
    regardless of sub_module/purpose. Useful for catch-all rules such as
    "any church receipt with a member produces a contribution record".

    Usage:
        register_module_handler("church", handle_church_giving)
    """
    key = (module or "").strip().lower()
    if not key:
        raise ValueError("register_module_handler: module cannot be empty")
    if not callable(handler):
        raise ValueError("register_module_handler: handler must be callable")
    bucket = _MODULE_HANDLERS.setdefault(key, [])
    if handler not in bucket:
        bucket.append(handler)


# ----------------------------------------------------------------------
# The service
# ----------------------------------------------------------------------
class TransactionPostingService:
    """
    Post one Trans to the journal, then run its handlers — all atomically.

    Handles all three trans_types:
      - Receipts : Dr Cash          Cr ledger_code
      - Payments : Dr ledger_code   Cr Cash
      - Journal  : Dr debit_code    Cr credit_code
    """

    CASH_ACCOUNT_BY_MODE = {
        "Cash": "1010",
        "Cheque": "1020",
        "Transfer": "1020",
        "Momo": "1020",
        "None": None,  # only for Journal type
    }

    def __init__(self, trans, user):
        self.trans = trans
        self.user = user
        self.entity = trans.entity
        self.results = {
            "success": False,
            "errors": [],
            "journal_entry": None,
            "journal_lines": [],
        }

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def process(self):
        """
        Post the Trans to the journal, then run its handlers.
        Idempotent — a Trans that is already POSTED returns success
        without doing anything.
        """
        # ---- guards ----
        if self.trans.journal_status == "POSTED":
            self.results.update(success=True, message="Already posted.")
            return self.results

        if self.trans.journal_status == "REJECTED":
            self.results["errors"].append("Rejected transactions cannot be posted.")
            return self.results

        if not self.entity:
            self.results["errors"].append("Transaction has no entity.")
            return self.results

        try:
            with db_transaction.atomic():
                engine = JournalEngine(self.entity.slug)

                description = self._build_description()
                journal = self._post_by_type(engine, description)

                self.results["journal_entry"] = journal
                self.results["journal_lines"] = list(journal.transactionmodel_set.all())

                # ---- mark the Trans as POSTED ----
                self.trans.journal_status = "POSTED"
                self.trans.status = "POSTED"
                self.trans.posted_at = timezone.now()
                self.trans.journal_entry_id = str(journal.uuid)
                self.trans.save(
                    update_fields=[
                        "journal_status",
                        "status",
                        "posted_at",
                        "journal_entry_id",
                    ]
                )

                # ---- run handlers (inside the same atomic block) ----
                # If any handler raises, the exception propagates out of
                # the atomic block, rolling back the journal, the Trans,
                # and anything the handler itself wrote.
                for handler in self._resolve_handlers():
                    handler(self.trans)

                self.results["success"] = True
                logger.info(
                    f"Trans {self.trans.rec_vou_no} posted to "
                    f"journal {journal.uuid}"
                )
                return self.results

        except Exception as e:
            logger.error(f"Posting failed for {self.trans.rec_vou_no}: {e}")
            logger.error(traceback.format_exc())
            self.results["errors"].append(str(e))
            return self.results

    # ------------------------------------------------------------------
    # Handler resolution
    # ------------------------------------------------------------------
    def _resolve_handlers(self):
        """
        Return the ordered, deduplicated list of handlers to run for this
        Trans.

        Order:
          1. Specific handlers matching sub_module (preferred)
          2. Specific handlers matching purpose (fallback)
          3. Module-level handlers (broad)
        """
        handlers = []
        seen = set()

        def _add(fn):
            if id(fn) not in seen:
                handlers.append(fn)
                seen.add(id(fn))

        # 1 & 2 — specific, by sub_module then purpose
        for raw_key in (self.trans.sub_module, self.trans.purpose):
            key = (raw_key or "").strip().lower()
            if not key:
                continue
            for fn in _POSTING_HANDLERS.get(key, []):
                _add(fn)

        # 3 — module-level fallback
        module_key = (self.trans.module or "").strip().lower()
        if module_key:
            for fn in _MODULE_HANDLERS.get(module_key, []):
                _add(fn)

        return handlers

    # ------------------------------------------------------------------
    # Journal construction
    # ------------------------------------------------------------------
    def _build_description(self):
        t = self.trans
        who = t.member_name or t.non_member_name or ""
        parts = [t.trans_type, t.purpose or "", t.details or "", who]
        body = " – ".join(p for p in parts if p)
        return f"{body} | {t.rec_vou_no}" if body else str(t.rec_vou_no)

    def _cash_code(self):
        code = self.CASH_ACCOUNT_BY_MODE.get(self.trans.pay_mode)
        if not code:
            raise ValueError(
                f"Cannot determine cash account for pay_mode "
                f"'{self.trans.pay_mode}'."
            )
        return code

    def _post_by_type(self, engine, description):
        t = self.trans

        if t.trans_type == "Receipts":
            return engine.record_receipt(
                amount=t.amount,
                cash_account_code=self._cash_code(),
                credit_account_code=t.ledger_code,
                description=description,
                date=t.date,
            )

        if t.trans_type == "Payments":
            return engine.record_payment(
                amount=t.amount,
                debit_account_code=t.ledger_code,
                cash_account_code=self._cash_code(),
                description=description,
                date=t.date,
            )

        if t.trans_type == "Journal":
            return engine.record_transaction(
                amount=t.amount,
                debit_account_code=t.debit_account_code,
                credit_account_code=t.credit_account_code,
                description=description,
                date=t.date,
            )

        raise ValueError(f"Unknown trans_type '{t.trans_type}'.")


# ----------------------------------------------------------------------
# Convenience wrapper (used by supervisor views)
# ----------------------------------------------------------------------
def process_transaction(trans, user):
    """Post a Trans via the standard engine. Returns a results dict."""
    return TransactionPostingService(trans, user).process()
