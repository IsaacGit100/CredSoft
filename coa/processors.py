# processors.py
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class TransactionProcessor:
    """Processes transactions and creates journal entries"""
    
    def __init__(self, transaction, user=None):
        self.trans = transaction
        self.user = user
        self.journal = None
        self.lines = []
    
    def process(self):
        """Main processing function"""
        with transaction.atomic():
            # Step 1: Validate transaction
            self.validate()
            
            # Step 2: Create journal entry
            self.create_journal()
            
            # Step 3: Create journal lines (double-entry)
            self.create_journal_lines()
            
            # Step 4: Update member records based on behavior
            self.update_member_records()
            
            # Step 5: Mark transaction as processed
            self.trans.processed = True
            self.trans.journal = self.journal
            self.trans.save()
            
            return self.journal
    
    def validate(self):
        """Validate transaction can be processed"""
        if not self.trans.ledger:
            raise ValueError("Transaction has no ledger account")
        
        if self.trans.processed:
            raise ValueError("Transaction already processed")
    
    def create_journal(self):
        """Create the journal entry header"""
        from .models import JournalEntry
        import random
        
        # Generate entry number
        entry_number = f"JE-{self.trans.date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        self.journal = JournalEntry.objects.create(
            entry_number=entry_number,
            entry_date=self.trans.date,
            description=f"{self.trans.rec_vou_no} - {self.trans.details or self.trans.purpose}",
            source_trans=self.trans,
            batch_number=f"BATCH-{timezone.now().strftime('%Y%m%d')}",
        )
    
    def create_journal_lines(self):
        """Create double-entry journal lines"""
        from .models import JournalLine
        
        behavior_info = get_behavior_info(self.trans.ledger.behavior)
        
        # Determine the offset account based on transaction type
        if self.trans.trans_type == 'Receipts':
            # Receipts: Debit Cash, Credit Income/Liability
            lines = self._create_receipt_lines()
        else:
            # Payments: Debit Expense/Asset, Credit Cash
            lines = self._create_payment_lines()
        
        # Create all lines
        for line_data in lines:
            JournalLine.objects.create(
                journal=self.journal,
                **line_data
            )
    
    def _create_receipt_lines(self):
        """Create journal lines for receipts"""
        lines = []
        
        # Line 1: Debit to Cash/Bank
        cash_account = ChartOfAccounts.objects.get(behavior='CASH')
        lines.append({
            'account': cash_account,
            'member': self.trans.member if cash_account.affects_master else None,
            'debit': self.trans.amount,
            'credit': 0,
            'line_description': f"Receipt from {self.trans.member_name or self.trans.non_member_name}",
        })
        
        # Line 2: Credit to the selected ledger account
        lines.append({
            'account': self.trans.ledger,
            'member': self.trans.member if self.trans.ledger.affects_master else None,
            'debit': 0,
            'credit': self.trans.amount,
            'line_description': self.trans.purpose,
        })
        
        return lines
    
    def _create_payment_lines(self):
        """Create journal lines for payments"""
        lines = []
        
        # Line 1: Debit to the selected ledger account
        lines.append({
            'account': self.trans.ledger,
            'member': self.trans.member if self.trans.ledger.affects_master else None,
            'debit': self.trans.amount,
            'credit': 0,
            'line_description': self.trans.purpose,
        })
        
        # Line 2: Credit to Cash/Bank
        cash_account = ChartOfAccounts.objects.get(behavior='CASH')
        lines.append({
            'account': cash_account,
            'member': self.trans.member if cash_account.affects_master else None,
            'debit': 0,
            'credit': self.trans.amount,
            'line_description': f"Payment to {self.trans.member_name or self.trans.non_member_name}",
        })
        
        return lines
    
    def update_member_records(self):
        """Update member records based on account behavior"""
        for line in self.journal.lines.all():
            if not line.member:
                continue
            
            behavior_info = get_behavior_info(line.account.behavior)
            if not behavior_info['affects_member']:
                continue
            
            field_name = behavior_info['field']
            if not field_name or not hasattr(line.member, field_name):
                continue
            
            current_value = getattr(line.member, field_name) or Decimal('0.00')
            direction = behavior_info['direction']
            
            # Update based on direction rule
            if direction == 'increase_on_debit':
                if line.debit > 0:
                    new_value = current_value + line.debit
                else:
                    new_value = current_value - line.credit
            elif direction == 'increase_on_credit':
                if line.credit > 0:
                    new_value = current_value + line.credit
                else:
                    new_value = current_value - line.debit
            elif direction == 'decrease_on_debit':
                if line.debit > 0:
                    new_value = current_value - line.debit
                else:
                    new_value = current_value + line.credit
            
            # Update member record
            setattr(line.member, field_name, new_value)
            line.member.save()
            
            # Mark line as updated
            line.member_updated = True
            line.save()
            
            logger.info(f"Updated member {line.member.id} {field_name}: {current_value} -> {new_value}")