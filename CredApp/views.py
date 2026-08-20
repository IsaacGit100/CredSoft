from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_ledger.models import EntityModel
from MembersApp.models import Master

# Create your views here.


def members_home(request, slug):
    pass


@login_required
def member_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    query = request.GET.get('q', '')

    members = Master.objects.all()

    if query:
        members = members.filter(
            Q(full_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(telephone1__icontains=query) |
            Q(email_address__icontains=query)
        )

    # Pagination
    paginator = Paginator(members, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'members': page_obj,
        'record_count': members.count(),
        'query': query,
    }
    return render(request, 'CredApp/member_list_manage.html', context)


@login_required
def member_create(request, slug):
    """Create new member with NOK percentage validation"""
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == 'POST':
        form = MasterForm(request.POST)

        if form.is_valid():
            try:
                # Save the form
                instance = form.save()

                # Get NOK percentages for verification
                percent1 = form.cleaned_data.get('nok_percent1', 0) or 0
                percent2 = form.cleaned_data.get('nok_percent2', 0) or 0
                percent3 = form.cleaned_data.get('nok_percent3', 0) or 0
                total_percent = percent1 + percent2 + percent3

                # Success message with percentage info
                if total_percent == 100:
                    messages.success(
                        request, 
                        f' Member {instance.full_name} created successfully! '
                        f'NOK distribution: {percent1}% / {percent2}% / {percent3}%'
                    )
                else:
                    messages.success(
                        request, 
                        f' Member {instance.full_name} created successfully!'
                    )

                return redirect('CredApp:member_list_manage')

            except Exception as e:
                messages.error(request, f'Error creating member: {str(e)}')
                return render(request, 'CredApp/member_create.html', {'form': form})
        else:
            # Form has errors - display them
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    else:
        form = MasterForm()

    context = {
        'form': form,
        'title': 'Create New Member',
        'submit_text': 'Save Member',
        'cancel_url': 'CredApp:member_list_manage',
    }

    return render(request, 'CredApp/member_create.html', context)


@login_required
def member_edit(request, pk, slug):
    """Edit existing member"""
    member = get_object_or_404(Master, pk=pk)
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == 'POST':
        form = MasterForm(request.POST, instance=member)

        if form.is_valid():
            try:
                instance = form.save()

                # Get NOK percentages for verification
                percent1 = form.cleaned_data.get('nok_percent1', 0) or 0
                percent2 = form.cleaned_data.get('nok_percent2', 0) or 0
                percent3 = form.cleaned_data.get('nok_percent3', 0) or 0
                total_percent = percent1 + percent2 + percent3

                if total_percent == 100:
                    messages.success(
                        request, 
                        f' Member {instance.full_name} updated successfully! '
                        f'NOK distribution: {percent1}% / {percent2}% / {percent3}%'
                    )
                else:
                    messages.success(request, f' Member {instance.full_name} updated successfully!')

                return redirect('CredApp:member_view', pk=member.id)

            except Exception as e:
                messages.error(request, f'Error updating member: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MasterForm(instance=member)

    context = {
        'form': form,
        'member': member,
        'title': f'Edit Member: {member.full_name}',
        'submit_text': 'Update Member',
        'cancel_url': 'members:member_view',
        'cancel_id': member.id,
    }

    return render(request, 'CredApp/member_create.html', context)

@login_required
def member_view(request, pk, slug):
    """View detailed member information"""
    member = get_object_or_404(Master, pk=pk)
    entity = get_object_or_404(EntityModel, slug=slug)

    # Calculate age
    age = None
    if member.date_of_birth:
        today = datetime.now().date()
        age = today.year - member.date_of_birth.year - (
            (today.month, today.day) < (member.date_of_birth.month, member.date_of_birth.day)
        )

    context = {
        'member': member,
        'age': age,
        'total_guaranteed': member.tot_guaranteed,
        'total_guaranted': member.tot_guaranted,
        'total_loans': member.tot_loans,
        'total_deposits': member.tot_deposits,
        'total_shares': member.tot_shares,
    }
    return render(request, 'CredApp/member_view.html', context)


@login_required
def member_pdf(request, pk, slug):
    """Generate PDF for a single member"""
    member = get_object_or_404(Master, pk=pk)
    entity = get_object_or_404(EntityModel, slug=slug)

    # Calculate age
    age = None
    if member.date_of_birth:
        today = datetime.now().date()
        age = today.year - member.date_of_birth.year - (
            (today.month, today.day) < (member.date_of_birth.month, member.date_of_birth.day)
        )

    # Create buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)

    elements = []

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.black
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=10,
        textColor=colors.black
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        spaceBefore=2,
        spaceAfter=2,
        textColor=colors.black
    )

    # Title
    elements.append(Paragraph("ST. ANDREWS CO-OPERATIVE CREDIT UNION", title_style))
    elements.append(Paragraph("MEMBER INFORMATION", heading_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Member ID and Date
    elements.append(Paragraph(f"<b>Member ID:</b> {member.id}", normal_style))
    elements.append(Paragraph(f"<b>Date Enrolled:</b> {member.date_enrolled.strftime('%d/%m/%Y') if member.date_enrolled else 'N/A'}", normal_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Personal Information Table
    elements.append(Paragraph("PERSONAL INFORMATION", heading_style))

    personal_data = [
        ['Full Name:', member.full_name or f"{member.first_name} {member.last_name}"],
        ['Title:', member.title or '-'],
        ['First Name:', member.first_name or '-'],
        ['Last Name:', member.last_name or '-'],
        ['Other Names:', member.other_names or '-'],
        ['Date of Birth:', member.date_of_birth.strftime('%d/%m/%Y') if member.date_of_birth else '-'],
        ['Age:', str(age) if age else '-'],
        ['Gender:', member.gender or '-'],
        ['Marital Status:', member.marital_status or '-'],
        ['Church Member:', member.church_member or '-'],
        ['Profession:', member.profession or '-'],
        ['Status:', member.mem_status or '-'],
    #    ['Loan Status:', member.loan_status or '-'],
        ['Role:', member.role or '-'],
    ]

    personal_table = Table(personal_data, colWidths=[1.5*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(personal_table)
    elements.append(Spacer(1, 0.15 * inch))

    # Contact Information
    elements.append(Paragraph("CONTACT INFORMATION", heading_style))

    contact_data = [
        ['Phone 1:', member.telephone1 or '-'],
        ['Phone 2:', member.telephone2 or '-'],
        ['Email:', member.email_address or '-'],
        ['Residential Address:', member.residential_address or '-'],
        ['Postal Address:', member.postal_address or '-'],
        ['City:', member.city or '-'],
        ['Near Landmark:', member.near_landmark or '-'],
        ['Street Name:', member.street_name or '-'],
        ['GPS Address:', member.gps or '-'],
    ]

    contact_table = Table(contact_data, colWidths=[1.5*inch, 4*inch])
    contact_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(contact_table)
    elements.append(Spacer(1, 0.15 * inch))

    # Next of Kin Information
    elements.append(Paragraph("NEXT OF KIN INFORMATION", heading_style))

    nok_data = []
    if member.nok_name1:
        nok_data.append(['NOK 1:', f"{member.nok_name1} ({member.nok_relation1}) - {member.nok_telephone1}"])
        if member.nok_address1:
            nok_data.append(['', member.nok_address1])
        if member.nok_gps1:
            nok_data.append(['', f"GPS: {member.nok_gps1}"])
        if member.nok_percent1:
            nok_data.append(['', f"Share: {member.nok_percent1}%"])

    if member.nok_name2:
        nok_data.append(['NOK 2:', f"{member.nok_name2} ({member.nok_relation2}) - {member.nok_telephone2}"])
        if member.nok_address2:
            nok_data.append(['', member.nok_address2])
        if member.nok_gps2:
            nok_data.append(['', f"GPS: {member.nok_gps2}"])
        if member.nok_percent2:
            nok_data.append(['', f"Share: {member.nok_percent2}%"])

    if member.nok_name3:
        nok_data.append(['NOK 3:', f"{member.nok_name3} ({member.nok_relation3}) - {member.nok_telephone3}"])
        if member.nok_address3:
            nok_data.append(['', member.nok_address3])
        if member.nok_gps3:
            nok_data.append(['', f"GPS: {member.nok_gps3}"])
        if member.nok_percent3:
            nok_data.append(['', f"Share: {member.nok_percent3}%"])

    if not nok_data:
        nok_data = [['No Next of Kin information available', '']]

    nok_table = Table(nok_data, colWidths=[1.5*inch, 4*inch])
    nok_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(nok_table)
    elements.append(Spacer(1, 0.15 * inch))

    # Financial Summary
    elements.append(Paragraph("FINANCIAL SUMMARY", heading_style))

    financial_data = [
        ['Total Deposits:', f"₵{member.tot_deposits:,.2f}"],
        ['Total Shares:', f"₵{member.tot_shares:,.2f}"],
        ['Total Loans:', f"₵{member.tot_loans:,.2f}"],
        ['Guaranteed FOR Member:', f"₵{member.tot_guaranteed:,.2f}"],
        ['Member Guarantees FOR Others:', f"₵{member.tot_guaranted:,.2f}"],
    ]

    financial_table = Table(financial_data, colWidths=[2*inch, 3.5*inch])
    financial_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(financial_table)
    elements.append(Spacer(1, 0.15 * inch))

    # Footer
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("-" * 70, normal_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    elements.append(Paragraph(f"Member ID: {member.id}", normal_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"member_{member.id}_{member.last_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
def member_excel(request, pk, slug):
    """Generate Excel for a single member"""
    member = get_object_or_404(Master, pk=pk)
    entity = get_object_or_404(EntityModel, slug=slug)

    # Calculate age
    age = None
    if member.date_of_birth:
        today = datetime.now().date()
        age = today.year - member.date_of_birth.year - (
            (today.month, today.day) < (member.date_of_birth.month, member.date_of_birth.day)
        )

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Member_{member.id}"

    # Styles
    header_font = Font(bold=True, size=12)
    bold_font = Font(bold=True)
    center_align = Alignment(horizontal="center")
    left_align = Alignment(horizontal="left")
    right_align = Alignment(horizontal="right")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    current_row = 1

    # Title
    ws.merge_cells(f'A{current_row}:C{current_row}')
    ws[f'A{current_row}'] = "ST. ANDREWS CO-OPERATIVE CREDIT UNION"
    ws[f'A{current_row}'].font = Font(bold=True, size=14)
    ws[f'A{current_row}'].alignment = center_align
    current_row += 1

    ws.merge_cells(f'A{current_row}:C{current_row}')
    ws[f'A{current_row}'] = "MEMBER INFORMATION"
    ws[f'A{current_row}'].font = Font(bold=True, size=12)
    ws[f'A{current_row}'].alignment = center_align
    current_row += 2

    # Member ID and Date
    ws[f'A{current_row}'] = "Member ID:"
    ws[f'B{current_row}'] = member.id
    ws[f'A{current_row}'].font = bold_font
    current_row += 1

    ws[f'A{current_row}'] = "Date Enrolled:"
    ws[f'B{current_row}'] = member.date_enrolled.strftime('%d/%m/%Y') if member.date_enrolled else '-'
    ws[f'A{current_row}'].font = bold_font
    current_row += 2

    # Personal Information
    ws.merge_cells(f'A{current_row}:C{current_row}')
    ws[f'A{current_row}'] = "PERSONAL INFORMATION"
    ws[f'A{current_row}'].font = bold_font
    current_row += 1

    personal_data = [
        ('Full Name:', member.full_name or f"{member.first_name} {member.last_name}"),
        ('Title:', member.title or '-'),
        ('First Name:', member.first_name or '-'),
        ('Last Name:', member.last_name or '-'),
        ('Other Names:', member.other_names or '-'),
        ('Date of Birth:', member.date_of_birth.strftime('%d/%m/%Y') if member.date_of_birth else '-'),
        ('Age:', str(age) if age else '-'),
        ('Gender:', member.gender or '-'),
        ('Marital Status:', member.marital_status or '-'),
        ('Church Member:', member.church_member or '-'),
        ('Profession:', member.profession or '-'),
        ('Status:', member.mem_status or '-'),
    #    ('Loan Status:', member.loan_status or '-'),
        ('Role:', member.role or '-'),
    ]

    for label, value in personal_data:
        ws.cell(row=current_row, column=1, value=label).font = bold_font
        ws.cell(row=current_row, column=2, value=value)
        current_row += 1

    current_row += 1

    # Contact Information
    ws.merge_cells(f'A{current_row}:C{current_row}')
    ws[f'A{current_row}'] = "CONTACT INFORMATION"
    ws[f'A{current_row}'].font = bold_font
    current_row += 1

    contact_data = [
        ('Phone 1:', member.telephone1 or '-'),
        ('Phone 2:', member.telephone2 or '-'),
        ('Email:', member.email_address or '-'),
        ('Residential Address:', member.residential_address or '-'),
        ('Postal Address:', member.postal_address or '-'),
        ('City:', member.city or '-'),
        ('Near Landmark:', member.near_landmark or '-'),
        ('Street Name:', member.street_name or '-'),
        ('GPS Address:', member.gps or '-'),
    ]

    for label, value in contact_data:
        ws.cell(row=current_row, column=1, value=label).font = bold_font
        ws.cell(row=current_row, column=2, value=value)
        current_row += 1

    current_row += 1

    # Next of Kin Information
    ws.merge_cells(f'A{current_row}:C{current_row}')
    ws[f'A{current_row}'] = "NEXT OF KIN INFORMATION"
    ws[f'A{current_row}'].font = bold_font
    current_row += 1

    if member.nok_name1:
        ws.cell(row=current_row, column=1, value="NOK 1:").font = bold_font
        ws.cell(row=current_row, column=2, value=f"{member.nok_name1} ({member.nok_relation1}) - {member.nok_telephone1}")
        current_row += 1
        if member.nok_address1:
            ws.cell(row=current_row, column=2, value=member.nok_address1)
            current_row += 1
        if member.nok_gps1:
            ws.cell(row=current_row, column=2, value=f"GPS: {member.nok_gps1}")
            current_row += 1
        if member.nok_percent1:
            ws.cell(row=current_row, column=2, value=f"Share: {member.nok_percent1}%")
            current_row += 1

    if member.nok_name2:
        ws.cell(row=current_row, column=1, value="NOK 2:").font = bold_font
        ws.cell(row=current_row, column=2, value=f"{member.nok_name2} ({member.nok_relation2}) - {member.nok_telephone2}")
        current_row += 1
        if member.nok_address2:
            ws.cell(row=current_row, column=2, value=member.nok_address2)
            current_row += 1
        if member.nok_gps2:
            ws.cell(row=current_row, column=2, value=f"GPS: {member.nok_gps2}")
            current_row += 1
        if member.nok_percent2:
            ws.cell(row=current_row, column=2, value=f"Share: {member.nok_percent2}%")
            current_row += 1

    if member.nok_name3:
        ws.cell(row=current_row, column=1, value="NOK 3:").font = bold_font
        ws.cell(row=current_row, column=2, value=f"{member.nok_name3} ({member.nok_relation3}) - {member.nok_telephone3}")
        current_row += 1
        if member.nok_address3:
            ws.cell(row=current_row, column=2, value=member.nok_address3)
            current_row += 1
        if member.nok_gps3:
            ws.cell(row=current_row, column=2, value=f"GPS: {member.nok_gps3}")
            current_row += 1
        if member.nok_percent3:
            ws.cell(row=current_row, column=2, value=f"Share: {member.nok_percent3}%")
            current_row += 1

    if not member.nok_name1 and not member.nok_name2 and not member.nok_name3:
        ws.cell(row=current_row, column=2, value="No Next of Kin information available")
        current_row += 1

    current_row += 1

    # Financial Summary
    ws.merge_cells(f'A{current_row}:C{current_row}')
    ws[f'A{current_row}'] = "FINANCIAL SUMMARY"
    ws[f'A{current_row}'].font = bold_font
    current_row += 1

    financial_data = [
        ('Total Deposits:', f"₵{member.tot_deposits:,.2f}"),
        ('Total Shares:', f"₵{member.tot_shares:,.2f}"),
        ('Total Loans:', f"₵{member.tot_loans:,.2f}"),
        ('Guaranteed FOR Member:', f"₵{member.tot_guaranteed:,.2f}"),
        ('Member Guarantees FOR Others:', f"₵{member.tot_guaranted:,.2f}"),
    ]

    for label, value in financial_data:
        ws.cell(row=current_row, column=1, value=label).font = bold_font
        ws.cell(row=current_row, column=2, value=value)
        ws.cell(row=current_row, column=2).alignment = right_align
        current_row += 1

    current_row += 2

    # Footer
    ws.merge_cells(f'A{current_row}:C{current_row}')
    ws[f'A{current_row}'] = f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws[f'A{current_row}'].font = Font(italic=True)
    ws[f'A{current_row}'].alignment = center_align
    current_row += 1

    ws.merge_cells(f'A{current_row}:C{current_row}')
    ws[f'A{current_row}'] = f"Member ID: {member.id}"
    ws[f'A{current_row}'].font = Font(italic=True)
    ws[f'A{current_row}'].alignment = center_align

    # Adjust column widths
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 10

    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"member_{member.id}_{member.last_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response

def report_modal(request):
    return render(request, 'CredApp/modal_test.html')


@login_required
def member_delete(request, pk, slug):
    """Soft delete a member"""
    member = get_object_or_404(Master, pk=pk)
    entity = get_object_or_404(EntityModel, slug=slug)

    # Check if already deleted
    if member.del_rec == 'Yes':
        messages.warning(request, f"⚠️ Member {member.full_name} is already deleted.")
        return redirect('CredApp:member_list_manage')

    if request.method == 'POST':
        try:
            user = request.user

            # Update deletion fields
            member.del_rec = 'Yes'
            member.del_user = user
            member.del_date_time = timezone.now()
            member.del_username = user.username
            member.del_by_name = user.get_full_name() or user.username
            member.save()

            # Single success message
            messages.success(request, f" Member {member.full_name} (ID: {member.id}) has been deleted successfully.")

        except Exception as e:
            messages.error(request, f"❌ Error deleting member: {str(e)}")

        # Redirect to list page
        return redirect('CredApp:member_list_manage')

    # GET request - show confirmation page
    return render(request, 'CredApp/member_delete_confirm.html', {'member': member})


@login_required
def member_settings(request, member_id=None):
    """Member interest rate settings with search"""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = None
    search_query = request.GET.get("search", "")
    members = []

    # If search is performed
    if search_query:
        members = Master.objects.filter(
            Q(full_name__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(id__icontains=search_query)
        ).filter(is_deleted=False)[
            :20
        ]  # Limit to 20 results

    # If a member is selected
    if member_id:
        member = get_object_or_404(Master, id=member_id)

        if request.method == "POST":
            form = MemberSettingsForm(request.POST, instance=member)
            if form.is_valid():
                # Update audit fields
                if "sav_int_rate" in form.changed_data:
                    member.sav_int_rate_date = timezone.now()
                    member.sav_int_rate_user = request.user

                if "sav_defer_int_appl" in form.changed_data:
                    member.sav_defer_int_appl_date = timezone.now()
                    member.sav_defer_int_appl_user = request.user

                if "loan_int_rate" in form.changed_data:
                    member.loan_int_rate_date = timezone.now()
                    member.loan_int_rate_user = request.user

                member.save()
                messages.success(request, f"Settings updated for {member.full_name}")
                return redirect("MembersApp:member_settings", member_id=member.id)
        else:
            form = MemberSettingsForm(instance=member)
    else:
        form = MemberSettingsForm()

    context = {
        "member": member,
        "members": members,
        "search_query": search_query,
        "form": form,
        "today": timezone.now(),
        "user": request.user,
    }
    return render(request, "MembersApp/member_settings.html", context)


@login_required
def member_sett(request, slug):
    return render(request, "MembersApp/member_settings.html")


def members_sav_int_list(request):
    members = Master.objects.filter(is_deleted=False).order_by("full_name")

    context = {
        "members": members,
    }
    return render(request, "CredApp/members_sav_int_list.html", context)
