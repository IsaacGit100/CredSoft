"""
CreditUnion post-posting handlers.

Registered with services.transaction_posting_service.
Each handler runs inside the same atomic block as the journal — if it
raises, the journal rolls back too, keeping Master/Loan/Guarantor in sync.
"""

from decimal import Decimal

from services.transaction_posting_service import register_posting_handler
from MembersApp.models import Master
from LoanApp.models import Loan, Guarantor


def _recompute_balance(m):
    m.balance = (
        (m.tot_deposits or Decimal("0"))
        - (m.tot_deposit_withdrawal or Decimal("0"))
        + (m.tot_sav_int or Decimal("0"))
    )


# ----------------------------------------------------------------------
# LOAN REPAYMENT
# ----------------------------------------------------------------------
def handle_loan_repayment(trans):

    if not trans.loan_id:
        return

    loan = Loan.objects.select_for_update().get(pk=trans.loan_id)
    old_balance = loan.loan_balance or Decimal("0")
    amount = trans.amount or Decimal("0")

    interest_due = loan.due_interest or Decimal("0")
    interest_paid = min(amount, interest_due)
    principal_paid = max(amount - interest_paid, Decimal("0"))

    new_balance = max(old_balance - principal_paid, Decimal("0"))
    loan.loan_balance = new_balance
    if new_balance <= 0 and old_balance > 0:
        loan.status = "CLOSED"
    loan.save(update_fields=["loan_balance", "status"])

    if principal_paid > 0:
        _release_guarantors(loan, principal_paid)

    if trans.member_id:
        m = Master.objects.select_for_update().get(pk=trans.member_id)
        m.loan_last_repayment = amount
        m.loan_last_repayment_date = trans.date
        m.loan_tot_repayment = (m.loan_tot_repayment or Decimal("0")) + amount
        m.loan_repayment_cnt = (m.loan_repayment_cnt or 0) + 1
        if new_balance <= 0 and old_balance > 0:
            m.active_loan_count = max((m.active_loan_count or 1) - 1, 0)

        m.save(
            update_fields=[
                "loan_last_repayment",
                "loan_last_repayment_date",
                "loan_tot_repayment",
                "loan_repayment_cnt",
                "active_loan_count",
            ]
        )

        m.refresh_from_db()
        print(f"[HANDLER] DB   : loan_tot_repayment={m.loan_tot_repayment!r}")


def _release_guarantors(loan, principal_paid):
    remaining = principal_paid
    for g in (
        Guarantor.objects.filter(loan=loan, status__in=["ACTIVE", "PARTIAL"])
        .select_for_update()
        .order_by("date", "id")
    ):
        if remaining <= 0:
            break
        holding = g.holding
        if holding <= 0:
            continue
        to_release = min(remaining, holding)
        g.release(to_release)
        remaining -= to_release


# ----------------------------------------------------------------------
# LOAN DISBURSEMENT
# ----------------------------------------------------------------------
def handle_loan_disbursement(trans):
    if not trans.loan_id:
        return

    loan = Loan.objects.select_for_update().get(pk=trans.loan_id)
    principal = loan.principal or Decimal("0")

    loan.loan_balance = principal
    loan.status = "ACTIVE"
    loan.save(update_fields=["loan_balance", "status"])

    if trans.member_id:
        m = Master.objects.select_for_update().get(pk=trans.member_id)
        m.loan_last_disb_date = trans.date
        m.loan_last_disb_princ = principal
        m.loan_disb_tot_princ = (m.loan_disb_tot_princ or Decimal("0")) + principal
        m.loan_disb_cnt = (m.loan_disb_cnt or 0) + 1
        m.active_loan_count = (m.active_loan_count or 0) + 1
        m.save(
            update_fields=[
                "loan_last_disb_date",
                "loan_last_disb_princ",
                "loan_disb_tot_princ",
                "loan_disb_cnt",
                "active_loan_count",
            ]
        )


# ----------------------------------------------------------------------
# SAVINGS
# ----------------------------------------------------------------------
def handle_savings_deposit(trans):
    if not trans.member_id:
        return
    m = Master.objects.select_for_update().get(pk=trans.member_id)
    m.tot_deposits = (m.tot_deposits or Decimal("0")) + trans.amount
    _recompute_balance(m)
    m.save(update_fields=["tot_deposits", "balance"])


def handle_savings_withdrawal(trans):
    if not trans.member_id:
        return
    m = Master.objects.select_for_update().get(pk=trans.member_id)
    m.tot_deposit_withdrawal = (m.tot_deposit_withdrawal or Decimal("0")) + trans.amount
    _recompute_balance(m)
    m.save(update_fields=["tot_deposit_withdrawal", "balance"])


def handle_savings_interest(trans):
    if not trans.member_id:
        return
    m = Master.objects.select_for_update().get(pk=trans.member_id)
    m.tot_sav_int = (m.tot_sav_int or Decimal("0")) + trans.amount
    m.tot_mnth_sav_int_accrued = Decimal("0.00")
    m.mnth_int_accrued_days = 0
    _recompute_balance(m)
    m.save(
        update_fields=[
            "tot_sav_int",
            "tot_mnth_sav_int_accrued",
            "mnth_int_accrued_days",
            "balance",
        ]
    )


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------
register_posting_handler("loan_repayment", handle_loan_repayment)
register_posting_handler("loan_disbursement", handle_loan_disbursement)
register_posting_handler("savings_deposit", handle_savings_deposit)
register_posting_handler("savings_withdrawal", handle_savings_withdrawal)
register_posting_handler("Interest Application", handle_savings_interest)
