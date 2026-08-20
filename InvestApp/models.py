from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from django.db import models
from django.urls import reverse
from django_ledger.models import EntityModel 


class Bank(models.Model):
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, null=True, blank=True, related_name="inv_bank")
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    sort_code = models.CharField(max_length=20, blank=True, null=True)
    bic_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.branch}"

    def get_absolute_url(self):
        return reverse('bank_list')


class Investment(models.Model):
    INVESTMENT_TYPES = [
        ('Savings', 'Savings'),
        ('Fixed Deposit', 'Fixed Deposit'),
        ('T-Bill', 'T-Bill'),
        ('Call Deposit', 'Call Deposit'),
        ('Bonds', 'Bonds'),
        ('Sweep Calls', 'Sweep Calls'),
        ('Other', 'Other'),
    ]

    PERIOD_CHOICES = [
        ('30 day', '30 day'),
        ('91 day', '91 day'),
        ('180 day', '180 day'),
        ('1 year', '1 year'),
        ('2 year', '2 year'),
        ('3 year', '3 year'),
        ('4 year', '4 year'),
        ('5 year', '5 year'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
    ('active', 'Active'),
    ('matured', 'Matured'),
    ('written off', 'Written off')
    ]
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, null=True, blank=True, related_name="inv_inv")
    certificate_no = models.CharField(max_length=50)
    date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    account_no = models.CharField(max_length=50)

    # Bank/Company fields
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, blank=True, null=True)
    other_company = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    term_days = models.IntegerField(blank=True, null=True)
    maturity_date = models.DateField(blank=True, null=True)

    # Investment type
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPES)
    other_investment_type = models.CharField(max_length=100, blank=True, null=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    rollover = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    processed_date = models.DateField(blank=True, null=True)
    # Investment period
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    other_period = models.CharField(max_length=100, blank=True, null=True)
    interest_expected = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    interest_earned = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    interest_earned_date = models.DateField(null=True, blank=True, default=None)

    discounted = models.BooleanField(default=False)
    discounted_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    discounted_date = models.DateField(null=True, blank=True, default=None)

    written_off = models.BooleanField(default=False)
    written_off_date = models.DateField(default=None, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.certificate_no} - {self.get_bank_company_display()}"

    def get_absolute_url(self):
        return reverse('investment_list')

    def get_bank_company_display(self):
        if self.bank:
            return self.bank.name
        return self.other_company

    def get_investment_type_display(self):
        if self.investment_type == 'Other':
            return self.other_investment_type
        return self.investment_type

    def get_period_display(self):
        if self.period == 'Other':
            return self.other_period
        return self.period

    def calculate_interest_expected(self):
        if self.amount and self.rate and self.term_days:
            return (self.amount * self.rate * self.term_days) / (100 * 365)
        return 0

    def save(self, *args, **kwargs):
        self.interest_expected = self.calculate_interest_expected()
        super().save(*args, **kwargs)
