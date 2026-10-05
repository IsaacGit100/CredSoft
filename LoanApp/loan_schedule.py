"""
Loan schedule calculations.

Single source of truth for the repayment schedule — used by:
  - the preview PDF (application form)
  - the saved-loan PDF (loan list)
  - the model save() when the loan is booked
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date

try:
    from dateutil.relativedelta import relativedelta
except ImportError:  # fallback if python-dateutil isn't installed
    from datetime import timedelta

    class _RD:
        def __init__(self, months=0, **kw):
            self.months = months

        def __radd__(self, other):
            y, m = other.year, other.month + self.months
            y += (m - 1) // 12
            m = (m - 1) % 12 + 1
            return date(y, m, other.day)

    def relativedelta(**kw):
        return _RD(**kw)


TWO = Decimal("0.01")


def _r(x):
    return Decimal(x).quantize(TWO, rounding=ROUND_HALF_UP)


def build_schedule(principal, monthly_rate_pct, term_months, start_date):
    """
    Reducing-balance (annuity) schedule.

    principal         : Decimal or number
    monthly_rate_pct  : e.g. Decimal('2.5') means 2.5% per month
    term_months       : int
    start_date        : date OR 'YYYY-MM-DD' string

    Returns (rows, totals):
      rows   = [{no, due_date, opening, principal, interest, installment, closing}, ...]
      totals = {total_payable, total_interest, total_principal, installment, count}
    """
    P = Decimal(str(principal))
    r = Decimal(str(monthly_rate_pct)) / Decimal("100")
    n = int(term_months)

    empty_totals = {
        "total_payable": Decimal("0.00"),
        "total_interest": Decimal("0.00"),
        "total_principal": Decimal("0.00"),
        "installment": Decimal("0.00"),
        "count": 0,
    }
    if n <= 0:
        return [], empty_totals

    # monthly installment (annuity formula)
    if r == 0:
        installment = _r(P / n)
    else:
        installment = _r(P * r / (Decimal(1) - (Decimal(1) + r) ** (-n)))

    # normalise start date
    if isinstance(start_date, str):
        y, m, d = map(int, start_date.split("-"))
        d0 = date(y, m, d)
    else:
        d0 = start_date

    rows, balance = [], P

    for i in range(1, n + 1):
        opening = balance
        interest = _r(opening * r)
        principal_part = _r(installment - interest)
        if i == n:  # last row absorbs rounding
            principal_part = opening
        closing = _r(opening - principal_part)
        due = d0 + relativedelta(months=i)

        rows.append(
            {
                "no": i,
                "due_date": due,
                "opening": opening,
                "principal": principal_part,
                "interest": interest,
                "installment": _r(principal_part + interest),
                "closing": max(closing, Decimal("0.00")),
            }
        )
        balance = closing

    totals = {
        "total_payable": sum((x["installment"] for x in rows), Decimal("0.00")),
        "total_interest": sum((x["interest"] for x in rows), Decimal("0.00")),
        "total_principal": sum((x["principal"] for x in rows), Decimal("0.00")),
        "installment": rows[0]["installment"] if rows else Decimal("0.00"),
        "count": len(rows),
    }
    return rows, totals
