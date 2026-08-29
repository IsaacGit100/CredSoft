from django.core.management.base import BaseCommand
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import date
from MembersApp.models import Master
from LoanApp.models import Loan
from FinanceApp.models import FinancialIndicator, GeneralLedger, ChartOfAccounts
from SysSetup.models import SystemSettings

class Command(BaseCommand):
    help = 'Calculate daily financial indicators'

    def handle(self, *args, **options):
        today = date.today()
        self.stdout.write(f"Calculating indicators for {today}...")

        # --- Helper aggregates ---
        members = Master.objects.filter(is_deleted=False)
        active_loans = Loan.objects.filter(status__in=['Active', 'New Loan', 'Owing'])

        # 6. Top 5 Depositors (using tot_deposits)
        top_depositors = members.order_by('-tot_deposits')[:5]
        top_5_depositors = sum(m.tot_deposits or 0 for m in top_depositors)

        # 7. Top 5 Exposures (loan_balance from active loans per member)
        exposures = {}
        for loan in active_loans:
            exposures[loan.master.id] = exposures.get(loan.master.id, 0) + (loan.loan_balance or 0)
        top_exposures = sorted(exposures.values(), reverse=True)[:5]
        top_5_exposures = sum(top_exposures)

        # Total member deposits (liability side)
        total_deposits = members.aggregate(total=Sum('tot_deposits'))['total'] or Decimal('0')

        # Total loan portfolio (outstanding balance)
        total_loans = active_loans.aggregate(total=Sum('loan_balance'))['total'] or Decimal('0')

        # Overdue loans (status 'Owing' or based on next_repayment_date)
        overdue_loans = Loan.objects.filter(
            Q(status='Owing') | Q(next_repayment_date__lt=today)
        )
        total_overdue = overdue_loans.aggregate(total=Sum('loan_balance'))['total'] or Decimal('0')
        par_ratio = (total_overdue / total_loans * 100) if total_loans > 0 else Decimal('0')

        # Loan to Deposit Ratio
        loan_to_deposit = (total_loans / total_deposits * 100) if total_deposits > 0 else Decimal('0')

        # --- System Settings (adjust these in your SysSetup model) ---
        settings = SystemSettings.objects.first()
        net_worth = settings.net_worth if settings and hasattr(settings, 'net_worth') else Decimal('0')
        total_risk_weighted_assets = settings.total_risk_weighted_assets if settings else Decimal('0')
        liquid_assets = settings.liquid_assets if settings else Decimal('0')
        short_term_liabilities = settings.short_term_liabilities if settings else Decimal('0')
        statutory_reserves = settings.statutory_reserves if settings else Decimal('0')
        total_risk_assets = settings.total_risk_assets if settings else Decimal('0')
        marketing_expenses = settings.marketing_expenses if settings else Decimal('0')
        total_assets = settings.total_assets if settings else Decimal('0')
        fixed_assets = settings.fixed_assets if settings else Decimal('0')
        shareholders_equity = settings.shareholders_equity if settings else Decimal('0')
        single_obligor_cap = settings.single_obligor_cap if settings else Decimal('25')  # % of capital

        # Capital Adequacy Ratio
        capital_adequacy = (net_worth / total_risk_weighted_assets * 100) if total_risk_weighted_assets > 0 else Decimal('0')

        # Liquidity Ratio
        liquidity = (liquid_assets / short_term_liabilities * 100) if short_term_liabilities > 0 else Decimal('0')

        # Single Obligor Limit
        max_obligor = max(top_exposures) if top_exposures else Decimal('0')
        single_obligor_limit = (max_obligor / net_worth * 100) if net_worth > 0 else Decimal('0')

        # Primary Cash Reserves
        primary_cash = (statutory_reserves / total_risk_assets * 100) if total_risk_assets > 0 else Decimal('0')

        # Marketing Assets Ratio
        marketing_assets = (marketing_expenses / total_assets * 100) if total_assets > 0 else Decimal('0')

        # Liquid Asset / Deposit Ratio
        liquid_deposit = (liquid_assets / total_deposits * 100) if total_deposits > 0 else Decimal('0')

        # Fixed Assets To Shareholders Funds
        fixed_share = (fixed_assets / shareholders_equity * 100) if shareholders_equity > 0 else Decimal('0')

        # --- Save to database ---
        indicator, created = FinancialIndicator.objects.update_or_create(
            date=today,
            defaults={
                'capital_adequacy_ratio': capital_adequacy,
                'liquidity_ratio': liquidity,
                'single_obligor_limit': single_obligor_limit,
                'primary_cash_reserves': primary_cash,
                'marketing_assets_ratio': marketing_assets,
                'top_5_depositors': top_5_depositors,
                'top_5_exposures': top_5_exposures,
                'liquid_asset_deposit_ratio': liquid_deposit,
                'fixed_assets_shareholders_ratio': fixed_share,
                'par_ratio': par_ratio,
                'loan_to_deposit_ratio': loan_to_deposit,
                'total_assets': total_assets,
                'total_deposits': total_deposits,
                'total_loans': total_loans,
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Indicators saved for {today}"))