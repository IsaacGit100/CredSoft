from django.db import models

# Create your models here.
# FinanceApp/models/opening_balance.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class OpeningBalanceLine(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('POSTED', 'Posted'),
    )
    account = models.ForeignKey('coa.ChartOfAccounts', on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    date = models.DateField(null=True, blank=True, default=None)
    ledger_entry = models.ForeignKey('FinanceApp.GeneralLedger', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_obl')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_obl')
    approved_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='posted_obl')
    posted_at = models.DateTimeField(null=True, blank=True)



    def __str__(self):
        return f"{self.account.accountno} - {self.debit} / {self.credit}"

    @property
    def created_by_name(self):
        if self.created_by:
            return self.created_by.get_full_name() or self.created_by.username
        return "System"
        
