from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from AndyApp.models import StateAndy, Mastandy
from MembersApp.models import Master
from RecPayApp.models import Trans


# AndyApp/management/commands/copy_stateandy_to_trans.py
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, FieldError
from AndyApp.models import StateAndy, Mastandy
from MembersApp.models import Master
from RecPayApp.models import Trans


from django.core.management.base import BaseCommand
from AndyApp.models import StateAndy
# AndyApp/management/commands/copy_stateandy_to_trans.py
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from AndyApp.models import StateAndy
from MembersApp.models import Master
from RecPayApp.models import Trans


# AndyApp/management/commands/copy_stateandy_to_trans.py
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from tqdm import tqdm  # optional: pip install tqdm
from AndyApp.models import StateAndy
from MembersApp.models import Master
from RecPayApp.models import Trans


# AndyApp/management/commands/copy_stateandy_to_trans.py
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from AndyApp.models import StateAndy
from MembersApp.models import Master
from RecPayApp.models import Trans


# AndyApp/management/commands/copy_stateandy_to_trans.py
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from AndyApp.models import StateAndy
from MembersApp.models import Master
from RecPayApp.models import Trans


class Command(BaseCommand):
    help = 'Copy StateAndy to Trans, creating missing Master records'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Simulate without saving')
        parser.add_argument('--limit', type=int,
                            default=None, help='Limit records')
        parser.add_argument(
            '--verbose', action='store_true', help='Show details')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        verbose = options['verbose']

        states = StateAndy.objects.all().order_by('id')
        if limit:
            states = states[:limit]

        total = states.count()
        self.stdout.write(f"Found {total} StateAndy records.")

        if total == 0:
            return

        # Prepare default values for Master (adjust to match your model)
        master_defaults = {
            'first_name': 'Legacy',
            'last_name': 'Member',
            'title': 'Mr.',
            'mem_status': 'Active',
            'is_deleted': False,
            'date_created': timezone.now(),
            'date_updated': timezone.now(),
            'tot_deposits': 0,
            'tot_deposit_withdrawal': 0,
            'tot_shares': 0,
            'tot_interest_accrued': 0,
            # add all other required fields with defaults
        }

        tot_trans = 0
        receipt_cnt = 0
        receipt_amt = Decimal('0')
        payment_cnt = 0
        payment_amt = Decimal('0')
        errors = []

        for idx, state in enumerate(states, 1):
            if verbose and idx % 500 == 0:
                self.stdout.write(f"Processed {idx}/{total}...")

            # ---- Get or create Master ----
            try:
                master, created = Master.objects.get_or_create(
                    old_member_id=state.master_id,
                    defaults={
                        'full_name': f'Legacy Member {state.master_id}',
                        **master_defaults
                    }
                )
                if created and verbose:
                    self.stdout.write(
                        f"  Created Master for old_member_id={state.master_id}")
            except Exception as e:
                errors.append(
                    f"Master create error for {state.master_id}: {e}")
                continue

            # ---- Determine ledger ----
            code = state.state_code
            if code == 'Savings':
                ledger = (19, '20101001', 'Savings Deposit', '')
            elif code == 'Withdrawal':
                ledger = (20, '20101002', 'Savings Withdrawal', '')
            elif code == 'Shares':
                ledger = (23, '20101001', 'Share Capital', '')
            elif code == 'Shares Withdrawal':
                ledger = (24, '20101002', 'Share Withdrawal', '')
            elif code == 'B/F':
                ledger = (23, '20101001', 'Savings Deposit', 'B/F')
            else:
                ledger = (0, '99999999', code, 'No Records Identified')
            m_ledger_id, m_ledger_code, m_ledger_name, m_details = ledger

            # ---- Transaction type ----
            if state.trans_type == 'cr':
                m_type = 'Receipts'
                m_voucher = f'REC:{state.rec_no}-{state.id}'
                receipt_cnt += 1
                receipt_amt += state.amount
            elif state.trans_type == 'dr':
                m_type = 'Payments'
                m_voucher = f'VOU:{state.rec_no}-{state.id}'
                payment_cnt += 1
                payment_amt += state.amount
            else:
                m_type = state.trans_type
                m_voucher = f'UNK:{state.rec_no}-{state.id}'

            tot_trans += 1

            if dry_run:
                if verbose:
                    self.stdout.write(
                        f"  Would create Trans: {m_voucher} for {master.full_name}")
                continue

            # ---- Create Trans ----
            try:
                Trans.objects.create(
                    status='DRAFT',
                    rec_vou_no=m_voucher,
                    date=state.date,
                    amount=state.amount,
                    trans_no=state.rec_no,
                    trans_type=m_type,
                    member=master,
                    member_name=master.full_name,
                    # ... other fields (keep same)
                )
                if verbose and idx % 500 == 0:
                    self.stdout.write(f"  Created Trans {idx}/{total}")
            except Exception as e:
                errors.append(
                    f"Trans create error for StateAndy {state.id}: {e}")

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f"\nProcessed {tot_trans} records. "
            f"Receipts: {receipt_cnt} (₵{receipt_amt:.2f}), "
            f"Payments: {payment_cnt} (₵{payment_amt:.2f})"
        ))
        if errors:
            self.stdout.write(self.style.ERROR(f"Errors: {len(errors)}"))
            for e in errors[:10]:
                self.stdout.write(f"  {e}")
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run – no changes made."))
        else:
            self.stdout.write(self.style.SUCCESS("Copy completed."))
