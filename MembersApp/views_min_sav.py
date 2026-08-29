
from django.utils import timezone
from datetime import date
from django.db import models  # ✅ Add this import

from MembersApp.models import Master
from SysSetup.models import SystemSettings
from MembersApp.models import Sav_Int_Table


from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Avg, Count, Q, Value

from django.contrib import messages
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from datetime import date
from decimal import Decimal

from SysSetup.models import SystemSettings
from MembersApp.models import Master, Sav_Int_Table

@login_required
@staff_member_required
def min_sav_process(request):
    """
    Process savings interest calculation
    This is a VIEW - it must return HttpResponse
    """
    
    # Only allow POST requests for processing
    if request.method == 'POST':
    
        try:
            # Your calculation logic here
            
            result = calculate_savings_interest_logic(request)
            
            if result['success']:
                messages.success(request, result['message'])
            else:
                messages.error(request, result['error'])
                
            return redirect('MembersApp:members_home')  # Change to your actual dashboard URL
            
        except Exception as e:
            messages.error(request, f"Error processing savings interest: {str(e)}")
            return redirect('MembersApp:members_home')
    
    # For GET requests, show confirmation page
    context = {
        'title': 'Process Savings Interest',
        'warning': 'This will calculate interest for all members based on minimum balances.'
    }
    return render(request, 'MembersApp/sav_int_process_confirm.html', context)


def calculate_savings_interest_logic(request):
    """
    Pure business logic - returns dict, not HttpResponse
    """
    sys_set = SystemSettings.objects.first()
    if not sys_set:
        return {'success': False, 'error': 'No system settings found'}
    
    today = date.today()
    last_proc_date = sys_set.last_savings_min_proc_date
    
    if last_proc_date is None:
        last_proc_date = today.replace(day=1)
    
    sav_days = (today - last_proc_date).days
    
    if sav_days <= 0:
        return {
            'success': True,
            'message': f'No days to process. Last processed: {last_proc_date}'
        }
    
    # Get quarter dates
    try:
        quarter_ends = [
            sys_set.first_quarter_end,
            sys_set.second_quarter_end,
            sys_set.third_quarter_end,
            sys_set.fourth_quarter_end
        ]
        is_quarter_end = today in quarter_ends
    except:
        is_quarter_end = False
    
    sys_min_sav_days = sys_set.min_savings_balance_days or 1
    sys_sav_int_rate = sys_set.savings_interest_rate or 0
    daily_interest_rate = Decimal(str(sys_sav_int_rate)) / 100 / 365
    
    masters = Master.objects.filter(is_deleted=False)
    processed_count = 0
    interest_calculated_count = 0
    total_interest = Decimal('0.00')
    
    for master in masters:
        try:
            sav_avail_bal = master.sav_avail_bal or Decimal('0.00')
            sav_min_bal = master.sav_min_bal or Decimal('0.00')
            sav_min_bal_days = master.sav_min_bal_days or 0
            sav_int_accr = master.sav_int_accrued or Decimal('0.00')
            
            # Track minimum balance
            if sav_min_bal == 0  and sav_avail_bal > 0:
                new_min_bal = sav_avail_bal
                
            
            if sav_avail_bal < sav_min_bal:
                new_min_bal = sav_avail_bal
            #    new_min_days = sav_days
            
                
            if sav_avail_bal <= 0:
                new_min_days = 0
            else:    
                new_min_days = sav_min_bal_days + sav_days
            
            # Calculate interest if quarter end
            sav_int = Decimal('0.00')
            int_calc_date = None
            
            if is_quarter_end and new_min_days >= sys_min_sav_days and new_min_bal > 0:
                quarter_days = 90
                interest_amount = new_min_bal * daily_interest_rate * quarter_days
                sav_int = interest_amount.quantize(Decimal('0.01'))
                int_calc_date = today
                sav_int_accr += sav_int
                total_interest += sav_int
                new_min_days = 0
                interest_calculated_count += 1
                
                new_min_bal = sav_avail_bal
                
            # Update master
            master.sav_min_bal = new_min_bal
            master.sav_min_bal_days = new_min_days
            master.sav_int_accrued = sav_int_accr
            master.save()
            
            # Create audit record
            Sav_Int_Table.objects.create(
                min_date=last_proc_date,
                master=master,
                sav_avail_bal=sav_avail_bal,
                sav_min_bal=new_min_bal,
                sav_min_days=sav_days,
                sav_int=sav_int,
                last_min_date=last_proc_date,
                sav_int_calc_date=int_calc_date
            )
            
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing member {master.id}: {e}")
            continue
    
    # Update system settings
    sys_set.last_savings_min_proc_date = today
    sys_set.save()
    
    return {
        'success': True,
        'message': f'Processed {processed_count} members. Interest calculated for {interest_calculated_count} members. Total interest: ₵{total_interest:,.2f}',
        'members_processed': processed_count,
        'interest_calculated': interest_calculated_count,
        'total_interest': total_interest
    }






# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import date
from decimal import Decimal

@staff_member_required
def process_savings_interest(request):
    """
    View for savings interest processing
    """
    from SysSetup.models import SystemSettings
    from MembersApp.models import Master
    
    settings = SystemSettings.objects.first()
    
    if request.method == 'POST':
        # Call your processing function
        result = min_sav_process(request)
        
        if result:
            messages.success(request, "Savings interest calculated successfully!")
        else:
            messages.error(request, "Error calculating savings interest!")
        
        return redirect('MembersApp:members_home')  # Change to your actual dashboard URL
    
    # GET request - show dashboard
    context = {
        'settings': settings,
        'total_members': Master.objects.filter(is_deleted=False).count(),
        'members_with_savings': Master.objects.filter(
            is_deleted=False
        ).count(),
        'total_savings_balance': Master.objects.with_sav_avail_bal().aggregate(Sum('sav_avail_bal')),
        'total_interest_accrued': Master.objects.filter(is_deleted=False).aggregate(total=models.Sum('tot_interest_accrued'))['total'] or Decimal('0.00'),
        'now': timezone.now()
    }
    
    return render(request, 'MembersApp/savings_dashboard.html', context)



def savings_dashboard(request):
    settings = SystemSettings.objects.first()
    
    # Get statistics using your manager
    total_balance = Master.objects.get_total_balance()
    members_with_savings = Master.objects.with_positive_balance().count()
    total_interest = Master.objects.aggregate(total=Sum('tot_interest_accrued'))['total'] or 0
    
    context = {
        'settings': settings,
        'total_members': Master.objects.filter(is_deleted=False).count(),
        'members_with_savings': members_with_savings,
        'total_savings_balance': total_balance,
        'total_interest_accrued': total_interest,
        'recent_processing': [],  # Add if you have processing history
    }
    
    if request.method == 'POST':
        result = min_sav_process(request)
        if result:
            messages.success(request, "Savings interest calculated successfully!")
        else:
            messages.error(request, "Error calculating savings interest!")
        return redirect('savings_dashboard')
    
    return render(request, 'MembersApp/savings_dashboard.html', context)
    


def sav_int_process_list(request):
#    savings = Sav_Int_Table.objects.order_by('id')
#    masters = Master.objects.filter(is_deleted=False)
    savings = Sav_Int_Table.objects.select_related('master').order_by('-sav_int_calc_date')
    
    
    context = {
        'savings': savings,
    }
    
    return render(request, 'MembersApp/sav_int_process_list.html', context)


def calculate_savings_interest_logic1(request):
    """
    Pure business logic - returns dict, not HttpResponse
    """
    sys_set = SystemSettings.objects.first()
    if not sys_set:
        return {'success': False, 'error': 'No system settings found'}
    
    today = date.today()
    last_proc_date = sys_set.last_savings_min_proc_date
    
    if last_proc_date is None:
        last_proc_date = today.replace(day=1)
    
    sav_days = (today - last_proc_date).days
    
    if sav_days <= 0:
        return {
            'success': True,
            'message': f'No days to process. Last processed: {last_proc_date}'
        }
    
    # Get quarter dates
    try:
        quarter_ends = [
            sys_set.first_quarter_end,
            sys_set.second_quarter_end,
            sys_set.third_quarter_end,
            sys_set.fourth_quarter_end
        ]
        is_quarter_end = today in quarter_ends
    except:
        is_quarter_end = False
    
    sys_min_sav_days = sys_set.min_savings_balance_days or 1
    sys_sav_int_rate = sys_set.savings_interest_rate or 0
    daily_interest_rate = Decimal(str(sys_sav_int_rate)) / 100 / 365
    
    masters = Master.objects.filter(is_deleted=False)
    processed_count = 0
    interest_calculated_count = 0
    total_interest = Decimal('0.00')
    
    for master in masters:
        try:
            sav_avail_bal = master.sav_avail_bal or Decimal('0.00')
            sav_min_bal = master.sav_min_bal or Decimal('0.00')
            sav_min_bal_days = master.sav_min_bal_days or 0
            sav_int_accr = master.sav_int_accrued or Decimal('0.00')
            
            # Track minimum balance
            if sav_avail_bal < sav_min_bal or sav_min_bal == 0:
                new_min_bal = sav_avail_bal
                new_min_days = sav_days
                
            elif sav_avail_bal == 0:
                sav_daysnew_min_days = 0
            
            else:
                new_min_bal = sav_min_bal
                
            if sav_avail_bal <= 0:
                new_min_days = 0
            else:    
                new_min_days = sav_min_bal_days + sav_days
            
            # Calculate interest if quarter end
            sav_int = Decimal('0.00')
            int_calc_date = None
            
            if is_quarter_end and new_min_days >= sys_min_sav_days and new_min_bal > 0:
                quarter_days = 90
                interest_amount = new_min_bal * daily_interest_rate * quarter_days
                sav_int = interest_amount.quantize(Decimal('0.01'))
                int_calc_date = today
                sav_int_accr += sav_int
                total_interest += sav_int
                new_min_days = 0
                interest_calculated_count += 1
            
            # Update master
            master.sav_min_bal = new_min_bal
            master.sav_min_bal_days = new_min_days
            master.sav_int_accrued = sav_int_accr
            master.save()
            
            # Create audit record
            Sav_Int_Table.objects.create(
                min_date=last_proc_date,
                master=master,
                sav_avail_bal=sav_avail_bal,
                sav_min_bal=new_min_bal,
                sav_min_days=sav_days,
                sav_int=sav_int,
                last_min_date=last_proc_date,
                sav_int_calc_date=int_calc_date
            )
            
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing member {master.id}: {e}")
            continue
    
    # Update system settings
    sys_set.last_savings_min_proc_date = today
    sys_set.save()
    
    return {
        'success': True,
        'message': f'Processed {processed_count} members. Interest calculated for {interest_calculated_count} members. Total interest: ₵{total_interest:,.2f}',
        'members_processed': processed_count,
        'interest_calculated': interest_calculated_count,
        'total_interest': total_interest
    }
