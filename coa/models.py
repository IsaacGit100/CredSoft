# coa/models.py - FINAL CORRECT VERSION
from django.db import models
from django.core.exceptions import ValidationError

class ChartOfAccounts(models.Model):
    ACCOUNT_TYPES = [
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('EQUITY', 'Equity'),
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    
    BEHAVIOR_CHOICES = [
        ('NORMAL', 'Normal'),
        ('CASH', 'Cash Account'),
        ('BANK', 'Bank Account'),
        ('MOMO', 'Mobile Money'),
        ('SAVINGS', 'Member Savings'),
        ('SHARES', 'Member Shares'),
        ('LOAN', 'Loan Account'),
    ]
    
    accountno = models.CharField(max_length=8, unique=True, blank=True, null=True)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    behavior = models.CharField(max_length=20, choices=BEHAVIOR_CHOICES, default='NORMAL')
    parent_account = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    
    is_data_entry = models.BooleanField(default=False)
    is_data_filled = models.BooleanField(default=False)
    is_data_view = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.accountno} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.accountno:
            self.accountno = self.generate_account_number()
        super().save(*args, **kwargs)
    
    def generate_account_number(self):
        """Generate account number in format: X XX XX XXX (8 digits)"""
        
        # LEVEL 1: Top Level (No Parent)
        if not self.parent_account:
            type_map = {
                'ASSET': '1',
                'LIABILITY': '2',
                'EQUITY': '3',
                'INCOME': '4',
                'EXPENSE': '5',
            }
            major = type_map.get(self.account_type, '9')
            return f"{major}0000000"  # 1 00 00 000 = 10000000
        
        parent = self.parent_account
        parent_code = parent.accountno
        
        # Count non-zero digits to determine level
        # 10000000 = 1 non-zero (Level 1)
        # 10100000 = 2 non-zero? Actually 1 and 01 = positions 1 and 2-3 = 3 non-zero digits total
        # Let me use a different approach: check the parent's pattern
        
        # LEVEL 2: Parent is Level 1 (format: X 00 00 000)
        if parent_code[1:3] == '00' and parent_code[3:5] == '00' and parent_code[5:8] == '000':
            # Parent is like 10000000, 20000000
            major = parent_code[0]
            
            existing = ChartOfAccounts.objects.filter(parent_account=parent).order_by('-accountno')
            if existing.exists():
                highest = existing.first()
                current_sub = int(highest.accountno[1:3])
                next_sub = current_sub + 1
            else:
                next_sub = 1
            
            return f"{major}{next_sub:02d}00000"
        
        # LEVEL 3: Parent is Level 2 (format: X 01 00 000)
        elif parent_code[3:5] == '00' and parent_code[5:8] == '000':
            # Parent is like 10100000, 10200000
            prefix = parent_code[:3]  # First 3 digits: "101"
            
            existing = ChartOfAccounts.objects.filter(parent_account=parent).order_by('-accountno')
            if existing.exists():
                highest = existing.first()
                current_group = int(highest.accountno[3:5])
                next_group = current_group + 1
            else:
                next_group = 1
            
            return f"{prefix}{next_group:02d}000"
        
        # LEVEL 4: Leaf accounts (Parent is Level 3, format: X 01 01 000)
        else:
            # Parent is like 10101000, 10102000
            prefix = parent_code[:5]  # First 5 digits: "10101"
            
            existing = ChartOfAccounts.objects.filter(parent_account=parent).order_by('-accountno')
            if existing.exists():
                highest = existing.first()
                current_seq = int(highest.accountno[5:8])
                next_seq = current_seq + 1
            else:
                next_seq = 1
            
            return f"{prefix}{next_seq:03d}"
    
    def can_have_children(self):
        return not self.is_data_filled and self.is_active
    
    class Meta:
        ordering = ['accountno']
        
        
# coa/models.py - Add this model
from django.contrib.auth.models import User


class AccountVisibilityPreference(models.Model):
    """Store user preferences for which accounts appear in transaction forms"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_preferences')
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE, related_name='visibility_preferences')
    is_visible = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'account']
        ordering = ['order', 'account__accountno']
    
    def __str__(self):
        return f"{self.user.username} - {self.account.name}: {'Visible' if self.is_visible else 'Hidden'}"