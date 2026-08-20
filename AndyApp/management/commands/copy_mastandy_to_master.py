from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from AndyApp.models import Mastandy
from MembersApp.models import Master
from django.utils import timezone


from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from AndyApp.models import Mastandy
from MembersApp.models import Master
from django.utils import timezone


# MembersApp/management/commands/copy_mastandy_to_master.py
from django.core.management.base import BaseCommand
from AndyApp.models import Mastandy
from MembersApp.models import Master
from django.utils import timezone


class Command(BaseCommand):
    help = 'Copy all records from Mastandy to Master (idempotent, sorted by id)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be copied without actually saving',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        # Sort by Mastandy.id ascending
        mastandy_records = Mastandy.objects.all().order_by('id')
        total = mastandy_records.count()
        created = 0
        updated = 0
        skipped = 0
        errors = []

        self.stdout.write(f"Found {total} records in Mastandy (ordered by id)")

        for old in mastandy_records:
            # Check if already copied by old_member_id
            existing = Master.objects.filter(old_member_id=old.id).first()
            if existing:
                skipped += 1
                continue

            # Map fields – adjust to your actual field names
            try:
                if dry_run:
                    self.stdout.write(
                        f"Would copy: {old.full_name} (ID {old.id})")
                    created += 1
                    continue

                # Use update_or_create to avoid duplicates (though we already checked)
                master, created_flag = Master.objects.update_or_create(
                    old_member_id=old.id,
                    defaults={
                        # Personal information
                        'first_name': old.first_name,
                        'last_name': old.last_name,
                        'full_name': old.full_name,
                        'title': getattr(old, 'title', 'Mr.'),
                        'date_of_birth': getattr(old, 'date_of_birth', None),
                        'gender': getattr(old, 'gender', ''),
                        'marital_status': getattr(old, 'marital_status', 'Single'),
                        'ghana_card_no': getattr(old, 'ghana_card_no', ''),
                        'profession': getattr(old, 'profession', ''),
                        # Contact
                        'postal_address': getattr(old, 'postal_address', ''),
                        'residential_address': getattr(old, 'residential_address', ''),
                        'city': getattr(old, 'city', ''),
                        'telephone1': getattr(old, 'telephone1', ''),
                        'telephone2': getattr(old, 'telephone2', ''),
                        'email_address': getattr(old, 'email_address', ''),
                        # Financial defaults
                        'tot_deposits': 0,
                        'tot_deposit_withdrawal': 0,
                        'tot_shares': 0,
                        'tot_shares_withdrawal': 0,
                        'tot_interest_accrued': 0,
                        'tot_dividend': 0,
                        'tot_dividend_withdrawal': 0,
                        'enrollment_fees': 0,
                        # Status
                        'mem_status': 'Active',
                        'is_deleted': False,
                        # Audit
                        'date_created': timezone.now(),
                        'date_updated': timezone.now(),
                    }
                )
                if created_flag:
                    created += 1
                    self.stdout.write(
                        f"Created: {master.full_name} (old ID {old.id})")
                else:
                    updated += 1
                    self.stdout.write(
                        f"Updated: {master.full_name} (old ID {old.id})")
            except Exception as e:
                errors.append(f"ID {old.id}: {str(e)}")
                self.stdout.write(self.style.ERROR(f"Error on {old.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Created: {created}, Updated: {updated}, Skipped (already existed): {skipped}, Errors: {len(errors)}"
        ))
        if errors:
            self.stdout.write(self.style.ERROR("Errors:"))
            for err in errors:
                self.stdout.write(f"  {err}")
