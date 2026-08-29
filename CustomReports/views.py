from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import datetime
import json


# Import Tables
from MembersApp.models import Master
from RecPayApp.models import Trans
from LoanApp.models import Loan
from coa.models import ChartOfAccounts
from FinanceApp.models import JournalEntry, JournalLine, GeneralLedger 
from InvestApp.models import Bank, Investment
 
# from your_main_app.models import Trans, Master, Loans, ChartOfAccounts
from .models import SavedReport

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def custom_report_builder(request):
    """Main view for building custom reports"""
    
    # Available tables for reporting
    available_tables = [
        {'value': 'trans', 'label': 'Transactions'},
        {'value': 'master', 'label': 'Members'},
        {'value': 'loans', 'label': 'Loans'},
        {'value': 'chartofaccounts', 'label': 'Chart of Accounts'},
    ]
    
    saved_reports = SavedReport.objects.filter(
        created_by=request.user.username if request.user.is_authenticated else ''
    )
    
    if request.method == 'POST':
        if 'generate_pdf' in request.POST or 'generate_excel' in request.POST:
            # Get selected options
            table_name = request.POST.get('table_name')
            selected_fields = request.POST.getlist('selected_fields')
            date_from = request.POST.get('date_from', '')
            date_to = request.POST.get('date_to', '')
            filter_member = request.POST.get('filter_member', '')
            filter_trans_type = request.POST.get('filter_trans_type', '')
            output_type = 'pdf' if 'generate_pdf' in request.POST else 'excel'
            
            # Store in session for export
            request.session['report_data'] = {
                'table_name': table_name,
                'selected_fields': selected_fields,
                'date_from': date_from,
                'date_to': date_to,
                'filter_member': filter_member,
                'filter_trans_type': filter_trans_type,
            }
            
            if output_type == 'pdf':
                return redirect('CustomReports:generate_custom_pdf')
            else:
                return redirect('CustomReports:generate_custom_excel')
        
        elif 'save_report' in request.POST:
            # Save report configuration
            report_name = request.POST.get('report_name')
            table_name = request.POST.get('table_name')
            selected_fields = request.POST.getlist('selected_fields')
            
            SavedReport.objects.create(
                name=report_name,
                table_name=table_name,
                selected_fields=json.dumps(selected_fields),
                created_by=request.user.username if request.user.is_authenticated else 'anonymous'
            )
            messages.success(request, f"Report '{report_name}' saved successfully!")
            return redirect('CustomReports:custom_report_builder')
    
    # GET request - show form
    return render(request, 'CustomReports/custom_report_builder.html', {
        'available_tables': available_tables,
        'saved_reports': saved_reports,
        'members': Master.objects.all(),
    })


@login_required
def get_table_columns1(request):
    """AJAX view to get columns for selected table"""
    table_name = request.GET.get('table')
    
    if not table_name:
        return JsonResponse({'error': 'No table selected'}, status=400)
    
    # Map app names to models - UPDATE THESE WITH YOUR ACTUAL APP NAMES
    table_mapping = {
        'trans': {'model': Trans, 'name': 'Transactions', 'app': 'your_main_app'},
        'master': {'model': Master, 'name': 'Members', 'app': 'your_main_app'},
        'loans': {'model': Loans, 'name': 'Loans', 'app': 'your_main_app'},
        'chartofaccounts': {'model': ChartOfAccounts, 'name': 'Chart of Accounts', 'app': 'your_main_app'},
    }
    
    if table_name not in table_mapping:
        return JsonResponse({'error': 'Invalid table'}, status=400)
    
    model = table_mapping[table_name]['model']
    
    # Get all fields from the model
    fields = []
    for field in model._meta.get_fields():
        # Skip auto-created fields and reverse relations
        if field.auto_created or (hasattr(field, 'one_to_many') and field.one_to_many):
            continue
        
        # Skip certain internal fields
        if field.name in ['created_at', 'updated_at']:
            continue
            
        field_info = {
            'name': field.name,
            'verbose_name': field.verbose_name.title(),
            'type': field.get_internal_type()
        }
        
        # Handle ForeignKey fields
        if field.is_relation:
            field_info['type'] = 'ForeignKey'
            field_info['related_model'] = field.related_model.__name__ if field.related_model else 'Unknown'
        
        fields.append(field_info)
    
    return JsonResponse({
        'fields': fields,
        'table_display': table_mapping[table_name]['name']
    })


@login_required
def generate_custom_pdf2(request):
    """Generate PDF for custom report"""
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa
    import io
    
    report_data = request.session.get('report_data', {})
    
    table_name = report_data.get('table_name')
    selected_fields = report_data.get('selected_fields', [])
    date_from = report_data.get('date_from')
    date_to = report_data.get('date_to')
    filter_member = report_data.get('filter_member')
    filter_trans_type = report_data.get('filter_trans_type')
    
    # Get queryset based on table
    if table_name == 'trans':
        queryset = Trans.objects.select_related('member', 'account').all()
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if filter_member:
            queryset = queryset.filter(member_id=filter_member)
        if filter_trans_type:
            queryset = queryset.filter(trans_type=filter_trans_type)
    
    elif table_name == 'master':
        queryset = Master.objects.all()
    elif table_name == 'loans':
        queryset = Loans.objects.select_related('member').all()
    elif table_name == 'chartofaccounts':
        queryset = ChartOfAccounts.objects.all()
    else:
        queryset = []
    
    # Prepare data for template
    data_rows = []
    for obj in queryset:
        row = {}
        for field in selected_fields:
            value = getattr(obj, field, '-')
            if hasattr(value, 'strftime'):  # Date object
                value = value.strftime('%d/%m/%Y')
            elif isinstance(value, Decimal):
                value = f"{value:,.2f}"
            row[field] = value
        data_rows.append(row)
    
    context = {
        'title': f'Custom Report - {table_name.title()}',
        'headers': selected_fields,
        'data_rows': data_rows,
        'generated_date': datetime.now(),
        'filters_applied': {
            'date_from': date_from,
            'date_to': date_to,
            'member': filter_member,
            'trans_type': filter_trans_type,
        }
    }
    
    html = render_to_string('CustomReports/custom_report_pdf.html', context)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if pdf.err:
        return HttpResponse("Error generating PDF", status=400)
    
    filename = f'custom_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def generate_custom_excel(request):
    """Generate Excel for custom report"""
    import xlsxwriter
    import io
    
    report_data = request.session.get('report_data', {})
    
    table_name = report_data.get('table_name')
    selected_fields = report_data.get('selected_fields', [])
    date_from = report_data.get('date_from')
    date_to = report_data.get('date_to')
    filter_member = report_data.get('filter_member')
    filter_trans_type = report_data.get('filter_trans_type')
    
    # Get queryset (same as PDF generation)
    if table_name == 'trans':
        queryset = Trans.objects.select_related('member', 'account').all()
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if filter_member:
            queryset = queryset.filter(member_id=filter_member)
        if filter_trans_type:
            queryset = queryset.filter(trans_type=filter_trans_type)
    elif table_name == 'master':
        queryset = Master.objects.all()
    elif table_name == 'loans':
        queryset = Loans.objects.select_related('member').all()
    elif table_name == 'chartofaccounts':
        queryset = ChartOfAccounts.objects.all()
    else:
        queryset = []
    
    # Create Excel file
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Report')
    worksheet.set_landscape()
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True, 
        'bg_color': '#2c3e50', 
        'font_color': 'white', 
        'border': 1,
        'align': 'center'
    })
    text_format = workbook.add_format({'border': 1})
    money_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
    date_format = workbook.add_format({'border': 1, 'num_format': 'dd/mm/yyyy'})
    
    # Write headers
    for col, header in enumerate(selected_fields):
        worksheet.write(0, col, header.replace('_', ' ').title(), header_format)
    
    # Write data
    for row, obj in enumerate(queryset, start=1):
        for col, field in enumerate(selected_fields):
            value = getattr(obj, field, '-')
            if hasattr(value, 'strftime'):
                worksheet.write(row, col, value, date_format)
            elif isinstance(value, Decimal):
                worksheet.write(row, col, float(value), money_format)
            else:
                worksheet.write(row, col, str(value), text_format)
    
    # Auto-fit columns
    for col in range(len(selected_fields)):
        worksheet.set_column(col, col, 18)
    
    workbook.close()
    output.seek(0)
    
    filename = f'custom_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def load_saved_report(request, report_id):
    """Load a saved report configuration"""
    report = get_object_or_404(SavedReport, pk=report_id)
    
    return JsonResponse({
        'name': report.name,
        'table_name': report.table_name,
        'selected_fields': json.loads(report.selected_fields),
    })
    
def get_table_columns(request):
    """AJAX view to get columns for selected table"""
    table_name = request.GET.get('table')
    
    print(f"=== get_table_columns called ===")
    print(f"Table name: {table_name}")
    
    if not table_name:
        return JsonResponse({'error': 'No table selected'}, status=400)
    
    # Map app names to models - UPDATE THESE WITH YOUR ACTUAL MODEL PATHS
    try:
        # Try to import your models - adjust these imports
        from MembersApp.models import Master
        from RecPayApp.models import Trans
        from LoanApp.models import Loan
        from coa.models import ChartOfAccounts  # Adjust as needed
    except ImportError as e:
        print(f"Import error: {e}")
        return JsonResponse({'error': f'Import error: {str(e)}'}, status=500)
    
    table_mapping = {
        'trans': {'model': Trans, 'name': 'Transactions'},
        'master': {'model': Master, 'name': 'Members'},
        'loans': {'model': Loan, 'name': 'Loans'},
        'chartofaccounts': {'model': ChartOfAccounts, 'name': 'Chart of Accounts'},
    }
    
    if table_name not in table_mapping:
        return JsonResponse({'error': f'Invalid table: {table_name}'}, status=400)
    
    model = table_mapping[table_name]['model']
    print(f"Model found: {model}")
    
    # Get all fields from the model
    fields = []
    for field in model._meta.get_fields():
        # Skip certain fields
        if field.auto_created:
            continue
        if field.name in ['created_at', 'updated_at', 'id']:
            continue
        
        field_info = {
            'name': field.name,
            'verbose_name': field.name.replace('_', ' ').title(),
            'type': field.get_internal_type()
        }
        fields.append(field_info)
    
    print(f"Found {len(fields)} fields: {[f['name'] for f in fields]}")
    
    return JsonResponse({
        'fields': fields,
        'table_display': table_mapping[table_name]['name']
    })
    
@login_required
def generate_custom_pdf(request):
    """Generate PDF for custom report"""
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa
    import io
    from decimal import Decimal
    
    report_data = request.session.get('report_data', {})
    
    table_name = report_data.get('table_name')
    selected_fields = report_data.get('selected_fields', [])
    date_from = report_data.get('date_from')
    date_to = report_data.get('date_to')
    filter_member = report_data.get('filter_member')
    filter_trans_type = report_data.get('filter_trans_type')
    
    # Import your models - adjust these imports to match your app names
    from MembersApp.models import Master
    from RecPayApp.models import Trans
    from coa.models import ChartOfAccounts
    from LoanApp.models import Loan
    
    # Get queryset based on table
    if table_name == 'trans':
        queryset = Trans.objects.select_related('member', 'account').all()
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if filter_member:
            queryset = queryset.filter(member_id=filter_member)
        if filter_trans_type:
            queryset = queryset.filter(trans_type=filter_trans_type)
    elif table_name == 'master':
        queryset = Master.objects.all()
    elif table_name == 'loans':
        queryset = Loans.objects.select_related('member').all()
    elif table_name == 'chartofaccounts':
        queryset = ChartOfAccounts.objects.all()
    else:
        queryset = []
    
    # Prepare data as list of lists (no dictionary lookups needed)
    data_rows = []
    for obj in queryset:
        row = []
        for field in selected_fields:
            try:
                value = getattr(obj, field, '-')
                if hasattr(value, 'strftime'):
                    value = value.strftime('%d/%m/%Y')
                elif isinstance(value, Decimal):
                    value = f"{value:,.2f}"
                elif value is None:
                    value = '-'
                row.append(str(value))
            except Exception as e:
                row.append('-')
        data_rows.append(row)
    
    context = {
        'title': f'Custom Report - {table_name.title()}',
        'headers': selected_fields,
        'data_rows': data_rows,  # Now a list of lists, not dicts
        'generated_date': datetime.now(),
        'filters_applied': {
            'date_from': date_from,
            'date_to': date_to,
            'member': filter_member,
            'trans_type': filter_trans_type,
        }
    }
    
    html = render_to_string('CustomReports/custom_report_pdf.html', context)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if pdf.err:
        return HttpResponse(f"Error generating PDF: {pdf.err}", status=400)
    
    filename = f'custom_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def generate_custom_pdf3(request):
    """Generate PDF for custom report"""
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa
    import io
    from decimal import Decimal

    report_data = request.session.get('report_data', {})

    table_name = report_data.get('table_name')
    selected_fields = report_data.get('selected_fields', [])
    date_from = report_data.get('date_from')
    date_to = report_data.get('date_to')
    filter_member = report_data.get('filter_member')
    filter_trans_type = report_data.get('filter_trans_type')

    # Import your models - adjust these imports
   
    from LoanApp.models import Loan

    # Get queryset based on table
    if table_name == 'trans':
        queryset = Trans.objects.select_related('member', 'account').all()
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if filter_member:
            queryset = queryset.filter(member_id=filter_member)
        if filter_trans_type:
            queryset = queryset.filter(trans_type=filter_trans_type)
    elif table_name == 'master':
        queryset = Master.objects.all()
    elif table_name == 'loans':
        queryset = Loans.objects.select_related('member').all()
    elif table_name == 'chartofaccounts':
        queryset = ChartOfAccounts.objects.all()
    else:
        queryset = []

    # Prepare data as list of lists (NOT dictionaries)
    data_rows = []
#    for obj in queryset:
#        row = []
#        for field in selected_fields:
#            try:
#                value = getattr(obj, field, '-')
#                if hasattr(value, 'strftime'):  # Date object
#                    value = value.strftime('%d/%m/%Y')
#                elif isinstance(value, Decimal):  # Decimal object
#                    value = f"{value:,.2f}"
#                elif value is None:
#                    value = '-'
#                elif value is True:
#                    value = 'Yes'
#                elif value is False:
#                    value = 'No'
#                row.append(str(value))
#            except Exception as e:
#                row.append('-')
#        data_rows.append(row)
    
    data_rows = []
    for obj in queryset:
        row = []
        for field in selected_fields:
            value = getattr(obj, field, '-')
            if hasattr(value, 'strftime'):
                value = value.strftime('%d/%m/%Y')
            elif value is None:
                value = '-'
            row.append(str(value))
    data_rows.append(row)

    context = {
        'title': f'Custom Report - {table_name.title()}',
        'headers': selected_fields,
        'data_rows': data_rows,  # This is a list of lists
        'generated_date': datetime.now(),
        'filters_applied': {
            'date_from': date_from,
            'date_to': date_to,
            'member': filter_member,
            'trans_type': filter_trans_type,
        }
    }

    html = render_to_string('CustomReports/custom_report_pdf.html', context)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    if pdf.err:
        return HttpResponse(f"Error generating PDF: {pdf.err}", status=400)

    filename = f'custom_report_{datetime.now().strftime("%Y%d%m_%H%M%S")}.pdf'
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
