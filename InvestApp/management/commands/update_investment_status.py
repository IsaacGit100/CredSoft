# management/commands/update_investment_status.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from InvestApp.models import Investment

class Command(BaseCommand):
    help = 'Update investment statuses based on maturity date and interest earned'

    def handle(self, *args, **options):
        today = timezone.now().date()
        investments = Investment.objects.all()

        for inv in investments:
            if inv.status == 'discounted' or inv.status == 'written_off':
                continue  # manual statuses never auto‑changed

            if inv.maturity_date and inv.maturity_date <= today:
                # Matured by date
                if inv.interest_earned and inv.interest_earned > 0:
                    inv.status = 'matured_earned'
                else:
                    inv.status = 'matured_not_earned'
            else:
                inv.status = 'active'
            inv.save()

        self.stdout.write(self.style.SUCCESS("Investment statuses updated"))