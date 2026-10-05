import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CredSoft.settings")
django.setup()

from RecPayApp.models import Trans
from ChurchApp.models import MemberContribution

posted = Trans.objects.filter(
    module="church",
    trans_type="Receipts",
    journal_status="POSTED",
    church_member__isnull=False,
)

created = 0
for t in posted:
    if MemberContribution.objects.filter(trans=t).exists():
        continue

    MemberContribution.objects.create(
        entity=t.entity,
        member=t.church_member,
        trans=t,
        date=t.date,
        amount=t.amount,
        ledger_code=(t.ledger_code or "")[:20],
        ledger_name=(t.ledger_name or "")[:100],
        details=(t.details or "")[:250],
        receipt_no=(t.rec_vou_no or "")[:50],
    )
    created += 1
    print(f"  + {t.rec_vou_no}  {t.church_member.full_name}  ₵{t.amount}")

print(f"\nCreated {created} contribution rows.")
