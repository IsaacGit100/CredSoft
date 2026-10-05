from services.transaction_posting_service import register_module_handler
from ChurchApp.models import MemberContribution

def handle_church_giving(trans):
    if (trans.module or "").lower() != "church":
        return
    if trans.trans_type != "Receipts":
        return

    # Use church_member — not member
    if not trans.church_member_id:
        return

    if MemberContribution.objects.filter(trans=trans).exists():
        return

    MemberContribution.objects.create(
        entity=trans.entity,
        member_id=trans.church_member_id,  
        trans=trans,
        date=trans.date,
        amount=trans.amount,
        ledger_code=(trans.ledger_code or "")[:20],
        ledger_name=(trans.ledger_name or "")[:100],
        details=(trans.details or "")[:250],
        receipt_no=(trans.rec_vou_no or "")[:50],
    )


register_module_handler("church", handle_church_giving)
