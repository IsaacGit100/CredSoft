from django_ledger.models import AccountModel
from djan_led.utils import get_accounts_for_type, add_accounts_to_coa


class COAService:
    def __init__(self, entity):
        self.entity = entity
        self.coa = entity.default_coa

    def ensure_coa_exists(self):
        if not self.coa:
            self.coa = self.entity.create_chart_of_accounts(
                assign_as_default=True, commit=True, coa_name="Default COA"
            )
        return self.coa

    def autofill(self, account_type="general"):
        """Autofill the COA with the selected account type."""
        self.ensure_coa_exists()

        root_assets = AccountModel.objects.get(
            coa_model=self.coa, name="Asset Accounts Root Node"
        )
        root_liabilities = AccountModel.objects.get(
            coa_model=self.coa, name="Liability Accounts Root Node"
        )
        root_capital = AccountModel.objects.get(
            coa_model=self.coa, name="Capital Accounts Root Node"
        )
        root_income = AccountModel.objects.get(
            coa_model=self.coa, name="Income Accounts Root Node"
        )
        root_expenses = AccountModel.objects.get(
            coa_model=self.coa, name="Expense Accounts Root Node"
        )
        root_nodes = (
            root_assets,
            root_liabilities,
            root_capital,
            root_income,
            root_expenses,
        )

        accounts_list = get_accounts_for_type(account_type, root_nodes)
        return add_accounts_to_coa(self.coa, accounts_list)
