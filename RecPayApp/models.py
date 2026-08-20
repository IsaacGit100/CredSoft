# RecPayApp/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

from MembersApp.models import Master
from UserAuth.models import User
from LoanApp.models import Loan

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType



class Trans(models.Model):
    """Transaction model for receipts and payments"""
    
    # Choices
    PAY_MODE = (
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Transfer', 'Transfer'),
        ('Momo', 'Mobile Money'),
    )
    
    TRANS_TYPE = (
        ('Receipts', 'Receipts'),
        ('Payments', 'Payments'),
    )
    
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('POSTED', 'Posted'),
        ('VOID', 'Void'),
    )
    
    JOURNAL_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('POSTED', 'Posted'),
    )
    MODULE_CHOICES = (
        ('church', 'Church'),
        ('school', 'School'),
        ('credit_union', 'Credit Union'),
        ('finance', 'Finance'),
    )
    module = models.CharField(max_length=20, choices=MODULE_CHOICES, default='credit_union')

    # Generic relationship to any source
    source_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    source_object_id = models.PositiveIntegerField(null=True, blank=True)
    source = GenericForeignKey('source_content_type', 'source_object_id')

    # ... existing fields (date, trans_no, amount, etc.)
    
    
    entity = models.ForeignKey('django_ledger.EntityModel', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    journal_status = models.CharField(max_length=10, choices=JOURNAL_STATUS_CHOICES, default='PENDING', help_text="Status for accounting integration")
    journal_entry_id = models.CharField(max_length=50, null=True, blank=True)
    
    
    
    
    
    # Core fields - PRESERVED existing field names
    rec_vou_no = models.CharField(max_length=35, null=True, blank=True, default='')
    trans_no = models.CharField(max_length=35, null=True, blank=True, default='')  # Kept for compatibility
    date = models.DateField()
    trans_type = models.CharField(max_length=10, choices=TRANS_TYPE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    pay_mode = models.CharField(max_length=10, choices=PAY_MODE)
    old_trans_id = models.IntegerField(default=0)
    
    
    # Member relationship - PRESERVED member_no and member_name but as properties
    member = models.ForeignKey(Master, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    member_no = models.IntegerField(null=True, blank=True, default=0)  # Kept for compatibility
    member_name = models.CharField(max_length=40, null=True, blank=True, default='')  # Kept for compatibility
    
    # Non-member transactions
    non_member_name = models.CharField(max_length=40, null=True, blank=True, default='')
    non_member_contact = models.CharField(max_length=50, null=True, blank=True, default='')
    
    # Bank Details - PRESERVED field names
    bank_date = models.DateField(blank=True, null=True)
    bank = models.CharField(max_length=100, blank=True)
    bank_no = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    cheque_date = models.DateField(blank=True, null=True)
    cheque_no = models.CharField(max_length=15, blank=True, null=True, default='')
    
    # Transfer Details
    momo_no = models.CharField(max_length=50, blank=True, default='')
    momo_name = models.CharField(max_length=100, blank=True, default='')
    
    # Finance Details - PRESERVED field names
    ledger_id = models.CharField(max_length=10, blank=True, null=True, default='')
    ledger_code = models.CharField(max_length=10, blank=True, null=True, default='')
    ledger_name = models.CharField(max_length=100, blank=True, null=True, default='')
    
    # Other Details - PRESERVED field names
    purpose = models.CharField(max_length=50, blank=True, null=True, default='')
    other_purpose = models.CharField(max_length=50, null=True, blank=True, default='')  # Kept
    details = models.CharField(max_length=70, null=True, blank=True, default='')
    
    # Loan relationship - PRESERVED loan_id and loan_name
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
#    loan_id = models.IntegerField(null=True, blank=True)  # Kept for compatibility
    loan_name = models.CharField(max_length=50, null=True, blank=True, default='')  # Kept
    
    # Batch processing
    batch_number = models.CharField(max_length=20, blank=True, null=True, default='')
    posted_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='trans_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='trans_updated')
    
    created_by_name = models.CharField(max_length=50, null=True, blank=True, default='')
    created_by_username = models.CharField(max_length=50, null=True, blank=True, default='')
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['rec_vou_no']),
            models.Index(fields=['trans_no']),
            models.Index(fields=['date']),
            models.Index(fields=['trans_type']),
            models.Index(fields=['status']),
            models.Index(fields=['member']),
            models.Index(fields=['batch_number']),
        ]
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        if self.member:
            return f"{self.rec_vou_no} - {self.member.full_name} - {self.amount}"
        elif self.non_member_name:
            return f"{self.rec_vou_no} - {self.non_member_name} - {self.amount}"
        return f"{self.rec_vou_no} - {self.amount}"
    
    @property
    def receipts(self):
        """Amount if this is a receipt"""
        return self.amount if self.trans_type == "Receipts" else Decimal('0.00')
    
    @property
    def payments(self):
        """Amount if this is a payment"""
        return self.amount if self.trans_type == "Payments" else Decimal('0.00')
    
    def save(self, *args, **kwargs):
        # Auto-generate receipt/voucher number if not provided
        if not self.rec_vou_no:
            prefix = 'RCP' if self.trans_type == 'Receipts' else 'PYT'
            # Get last transaction number for this type
            last_trans = Trans.objects.filter(
                trans_type=self.trans_type
            ).order_by('-id').first()
            
            if last_trans and last_trans.rec_vou_no:
                try:
                    last_num = int(last_trans.rec_vou_no.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            
            self.rec_vou_no = f"{prefix}-{new_num:06d}"
        
        # Auto-populate member_no and member_name from member relationship
        if self.member:
            self.member_no = self.member.id
            self.member_name = self.member.full_name
        else:
            self.member_no = 0
            if not self.member_name:  # Don't override if already set
                self.member_name = ''
        
        # Auto-populate loan_id and loan_name from loan relationship
        if self.loan:
            self.loan_id = self.loan.id
            self.loan_name = str(self.loan)
        else:
            self.loan_id = None
            if not self.loan_name:  # Don't override if already set
                self.loan_name = ''
        
        # Set trans_no to rec_vou_no for backward compatibility
        if not self.trans_no:
            self.trans_no = self.rec_vou_no
        
        super().save(*args, **kwargs)

