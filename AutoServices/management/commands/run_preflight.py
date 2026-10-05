"""
Pre-flight dry-run.

Runs every service in dry-run mode, ~1 hour before the main job.
If any service reports errors, it creates a ServiceGate (PENDING)
that will block the main run until a human releases or aborts it.
"""

import json
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from RecPayApp.models import EntityModel
from AutoServices.models import ServiceGate, ServiceRun
from AutoServices.services.runner import SERVICES, run_one_service


class Command(BaseCommand):
    help = "Pre-flight dry-run before the main nightly job."

    def add_arguments(self, parser):
        parser.add_argument("--slug")
        parser.add_argument("--date")

    def handle(self, *args, **opts):
        today = (
            datetime.strptime(opts["date"], "%Y-%m-%d").date()
            if opts.get("date")
            else timezone.localdate()
        )

        entities = EntityModel.objects.all()
        if opts.get("slug"):
            entities = entities.filter(slug=opts["slug"])

        total_errors = 0
        for svc in SERVICES:
            for entity in entities:
                res = run_one_service(
                    svc, entity, today, kind="preflight", dry_run=True
                )
                total_errors += res.get("errors", 0)

        if total_errors:
            gate, created = ServiceGate.objects.get_or_create(run_date=today)
            gate.action = "PENDING"
            gate.reason = f"Preflight found {total_errors} error(s)."
            gate.decided_by = None
            gate.decided_at = None
            gate.save()
            self.stdout.write(
                self.style.ERROR(
                    f"Preflight found {total_errors} error(s). "
                    f"Main run is GATED. Review ServiceRun rows, then release."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Preflight clean. Main run will proceed as scheduled."
                )
            )
