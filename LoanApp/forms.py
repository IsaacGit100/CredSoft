from decimal import Decimal

from django import forms

from MembersApp.models import Master
from .models import Loan


class LoanApplicationForm(forms.Form):
    """Loan application form with shortfall/guarantor workflow."""

    member = forms.ModelChoiceField(
        queryset=Master.objects.none(),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_member"}),
        required=True,
        label="Member",
    )

    date_applied = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        required=True,
    )

    principal = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "id": "id_principal"}
        ),
        label="Principal (₵)",
    )

    interest_rate = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal("0.01"),
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "id": "id_interest_rate"}
        ),
        label="Interest Rate (%/month)",
    )

    term_months = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "id": "id_term_months"}
        ),
        initial=12,
        label="Term (months)",
    )

    purpose = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Purpose of the loan"}
        ),
    )

    def __init__(self, *args, entity=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity

        if entity:
            self.fields["member"].queryset = Master.objects.filter(
                entity=entity, is_deleted=False
            ).order_by("last_name", "first_name")
            self.fields["member"].label_from_instance = (
                lambda obj: f"{obj.full_name} (ID {obj.id})"
            )

    def clean(self):
        data = super().clean()
        member = data.get("member")
        principal = data.get("principal")
        term = data.get("term_months")

        if not member or not principal:
            return data

        # Interest rate default chain
        if not data.get("interest_rate"):
            rate = member.loan_int_rate
            if not rate or rate <= 0:
                cfg = getattr(member.entity, "config", None)
                rate = cfg.loan_interest_rate if cfg else Decimal("3.00")
            data["interest_rate"] = rate or Decimal("3.00")

        # Shortfall + guarantor coverage
        shortfall = max(principal - member.available_balance, Decimal("0.00"))
        data["shortfall"] = shortfall

        # Collect guarantor entries from POST
        guarantor_ids = self.data.getlist("guarantor_id")
        guarantor_amounts = self.data.getlist("guarantor_amount")

        guarantors = []
        total_guaranteed = Decimal("0.00")

        for gid, amt in zip(guarantor_ids, guarantor_amounts):
            if not gid or not amt:
                continue
            try:
                amount = Decimal(str(amt))
            except Exception:
                continue
            if amount <= 0:
                continue

            try:
                g = Master.objects.get(id=int(gid), entity=self.entity)
            except Master.DoesNotExist:
                raise forms.ValidationError(f"Guarantor {gid} not found.")

            if amount > g.available_balance:
                raise forms.ValidationError(
                    f"{g.full_name} only has ₵{g.available_balance} available; "
                    f"cannot guarantee ₵{amount}."
                )

            if g.id == member.id:
                raise forms.ValidationError("Member cannot guarantee their own loan.")

            if any(x["member"].id == g.id for x in guarantors):
                raise forms.ValidationError(f"{g.full_name} is listed twice.")

            guarantors.append({"member": g, "amount": amount})
            total_guaranteed += amount

        data["guarantors"] = guarantors
        data["total_guaranteed"] = total_guaranteed

        if total_guaranteed < shortfall:
            raise forms.ValidationError(
                f"Insufficient guarantor coverage. Need ₵{shortfall}, "
                f"have ₵{total_guaranteed}."
            )

        # Require acceptance checkbox
        if not self.data.get("accept_schedule"):
            raise forms.ValidationError(
                "You must review and accept the repayment schedule."
            )

        return data


class LoanEditForm(forms.ModelForm):
    """Edit loan terms — allowed only while status is NEW."""

    class Meta:
        model = Loan
        fields = [
            "principal",
            "interest_rate",
            "term_months",
            "moratorium_months",
            "purpose",
            "date_applied",
            "date_approved",
            "approved_by",
        ]
        widgets = {
            "principal": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "interest_rate": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "term_months": forms.NumberInput(attrs={"class": "form-control"}),
            "moratorium_months": forms.NumberInput(attrs={"class": "form-control"}),
            "purpose": forms.TextInput(attrs={"class": "form-control"}),
            "date_applied": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "date_approved": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "approved_by": forms.TextInput(attrs={"class": "form-control"}),
        }


class LoanRepaymentForm(forms.Form):
    """Loan repayment — pick a loan, split the money, release guarantors."""

    loan = forms.ModelChoiceField(
        queryset=Loan.objects.none(),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_loan"}),
        required=True,
        label="Loan",
    )

    date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Date",
        required=True,
    )

    reference = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Receipt / Voucher No",
            }
        ),
    )

    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "id": "id_amount",
            }
        ),
        label="Total Amount (₵)",
    )

    principal_paid = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "id": "id_principal",
            }
        ),
    )

    interest_paid = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "id": "id_interest",
            }
        ),
    )

    penalty_paid = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "id": "id_penalty",
            }
        ),
    )

    notes = forms.CharField(
        required=False,
        max_length=250,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, entity=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity

        if entity:
            self.fields["loan"].queryset = (
                Loan.objects.filter(entity=entity)
                .exclude(status__in=[Loan.STATUS_COMPLETED, "Completed"])
                .select_related("member")
                .order_by("-date_applied", "-id")
            )
            self.fields["loan"].label_from_instance = (
                lambda obj: f"{obj.loan_no} — {obj.member.full_name} — ₵{obj.balance:,.2f}"
            )
