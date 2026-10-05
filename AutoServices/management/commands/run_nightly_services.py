"""
Main nightly automation run.

Usage:
    python manage.py run_nightly_services
    python manage.py run_nightly_services --slug X
    python manage.py run_nightly_services --date 2026-09-30
    python manage.py run_nightly_services --dry-run
    python manage.py run_nightly_services --force
    python manage.py run_nightly_services --only daily_sav_runs
"""

import time
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from RecPayApp.models import EntityModel
from AutoServices.models import ServiceGate
from AutoServices.services.runner import SERVICES, run_one_service


class Command(BaseCommand):
    help = "Main nightly automation run."

    def add_arguments(self, parser):
        parser.add_argument("--slug", help="Only this entity")
        parser.add_argument("--date", help="Override date YYYY-MM-DD")
        parser.add_argument(
            "--dry-run", action="store_true", help="Preview only — write nothing"
        )
        parser.add_argument(
            "--force", action="store_true", help="Ignore the preflight gate"
        )
        parser.add_argument("--only", help="Run only the named service")

    def handle(self, *args, **opts):
        today = (
            datetime.strptime(opts["date"], "%Y-%m-%d").date()
            if opts.get("date")
            else timezone.localdate()
        )
        dry = opts["dry_run"]
        only = opts.get("only")

        # -------- gate check (skipped on dry-run) --------
        if not dry:
            gate = ServiceGate.objects.filter(run_date=today).first()
            if gate and not opts["force"]:
                if gate.action == "PENDING":
                    self.stderr.write(
                        self.style.ERROR(
                            f"Gate is PENDING for {today}. "
                            f"Release in admin or use --force."
                        )
                    )
                    return
                if gate.action == "DELAY":
                    if gate.run_after and timezone.now() < gate.run_after:
                        wait = (gate.run_after - timezone.now()).total_seconds()
                        self.stdout.write(
                            f"Delayed until {gate.run_after}. Sleeping {wait:.0f}s..."
                        )
                        time.sleep(max(wait, 0))
                if gate.action == "ABORT":
                    self.stderr.write(
                        self.style.WARNING(
                            f"Gate says ABORT for {today}. Skipping tonight."
                        )
                    )
                    return

        # -------- entities --------
        entities = EntityModel.objects.all()
        if opts.get("slug"):
            entities = entities.filter(slug=opts["slug"])
        if not entities.exists():
            self.stderr.write("No entities matched.")
            return

        # -------- run services --------
        kind = "preflight" if dry else "main"
        totals = {"written": 0, "skipped": 0, "errors": 0}

        for svc in SERVICES:
            name = svc.__name__.rsplit(".", 1)[-1]
            if only and only != name:
                continue
            self.stdout.write(self.style.MIGRATE_HEADING(f"→ {name}"))
            for entity in entities:
                result = run_one_service(svc, entity, today, kind=kind, dry_run=dry)
                line = (
                    f"    [{result.get('date', today)}] "
                    f"{result.get('entity', entity.slug)}: "
                    f"{result.get('written', 0)} written, "
                    f"{result.get('skipped', 0)} skipped"
                )
                if result.get("errors"):
                    line += f", {result['errors']} errors"
                self.stdout.write(self.style.SUCCESS(line))
                for err in result.get("error_list", [])[:5]:
                    self.stderr.write(f"      ! {err}")
                totals["written"] += result.get("written", 0)
                totals["skipped"] += result.get("skipped", 0)
                totals["errors"] += result.get("errors", 0)

        mode = "DRY-RUN" if dry else "MAIN"
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{mode} complete — "
                f"{totals['written']} written, "
                f"{totals['skipped']} skipped, "
                f"{totals['errors']} errors."
            )
        )
