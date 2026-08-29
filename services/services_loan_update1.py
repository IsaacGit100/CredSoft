# services/savings_interest.py
from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction
from MembersApp.models import Master, Sav_Int_Table
from SysSetup.models import SystemSettings
from LoanApp.models import Loan


def get_effective_rate(member, settings):
    """Return the interest rate to use for a member."""
    if member.sav_int_rate and member.sav_int_rate > 0:
        return member.sav_int_rate
    if settings.savings_calc_type == 'Simple_Sav_Interest':
        return settings.simple_sav_interest_rate
    else:
        return settings.minimum_sav_interest_rate

def is_capitalisation_date(today, period):
    if period == 'DAILY':
        return True
    if period == 'MONTHLY':
        # Capitalise on the first day of the next month
        return today.day == 1
    if period == 'QUARTERLY':
        return (today.month, today.day) in [(3,31), (6,30), (9,30), (12,31)]
    if period == 'YEARLY':
        return today.month == 12 and today.day == 31
    return False

def calculate_simple_interest(balance, annual_rate, days):
    """Simple interest = balance * (annual_rate/100) / 365 * days"""
    daily_rate = annual_rate / Decimal('100') / Decimal('365')
    return balance * daily_rate * days

def calculate_minimum_balance_interest(member, annual_rate, days, settings):
    """Minimum balance method: interest = min_balance * rate * days / 365"""
    min_bal = member.sav_min_bal or Decimal('0')
    if min_bal < settings.min_savings_balance:
        return Decimal('0')
    if member.sav_min_bal_days < settings.sav_min_days_int_calc:
        return Decimal('0')
    daily_rate = annual_rate / Decimal('100') / Decimal('365')
    return min_bal * daily_rate * days

def run_daily_interest_accrual(force_date=None):
    """
    Main function to accrue interest for all active members.
    If force_date is given, use that date (for testing). Otherwise use today.
    Returns a summary dict.
    """
    settings = SystemSettings.objects.first()
    if not settings:
        raise Exception("SystemSettings not found")

    today = force_date or date.today()
    calc_type = settings.savings_calc_type
    apply_period = settings.savings_interest_application
    capitalise = is_capitalisation_date(today, apply_period)

    members = Master.objects.filter(is_deleted=False, mem_status='Active')
    processed = 0
    total_interest = Decimal('0')
    capitalised_total = Decimal('0')

    for member in members:
        last_date = member.last_sav_int_accrual_date or member.date_created.date()
        days = (today - last_date).days
        if days <= 0:
            continue

        rate = get_effective_rate(member, settings)
        if rate <= 0:
            continue

        # Calculate interest for the period
        if calc_type == 'Simple_Sav_Interest':
            interest = calculate_simple_interest(member.sav_avail_bal, rate, days)
        else:  # Minimum balance method
            interest = calculate_minimum_balance_interest(member, rate, days, settings)

        if interest <= 0:
            continue

        member.sav_int_accrued = (member.sav_int_accrued or Decimal('0')) + interest
        member.last_sav_int_accrual_date = today
        total_interest += interest

        # If capitalisation day, move accrued to total and reset
        if capitalise:
            member.tot_interest_accrued = (member.tot_interest_accrued or Decimal('0')) + member.sav_int_accrued
            capitalised_total += member.sav_int_accrued
            member.sav_int_accrued = Decimal('0')

        member.save()

        # Optional: log each calculation (can be commented out if too many rows)
        Sav_Int_Table.objects.create(
            master=member,
            sav_avail_bal=member.sav_avail_bal,
            sav_int=interest,
            sav_int_calc_date=today,
            sav_min_bal=member.sav_min_bal,
            sav_min_days=member.sav_min_bal_days,
        )
        processed += 1

    return {
        'processed_members': processed,
        'total_interest_accrued': total_interest,
        'total_capitalised': capitalised_total,
        'date': today,
        'capitalisation_occurred': capitalise,
    }