from django.db import models
from django.contrib import admin


# Create your models here.
class ServiceRun(models.Model):
    KIND_CHOICES = [("preflight", "Preflight"), ("main", "Main run")]
    entity = models.ForeignKey("django_ledger.EntityModel",  null=True, blank=True,  on_delete=models.CASCADE, related_name="service_runs")
    service_name = models.CharField(max_length=100, db_index=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default="main")
    run_date = models.DateField(db_index=True)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("RUNNING", "Running"),
            ("SUCCESS", "Success"),
            ("PARTIAL", "Partial"),
            ("FAILED", "Failed"),
            ("BLOCKED", "Blocked by gate"),
        ],
        default="RUNNING",
    )

    written = models.PositiveIntegerField(default=0)
    skipped = models.PositiveIntegerField(default=0)
    errors = models.PositiveIntegerField(default=0)
    error_detail = models.TextField(blank=True)
    triggered_by = models.CharField(max_length=20, default="cron")

    class Meta:
        unique_together = ("service_name", "kind", "run_date")
        ordering = ["-run_date", "service_name", "kind"]

class ServiceGate(models.Model):
    """
    Human-controlled override for the main run of a given night.

    Created automatically when preflight finds problems.
    Cleared by an admin (release / delay / abort).
    """

    ACTION_CHOICES = [
        ("PENDING", "Awaiting human decision"),
        ("RELEASE", "Released — proceed"),
        ("DELAY", "Delayed — run later"),
        ("ABORT", "Aborted — skip tonight"),
    ]

    run_date = models.DateField(unique=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default="PENDING")
    reason = models.TextField(blank=True)
    decided_by = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    run_after = models.DateTimeField(null=True, blank=True)  # for DELAY

    def __str__(self):
        return f"Gate {self.run_date} → {self.action}"


class EntityResetLog(models.Model):
    """
    Immutable audit trail of every entity data reset.
    Never delete rows from this table.
    """

    entity = models.ForeignKey(
        "django_ledger.EntityModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reset_logs",
    )
    entity_name = models.CharField(max_length=200)  # snapshot
    entity_slug = models.CharField(max_length=200)  # snapshot
    reset_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
    )
    reset_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField()  # JSON of counts
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-reset_at"]

    def __str__(self):
        return f"Reset {self.entity_slug} @ {self.reset_at:%Y-%m-%d %H:%M}"
