import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CredSoft.settings")
django.setup()

from django_ledger.models import EntityModel, JournalEntryModel, TransactionModel
from django.db.models import Sum

for e in EntityModel.objects.all():
    journals = JournalEntryModel.objects.filter(ledger__entity=e)
    lines = TransactionModel.objects.filter(journal_entry__in=journals)

    d = lines.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or 0
    c = lines.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or 0
    diff = d - c

    mark = "✓" if abs(diff) < 0.01 else "✗"
    print(f"{mark}  {e.slug:42s}  Dr={d:>14}  Cr={c:>14}  diff={diff}")
