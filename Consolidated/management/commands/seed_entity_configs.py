"""
Ensure every EntityModel has an EntityConfig row and a sensible entity_type.
"""
from django.core.management.base import BaseCommand
from django_ledger.models import EntityModel
from djan_led.models import EntityConfig


class Command(BaseCommand):
    help = "Seed EntityConfig rows for all entities."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true",
                            help="Write changes (default is dry-run)")

    def handle(self, *args, **options):
        apply = options["apply"]

        created = 0
        typed = 0

        for entity in EntityModel.objects.all():
            cfg = getattr(entity, "config", None)

            if cfg is None:
                self.stdout.write(f"  no config: {entity.slug} ({entity.name})")
                if apply:
                    cfg = EntityConfig.objects.create(entity=entity)
                    created += 1

            if apply and cfg and not cfg.entity_type:
                name_lower = (entity.name or "").lower()
                if "credit" in name_lower or "union" in name_lower:
                    cfg.entity_type = "credit_union"
                elif "parish" in name_lower or "church" in name_lower:
                    cfg.entity_type = "church"
                else:
                    cfg.entity_type = "other"
                cfg.save(update_fields=["entity_type"])
                typed += 1

        if not apply:
            self.stdout.write(self.style.WARNING(
                "\nDry run. Re-run with --apply to write changes."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nCreated {created} configs, typed {typed} configs."
            ))
