"""
Validation helpers for Receipts / Payments transactions.
Kept separate from views so they can be reused (edit view, API, tests).
"""

from decimal import Decimal, InvalidOperation
from datetime import datetime

from django_ledger.models import AccountModel

from RecPayApp.models import Trans
from ChurchApp.models import Member

# ---------------------------------------------------------------
# Small parsing helpers — reused by the validator AND the view
# ---------------------------------------------------------------
DATE_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")


def parse_date(value):
    """Return a date or None."""
    if not value:
        return None
    value = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(value):
    """Return Decimal or None."""
    if value is None:
        return None
    cleaned = str(value).replace(",", "").replace(" ", "")
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


# ---------------------------------------------------------------
# Main validator
# ---------------------------------------------------------------
class TransValidationResult:
    """
    Simple container: `.data` is a dict of cleaned values,
    `.errors` is a list of human-readable strings.
    """

    def __init__(self, data, errors):
        self.data = data
        self.errors = errors

    @property
    def is_valid(self):
        return not self.errors


def validate_trans_post(request, entity, coa):
    """
    Validate a Receipts/Payments POST.
    Returns TransValidationResult.
    """
    errors = []
    data = {}
    post = request.POST

    # -----------------------------------------------------------
    # 1. Transaction type
    # -----------------------------------------------------------
    trans_type = (post.get("trans_type") or "").strip()
    if trans_type not in ("Receipts", "Payments"):
        errors.append("Transaction type must be Receipts or Payments.")
    data["trans_type"] = trans_type

    # -----------------------------------------------------------
    # 2. Date
    # -----------------------------------------------------------
    date = parse_date(post.get("date"))
    if not date:
        errors.append("Invalid date. Use DD/MM/YYYY.")
    data["date"] = date

    # -----------------------------------------------------------
    # 3. Reference No (unique per entity)
    # -----------------------------------------------------------
    trans_no = (post.get("trans_no") or "").strip()
    if not trans_no:
        errors.append("Reference No is required.")
    else:
        # exclude the current instance when editing
        exclude_id = post.get("_exclude_id")
        qs = Trans.objects.filter(entity=entity, trans_no=trans_no)
        if exclude_id and exclude_id.isdigit():
            qs = qs.exclude(pk=int(exclude_id))
        if qs.exists():
            errors.append(f"Reference No '{trans_no}' already exists for this entity.")
    data["trans_no"] = trans_no

    # -----------------------------------------------------------
    # 4. Amount
    # -----------------------------------------------------------
    amount = parse_amount(post.get("amount"))
    if amount is None:
        errors.append("Amount must be a valid number.")
    elif amount <= 0:
        errors.append("Amount must be greater than zero.")
    data["amount"] = amount

    # -----------------------------------------------------------
    # 5. Payment mode
    # -----------------------------------------------------------
    pay_mode = (post.get("pay_mode") or "").strip()
    if pay_mode not in ("Cash", "Cheque", "Transfer"):
        errors.append("Invalid payment mode.")
    data["pay_mode"] = pay_mode

    # -----------------------------------------------------------
    # 6. Ledger account
    # -----------------------------------------------------------
    ledger = None
    chart_value = (post.get("chart_account") or "").strip()
    if not chart_value:
        errors.append("Ledger account is required.")
    else:
        parts = chart_value.split(",")
        if len(parts) != 3:
            errors.append("Invalid ledger account.")
        else:
            try:
                ledger = AccountModel.objects.get(
                    pk=int(parts[0]), coa_model=coa, active=True
                )
            except (AccountModel.DoesNotExist, ValueError):
                errors.append("Selected ledger account is not valid for this entity.")
    data["ledger"] = ledger

    # -----------------------------------------------------------
    # 7. Party (Member / Non-member)
    # -----------------------------------------------------------
    name_type = post.get("name_type", "")
    master_obj = church_member_obj = None
    member_no = None
    member_name = ""
    non_member_name = ""
    non_member_contact = ""

    if name_type == "Member":
        member_id = post.get("member_id", "")
        if not (member_id and member_id.isdigit()):
            errors.append("Please select a member.")
        else:
            try:
                master_obj = Member.objects.get(id=int(member_id), is_deleted=False)
                member_no = master_obj.id
                member_name = master_obj.full_name
            except Member.DoesNotExist:
                try:
                    church_member_obj = Member.objects.get(
                        id=int(member_id), entity=entity, is_deleted=False
                    )
                    member_name = church_member_obj.full_name
                except Member.DoesNotExist:
                    errors.append("Selected member was not found.")
    elif name_type == "Non Member":
        non_member_name = (post.get("non_member_name") or "").strip()
        non_member_contact = (post.get("non_member_contact") or "").strip()
        if not non_member_name:
            errors.append("Non-member name is required.")
    else:
        errors.append("Please choose a name type.")

    data.update(
        {
            "name_type": name_type,
            "master_obj": master_obj,
            "church_member_obj": church_member_obj,
            "member_no": member_no,
            "member_name": member_name,
            "non_member_name": non_member_name,
            "non_member_contact": non_member_contact,
        }
    )

    # -----------------------------------------------------------
    # 8. Loan (required only if ledger mentions "loan")
    # -----------------------------------------------------------
    loan_obj = None
    if ledger and ledger.name and "loan" in ledger.name.lower():
        loan_id = post.get("loan_id", "")
        if not (loan_id and loan_id.isdigit()):
            errors.append("This ledger requires a loan to be selected.")
        else:
            try:
                loan_obj = Loan.objects.get(id=int(loan_id))
                if master_obj and loan_obj.master_id != master_obj.id:
                    errors.append(
                        "Selected loan does not belong to the selected member."
                    )
            except Loan.DoesNotExist:
                errors.append("Selected loan was not found.")
    data["loan_obj"] = loan_obj

    # -----------------------------------------------------------
    # 9. Payment-method specifics
    # -----------------------------------------------------------
    cheque_date = None
    bank = bank_no = bank_branch = momo_no = momo_name = cheque_no = ""

    if pay_mode == "Cheque":
        cheque_no = (post.get("cheque_no") or "").strip()
        bank = (post.get("bank") or "").strip()
        bank_branch = (post.get("bank_branch") or "").strip()
        bank_no = (post.get("bank_no") or "").strip()
        cheque_date = parse_date(post.get("cheque_date"))

        if not cheque_no:
            errors.append("Cheque number is required for cheque payments.")
        if not bank:
            errors.append("Bank name is required for cheque payments.")

    elif pay_mode == "Transfer":
        momo_no = (post.get("momo_no") or "").strip()
        momo_name = (post.get("momo_name") or "").strip()
        if not momo_no:
            errors.append("Mobile money / transfer number is required.")

    data.update(
        {
            "cheque_date": cheque_date,
            "cheque_no": cheque_no,
            "bank": bank,
            "bank_no": bank_no,
            "bank_branch": bank_branch,
            "momo_no": momo_no,
            "momo_name": momo_name,
        }
    )

    return TransValidationResult(data, errors)
