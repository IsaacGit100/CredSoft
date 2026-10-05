from django.db import models

# Create your models here.
# FinanceApp/models/opening_balance.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_ledger.models import EntityModel, AccountModel

class OpeningBalanceLine(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('POSTED', 'Posted'),
    )

    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="opening_balance_lines")
    account_code = models.ForeignKey("django_ledger.AccountModel", on_delete=models.PROTECT, related_name="opening_balance_lines")

    trans = models.ForeignKey('RecPayApp.Trans', on_delete=models.SET_NULL, null=True, blank=True, related_name='opening_balance_lines')
    account_name = models.CharField(max_length=200, blank=True, default='')
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    date = models.DateField(null=True, blank=True, default=None)
    ledger_entry = models.ForeignKey('FinanceApp.GeneralLedger', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    description = models.CharField(max_length=200, blank=True, default="")
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_obl')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_obl')
    approved_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='posted_obl')
    posted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.account_code.code} - Dr {self.debit_amount} / Cr {self.credit_amount}"

    @property
    def created_by_name(self):
        if self.created_by:
            return self.created_by.get_full_name() or self.created_by.username
        return "System"

#
