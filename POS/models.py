from django.db import models

# Create your models here.
from django.db import models
from django_ledger.models import EntityModel
from django.contrib.auth.models import User


class Customer(models.Model):
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="pos_customers"
    )
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True, default='')
    email = models.EmailField(blank=True, null=True, default='')
    address = models.TextField(blank=True, null=True, default='')
    tot_receipts = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    tot_payments = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    cnt_receipts = models.IntegerField(null=True, blank=True, default=0)
    cnt_payments = models.IntegerField(null=True, blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="pos_products"
    )
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, default='')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Sale(models.Model):
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="pos_sales"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    sale_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    payment_method = models.CharField(
        max_length=20,
        choices=[("Cash", "Cash"), ("Cheque", "Cheque"), ("Mobile", "Mobile Money")],
        default="Cash")
    
    payment_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default="Completed")  # Completed, Voided
    posted_to_ledger = models.BooleanField(default=False)
    journal_entry_id = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    #created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=None)

    def __str__(self):
        return f"Sale #{self.id} - {self.sale_date}"


class SaleLine(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Payment(models.Model):
    PAYMENT_METHODS = (
        ("Cash", "Cash"),
        ("Momo", "Mobile Money"),
        ("Cheque", "Cheque"),
        ("Credit", "Credit"),
    )
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="pos_payments"
    )
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="payments")
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="Cash")
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    momo_name = models.CharField(max_length=100, blank=True)
    momo_no = models.CharField(max_length=20, blank=True)
    cheque_no = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    posted_to_ledger = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment #{self.id} - {self.method} - {self.amount}"
