from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "code",
            "name",
            "description",
            "purchase_price",
            "selling_price",
            "stock",
            "is_active",
        ]



from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "address"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }
