from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from openpyxl import Workbook
from io import BytesIO

from MembersApp.models import Master
from RecPayApp.models import Trans
from SysSetup.models import SystemSettings
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date


@staff_member_required
def dividend_appropriation_preview(request):
    """Show form to enter dividend amount, preview list of members and calculated dividends."""
    total_shares = Master.objects.filter(is_deleted=False).aggregate(total=Sum('tot_shares'))['total'] or Decimal('0')
    dividend_amount = None
    per_share = Decimal('0')
    members_with_dividends = []
    total_dividend = Decimal('0')
    
    dividend_period = ''
    
    dividend_date = date.today()
    
   
    if request.method == 'POST':
        dividend_period = request.POST.get('dividend_period')
        
     ## Amount Inputs from Template Converted ================================   
        raw_amount = request.POST.get('dividend_amount', '')   # "1,234.56"
        clean_amount = raw_amount.replace(',', '')
    #    dividend_amount = Decimal(clean_amount)
        
        try:
            dividend_amount = Decimal(clean_amount)
        except:
            dividend_amount = Decimal('0')      
    ## =======================================================================  
     ## Date Format 
        raw_date = request.POST.get('dividend_date', '')
        date_obj = datetime.strptime(raw_date, '%d/%m/%Y').date()
        dividend_date=date_obj
    ## =======================================================================
        
        if dividend_amount <= 0:
            messages.error(request, "Dividend amount must be greater than zero.")
            return redirect('Supervisor:dividend_appropriation_preview')

        if total_shares == 0:
            messages.error(request, "No shares found among members.")
            return redirect('Supervisor:dividend_appropriation_preview')

        per_share = dividend_amount / total_shares

        # Get all active members with shares > 0
        members = Master.objects.filter(is_deleted=False, tot_shares__gt=0).order_by('last_name', 'first_name')
        running_total = Decimal('0')
        for m in members:
            dividend = (per_share * m.tot_shares).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            running_total += dividend
            members_with_dividends.append({
                'member': m,
                'shares': m.tot_shares,
                'dividend': dividend,
            })
        total_dividend = running_total

        # Store data in session for the appropriation step
        request.session['dividend_appropriation'] = {
            'dividend_amount': str(dividend_amount),
            'total_shares': str(total_shares),
            'per_share': str(per_share),
            'members_data': [(m.id, float(d['dividend'])) for m, d in zip(members, members_with_dividends)],
            'total_dividend': str(total_dividend),
            'dividend_period': str(dividend_period),
            'dividend_date': str(dividend_date),
        }
        context = {
            'dividend_amount': dividend_amount,
            'total_shares': total_shares,
            'per_share': per_share,
            'members': members_with_dividends,
            'total_dividend': total_dividend,
            'preview': True,
            'dividend_period': dividend_period,
            'dividend_date': dividend_date,
        }
        return render(request, 'Supervisor/dividend_appropriation.html', context)

    # GET request – show form only
    context = {
        'total_shares': total_shares,
        'preview': False,
    }
    return render(request, 'Supervisor/dividend_appropriation.html', context)

@staff_member_required
@transaction.atomic
def dividend_appropriation_execute(request):
    """Create Trans records and then show confirmation report."""
    if request.method != 'POST':
        return redirect('Supervisor:dividend_appropriation_preview')

    data = request.session.get('dividend_appropriation')
    if not data:
        messages.error(request, "No dividend appropriation data found. Please start over.")
        return redirect('Supervisor:dividend_appropriation_preview')

    dividend_amount = Decimal(data['dividend_amount'])
    total_shares = Decimal(data['total_shares'])
    per_share = Decimal(data['per_share'])
    members_data = data['members_data']
    total_dividend = Decimal(data['total_dividend'])
    dividend_period = data['dividend_period']
    dividend_date = data['dividend_date']
    
    # Get the ledger account for dividend appropriation (expense)
    from coa.models import ChartOfAccounts
    try:
        dividend_account = ChartOfAccounts.objects.get(accountno='50103000')  # adjust to your actual code
        ledger_id = dividend_account.id
        
    except ChartOfAccounts.DoesNotExist:
        messages.error(request, "Dividend expense account (50103000) not found in Chart of Accounts.")
        return redirect('Supervisor:dividend_appropriation_preview')

    # Get a batch number
    from datetime import datetime
    batch_number = f"DIV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    created_transactions = []
    for member_id, div_amt in members_data:
        member = Master.objects.get(id=member_id)
        div_amt = Decimal(str(div_amt)).quantize(Decimal('0.01'))
        if div_amt <= 0:
            continue
        trans = Trans.objects.create(
            rec_vou_no=f"{batch_number}-{member_id}",
            trans_no=f"{batch_number}-{member_id}",
            date=timezone.now().date(),
            trans_type='Receipts',
            amount=div_amt,
            pay_mode='Transfer',
            member=member,
            member_no=member.id,
            member_name=member.full_name,
            ledger_id=ledger_id,
            ledger_code=dividend_account.accountno,
            ledger_name='Dividend',
            purpose='Dividend Appropriation',
            details=f'Dividend for {dividend_period} based on {member.tot_shares} shares',
            batch_number=batch_number,
            status='DRAFT',
            created_by=request.user,
        )
        created_transactions.append({
            'member': member,
            'dividend': div_amt,
            'dividend_period': dividend_period,
            'dividend_date': dividend_date,
        })

    # Save the dividend amount in SystemSettings
    settings = SystemSettings.objects.first()
    if settings:
        settings.dividend_amount = dividend_amount # This is giving me error ["“(Decimal('21500'),)” value must be a decimal number."]
        settings.dividend_date = dividend_date     # This is giving me error too
        settings.dividend_period = dividend_period 
        settings.save()

    # Clear session data
    del request.session['dividend_appropriation']

    # Prepare context for confirmation report
    context = {
        'batch_number': batch_number,
        'total_members': len(created_transactions),
        'total_dividend': total_dividend,
        'dividend_amount': dividend_amount,
        'total_shares': total_shares,
        'per_share': per_share,
        'transactions': created_transactions,
        'created_at': timezone.now(),
    }
    return render(request, 'Supervisor/dividend_appropriation_confirmation.html', context)





def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if pdf.err:
        return None
    return result.getvalue()


@staff_member_required
def dividend_appropriation_pdf(request):
    """Export the preview list as PDF."""
    data = request.session.get('dividend_appropriation')
    if not data:
        messages.error(request, "No dividend data found. Please preview first.")
        return redirect('Supervisor:dividend_appropriation_preview')
    total_shares = Decimal(data['total_shares'])
    per_share = Decimal(data['per_share'])
    members_data = data['members_data']
    total_dividend = Decimal(data['total_dividend'])
    dividend_amount = Decimal(data['dividend_amount'])

    # Rebuild member list
    members = []
    for member_id, div_amt in members_data:
        member = Master.objects.get(id=member_id)
        members.append({
            'member': member,
            'shares': member.tot_shares,
            'dividend': Decimal(str(div_amt)),
        })

    context = {
        'dividend_amount': dividend_amount,
        'total_shares': total_shares,
        'per_share': per_share,
        'members': members,
        'total_dividend': total_dividend,
        'date': timezone.now(),
    }
    pdf = render_to_pdf('Supervisor/dividend_appropriation_pdf.html', context)
    if pdf is None:
        return HttpResponse("Error generating PDF", status=500)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dividend_appropriation.pdf"'
    return response


@staff_member_required
def dividend_appropriation_excel(request):
    """Export the preview list as Excel."""
    data = request.session.get('dividend_appropriation')
    if not data:
        messages.error(request, "No dividend data found. Please preview first.")
        return redirect('Supervisor:dividend_appropriation_preview')
    members_data = data['members_data']
    total_shares = Decimal(data['total_shares'])
    per_share = Decimal(data['per_share'])
    total_dividend = Decimal(data['total_dividend'])
    dividend_amount = Decimal(data['dividend_amount'])

    wb = Workbook()
    ws = wb.active
    ws.title = "Dividend Appropriation"
    ws.append(['Member Name', 'Number of Shares', 'Dividend (₵)'])
    for member_id, div_amt in members_data:
        member = Master.objects.get(id=member_id)
        ws.append([member.full_name, float(member.tot_shares or 0), float(div_amt)])
    ws.append([])
    ws.append(['Total Shares', float(total_shares), ''])
    ws.append(['Dividend Amount (₵)', float(dividend_amount), ''])
    ws.append(['Dividend per Share (₵)', float(per_share), ''])
    ws.append(['Total Dividend Paid', float(total_dividend), ''])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="dividend_appropriation.xlsx"'
    wb.save(response)
    return response


