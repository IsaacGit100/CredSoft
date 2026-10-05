"""
Post RecPayApp.Trans rows to django_ledger as JournalEntryModel + TransactionModel.

Usage:
    python manage.py post_trans_to_journals --slug <slug>            # dry run
    python manage.py post_trans_to_journals --slug <slug> --apply    # commit
"""
from datetime import datetime, time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from django_ledger.models import (
    AccountModel,
    EntityModel,
    EntityUnitModel,
    JournalEntryModel,
    LedgerModel,
    TransactionModel,
)
from RecPayApp.models import Trans


ELIGIBLE_SUBMODULES = [
    "service",
    "dues_tithe",
    "receipts_payments",
    "opening_balance",
]

PAY_MODE_TO_CODE = {
    "Cash":     "1010",
    "Cheque":   "1020",
    "Transfer": "1020",
}


class Command(BaseCommand):
    help = "Post eligible RecPayApp.Trans rows to django_ledger journals."

    def add_arguments(self, parser):
        parser.add_argument("--slug", required=True, help="Entity slug")
        parser.add_argument("--apply", action="store_true",
                            help="Actually create journal entries (default is dry-run)")

    def handle(self, *args, **options):
        slug  = options["slug"]
        apply = options["apply"]

        entity = EntityModel.objects.get(slug=slug)

        ledger = LedgerModel.objects.filter(entity=entity).first()
        if not ledger:
            raise CommandError(f"No Ledger for entity {entity.slug}. Create one first.")

        entity_unit = EntityUnitModel.objects.filter(entity=entity, active=True).first()
        if not entity_unit:
            raise CommandError(f"No active EntityUnit for entity {entity.slug}.")

        coa = entity.get_default_coa()
        if not coa:
            raise CommandError(f"No default COA for entity {entity.slug}.")

        code_to_account = {
            a.code: a for a in AccountModel.objects.filter(coa_model=coa)
        }

        jid_field = Trans._meta.get_field("journal_entry_id")
        self.stdout.write(f"Trans.journal_entry_id max_length = {jid_field.max_length}")

        qs = (
            Trans.objects
            .filter(entity=entity, sub_module__in=ELIGIBLE_SUBMODULES)
            .filter(Q(journal_entry_id__isnull=True) | Q(journal_entry_id=""))
            .order_by("date", "id")
        )

        self.stdout.write(f"Candidates: {qs.count()}")

        previews = []
        skipped = []

        for t in qs:
            dr_code, cr_code = self._resolve_dr_cr(t)
            if not dr_code or not cr_code:
                skipped.append((t, f"missing DR/CR codes (dr={dr_code!r} cr={cr_code!r})"))
                continue

            dr_acc = code_to_account.get(dr_code)
            cr_acc = code_to_account.get(cr_code)
            if not dr_acc:
                skipped.append((t, f"DR account {dr_code} not in COA"))
                continue
            if not cr_acc:
                skipped.append((t, f"CR account {cr_code} not in COA"))
                continue

            previews.append((t, dr_acc, cr_acc))
            self.stdout.write(
                f"  id={t.pk:<5} {t.date} {t.trans_type:<9} "
                f"amt={t.amount:>10}  DR {dr_code} / CR {cr_code}  "
                f"({t.ledger_name or t.purpose or t.details})"
            )

        self.stdout.write(f"\nWould post: {len(previews)}")
        if skipped:
            self.stdout.write(self.style.WARNING(f"Skipped: {len(skipped)}"))
            for t, reason in skipped[:30]:
                self.stdout.write(f"  id={t.pk}  reason: {reason}")

        if not apply:
            self.stdout.write(self.style.WARNING(
                "\nDry run. Re-run with --apply to actually post."
            ))
            return

        posted = 0
        with transaction.atomic():
            for t, dr_acc, cr_acc in previews:
                ts = timezone.make_aware(datetime.combine(t.date, time.min))

                # 1. Create JE in draft (posted=False) so we can add lines
                je = JournalEntryModel.objects.create(
                    ledger=ledger,
                    entity_unit=entity_unit,
                    je_number=f"JE-{t.date:%Y%m}-{t.pk:06d}",
                    timestamp=ts,
                    description=(t.details or t.purpose or t.ledger_name or "")[:250],
                    posted=False,  # ← draft first
                    origin="RecPayApp",
                )

                # 2. Add the two lines
                TransactionModel.objects.create(
                    journal_entry=je,
                    tx_type="debit",
                    account=dr_acc,
                    amount=t.amount,
                    description=(t.details or t.purpose or "")[:250],
                )
                TransactionModel.objects.create(
                    journal_entry=je,
                    tx_type="credit",
                    account=cr_acc,
                    amount=t.amount,
                    description=(t.details or t.purpose or "")[:250],
                )

                # 3. Now mark the JE as posted
                je.posted = True
                je.save(update_fields=["posted"])

                # 4. Link back to the Trans row
                t.journal_entry_id = str(je.uuid)
                t.journal_status = "POSTED"
                t.save(update_fields=["journal_entry_id", "journal_status"])

                posted += 1

                

        self.stdout.write(self.style.SUCCESS(f"\nPosted {posted} journal entries."))

    def _resolve_dr_cr(self, t):
        """Return (dr_code, cr_code) for a Trans row, or (None, None)."""
        if t.trans_type == "Receipts":
            return (PAY_MODE_TO_CODE.get(t.pay_mode, "1010"), t.ledger_code)
        if t.trans_type == "Payments":
            return (t.ledger_code, PAY_MODE_TO_CODE.get(t.pay_mode, "1010"))
        if t.trans_type == "Journal":
            return (t.debit_account_code, t.credit_account_code)
        return (None, None)
