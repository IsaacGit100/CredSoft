from django.core.management.base import BaseCommand
from django.db import transaction
from django_ledger.models import AccountModel, EntityModel
from RecPayApp.models import Trans

# Intent (from the name we typed) → correct COA code
INTENT_TO_CODE = {
    "Dues": "4013",
    "Tithe": "4014",
    "Tithes": "4014",
    "Day Born": "4011",
    "Guild": "4012",
}


class Command(BaseCommand):
    help = "Fix wrong ledger_code/ledger_name on service and dues_tithe Trans rows."

    def add_arguments(self, parser):
        parser.add_argument("--slug", required=True, help="Entity slug")
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually write changes (default is dry-run)",
        )

    def handle(self, *args, **options):
        slug = options["slug"]
        apply = options["apply"]

        entity = EntityModel.objects.get(slug=slug)
        coa = entity.get_default_coa()
        code_to_name = {
            a.code: a.name for a in AccountModel.objects.filter(coa_model=coa)
        }

        qs = Trans.objects.filter(
            entity=entity, sub_module__in=["service", "dues_tithe"]
        ).exclude(ledger_code="")

        changes = []
        for t in qs:
            intent = (t.ledger_name or t.purpose or "").strip()
            new_code = INTENT_TO_CODE.get(intent, t.ledger_code)
            new_name = code_to_name.get(new_code, t.ledger_name)

            if t.ledger_code != new_code or t.ledger_name != new_name:
                changes.append((t, new_code, new_name))

        self.stdout.write(f"Rows to fix: {len(changes)}")
        for t, new_code, new_name in changes:
            self.stdout.write(
                f"  id={t.pk}  code {t.ledger_code} -> {new_code}  "
                f"name {t.ledger_name!r} -> {new_name!r}"
            )

        if not apply:
            self.stdout.write(
                self.style.WARNING("\nDry run. Re-run with --apply to write changes.")
            )
            return

        with transaction.atomic():
            for t, new_code, new_name in changes:
                t.ledger_code = new_code
                t.ledger_name = new_name
                t.save(update_fields=["ledger_code", "ledger_name"])

        self.stdout.write(self.style.SUCCESS(f"Applied {len(changes)} fixes."))
