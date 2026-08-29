from django.db import models
from coa.models import ChartOfAccounts
from UserAuth.models import User
from decimal import Decimal

# Create your models here.
class GeneralLedger(models.Model):
    """
    General Ledger - Stores the current balance for each account
    Think of this as a running total for each account:
    - Cash Account: ₵10,000
    - Member Savings: ₵50,000
    - etc.
    """
    # Each account has ONE ledger entry (One-to-One relationship)
    account = models.OneToOneField(ChartOfAccounts, on_delete=models.CASCADE, related_name='ledger')
    
    # Balance fields
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal(0.00))
    open_bal_date = models.DateField(null=True, blank=True, default=None)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    period_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Current period
    year_to_date = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)   # Year to date
    
    # Track last update
    last_updated = models.DateTimeField(auto_now=True)
    last_journal = models.ForeignKey('JournalEntry', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "General Ledger"
    
    def __str__(self):
        return f"{self.account.account_code} - {self.account.account_name}: ₵{self.current_balance:,.2f}"
    
    def update_balance(self, amount, is_debit):
        """
        Update balance based on debit/credit and account type
        This is the core accounting logic!
        """
        # Rule: Assets and Expenses increase with DEBIT
        #       Liabilities, Equity, Income increase with CREDIT
        if self.account.account_type in ['ASSET', 'EXPENSE']:
            if is_debit:
                self.current_balance += amount  # Debit increases
            else:
                self.current_balance -= amount  # Credit decreases
        else:  # LIABILITY, EQUITY, INCOME
            if is_debit:
                self.current_balance -= amount  # Debit decreases
            else:
                self.current_balance += amount  # Credit increases
        
        self.save()
        return self.current_balance
    
    @property
    def last_transaction_date(self):
        last_line = self.account.lines.order_by('-journal__entry_date', '-journal__id').first()
        return last_line.journal.entry_date if last_line else None
    
class JournalEntry(models.Model):
    """
    Journal Entry - The header of an accounting entry
    Think of this as a receipt or invoice number that groups related transactions
    Example: JE-001 for a member deposit transaction
    """
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft - Not yet posted to ledger'),
        ('POSTED', 'Posted - Affects account balances'),
        ('VOID', 'Void - Cancelled'),
    ]
    
    # Identification
   # entry_number = models.CharField(max_length=20, unique=True)  # Like JE-20240325-001
    entry_number = models.CharField(max_length=20)  # Like JE-20240325-001
    entry_date = models.DateField()
    description = models.CharField(max_length=200)
    
    # Link to source transaction (from RecPayApp)
    source_trans = models.ForeignKey('RecPayApp.Trans', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries')
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='journals_created')
    
    class Meta:
        ordering = ['-entry_date', '-entry_number']
    
    def __str__(self):
        return f"{self.entry_number} - {self.entry_date} - {self.description[:50]}"
    
    def total_debit(self):
        """Sum of all debit lines in this journal"""
        return self.lines.aggregate(total=models.Sum('debit'))['total'] or 0
    
    def total_credit(self):
        """Sum of all credit lines in this journal"""
        return self.lines.aggregate(total=models.Sum('credit'))['total'] or 0
    
    def is_balanced(self):
        """Check if debits equal credits"""
        return self.total_debit() == self.total_credit()
    
    def post(self, user=None):
        """
        Post this journal to the general ledger
        This is the most important function!
        """
        if self.posted:
            return
        
        # Use transaction to ensure all or nothing
        from django.db import transaction as db_transaction
        
        with db_transaction.atomic():
            # Post each line to the ledger
            for line in self.lines.all():
                line.post_to_ledger()
            
            # Mark journal as posted
            self.posted = True
            self.posted_at = timezone.now()
            self.posted_by = user
            self.save()
            
            # Update source transaction if exists
            if self.source_trans:
                self.source_trans.status = 'POSTED'
                self.source_trans.save()
            
            print(f"✅ Posted journal: {self.entry_number}")
            

class JournalLine(models.Model):
    """Journal Line Items - Debit/Credit entries"""
    
    journal = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='journal_lines')
    member = models.ForeignKey('MembersApp.Master', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_lines')
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    line_description = models.CharField(max_length=200, blank=True)
    ledger_updated = models.BooleanField(default=False)
    member_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.journal.entry_number} - {'DR' if self.debit > 0 else 'CR'}"
    
    def post_to_ledger(self):
        """Post this line to the general ledger"""
        # Get or create ledger for this account
        ledger, created = GeneralLedger.objects.get_or_create(
            account=self.account,
            defaults={
                'opening_balance': 0,
                'current_balance': 0,
                'period_balance': 0,
                'year_to_date': 0,
            }
        )
        
        # Update balance based on account type
        if self.debit > 0:
            if self.account.account_type in ['ASSET', 'EXPENSE']:
                ledger.current_balance += self.debit
            else:
                ledger.current_balance -= self.debit
        else:  # credit > 0
            if self.account.account_type in ['ASSET', 'EXPENSE']:
                ledger.current_balance -= self.credit
            else:
                ledger.current_balance += self.credit
        
        ledger.last_journal = self.journal
        ledger.save()
        
        self.ledger_updated = True
        self.save()
        
        # Update member if applicable
        if self.member:
            self.update_member_balance()
    
    def update_member_balance(self):
        """Update member's record based on account behavior"""
        if not self.member:
            return
        
        behavior = self.account.behavior
        
        if behavior == 'MEMBER_SAVINGS':
            if self.debit > 0:
                self.member.tot_deposits += self.debit
            else:
                self.member.tot_deposits -= self.credit
        
        elif behavior == 'MEMBER_SHARES':
            if self.debit > 0:
                self.member.tot_shares += self.debit
            else:
                self.member.tot_shares -= self.credit
        
        elif behavior in ['LOAN_DISBURSEMENT', 'MEMBER_LOAN']:
            if self.debit > 0:
                self.member.tot_loans += self.debit
            else:
                self.member.tot_loans -= self.credit
        
        self.member.save()
        self.member_updated = True
        self.save()
        
from django.db import models
from django.utils import timezone

class FinancialIndicator(models.Model):
    date = models.DateField(unique=True)
    
    # 1. Capital Adequacy Ratio (%)
    capital_adequacy_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 2. Liquidity Ratio (%)
    liquidity_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 3. Single Obligor Limit (%)
    single_obligor_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 4. Primary Cash Reserves (%)
    primary_cash_reserves = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 5. Marketing Assets Ratio (%)
    marketing_assets_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 6. Top 5 Depositors (total amount)
    top_5_depositors = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # 7. Top 5 Exposures (total loan balance)
    top_5_exposures = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # 8. Liquid Asset / Deposit Ratio (%)
    liquid_asset_deposit_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 9. Fixed Assets To Shareholders Funds (%)
    fixed_assets_shareholders_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 10. PAR (Portfolio at Risk) (%)
    par_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 11. Loan To Deposit Ratio (%)
    loan_to_deposit_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional fields for raw data (optional)
    total_assets = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_deposits = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_loans = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Financial Indicator'
        verbose_name_plural = 'Financial Indicators'

    def __str__(self):
        return f"Indicators for {self.date}"