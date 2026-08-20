from django.db import models

# Create your models here.
# RecPayApp/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

from MembersApp.models import Master
from UserAuth.models import User
from LoanApp.models import Loan


class StateTrans(models.Model):
    state_date = models.DateField(blank=True, null=True, default=None)
    state_type = models.CharField(max_length = 15, null=True, blank=True, default='')
    rec_vou_no = models.CharField(max_length=15, null=True, blank=True, default='')
    trans_no = models.CharField(max_length=15, null=True, blank=True, default='')  # Kept for compatibility
    date = models.DateField(null=True, blank=True, default=None)
    trans_type = models.CharField(max_length=10, null=True, blank=True, default='')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    pay_mode = models.CharField(max_length=10, null=True, blank=True, default='')
    
    # Foreign Tables
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True, related_name='StateTransLoan')
    loan_name = models.CharField(max_length=50, null=True, blank=True, default='')  # Kept
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, null=True, blank=True, related_name='StateTransMaster')
    master_name = models.CharField(max_length=40, null=True, blank=True, default='')  # Kept for compatibility
    
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
    details = models.CharField(max_length=50, null=True, blank=True, default='')
    
    # Loan relationship - PRESERVED loan_id and loan_name
    
    
    # Audit Processing
    posted_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='StateTransCreated')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='StateTransUpdated')
    
    created_by_who_id = models.IntegerField(null=True, blank=True, default=0)
    created_by_name = models.CharField(max_length=100, blank=True, null=True, default='')
    created_by_username =  models.CharField(max_length=100, blank=True, null=True, default='')


class StateUpdate(models.Model):
    state_update_date = models.DateField(null=True, blank=True, default=None)
    rec_vou_no = models.CharField(max_length=15, null=True, blank=True, default='')
    trans_no = models.CharField(max_length=15, null=True, blank=True, default='') 
    trans_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    date = models.DateField(null=True, blank=True, default=None)
    trans_type = models.CharField(max_length=10, null=True, blank=True, default='')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    activity = models.CharField(max_length=60, unique=True, null=True, blank=True, default='')
    
    ledger_id = models.CharField(max_length=10, blank=True, null=True, default='')
    ledger_code = models.CharField(max_length=10, blank=True, null=True, default='')
    ledger_name = models.CharField(max_length=100, blank=True, null=True, default='')
    
    old_enrollment_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    new_enrollment_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    old_shares = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    new_shares = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    old_shares_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    new_shares_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    old_deposit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    new_deposit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    old_deposit_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    new_deposit_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    old_dividend = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    new_dividend = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    old_dividend_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    new_dividend_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    old_int_accrued = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    new_int_accrued = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    old_available_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    new_available_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00) 

    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updUserCreator')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updUserUpdator')
    
    
class StateJournalEntry(models.Model):
    original_id = models.CharField(max_length=255, null=True, blank=True)   # changed
    source_trans_id = models.CharField(max_length=255, null=True, blank=True)  # changed
    posted_by_id = models.CharField(max_length=255, null=True, blank=True)  # changed
    entry_number = models.CharField(max_length=20)
    entry_date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=10)
    posted = models.BooleanField(default=True)
    posted_at = models.DateTimeField()
    archived_at = models.DateTimeField(auto_now_add=True)

class StateJournalLine(models.Model):
    original_id = models.CharField(max_length=255, null=True, blank=True)   # changed
    member_id = models.CharField(max_length=255, null=True, blank=True)     # changed
    journal_entry_number = models.CharField(max_length=20)
    account_code = models.CharField(max_length=10)
    debit = models.DecimalField(max_digits=15, decimal_places=2)
    credit = models.DecimalField(max_digits=15, decimal_places=2)
    line_description = models.TextField()
    archived_at = models.DateTimeField(auto_now_add=True)
