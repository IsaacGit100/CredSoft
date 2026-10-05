from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from decimal import Decimal
from django.contrib import messages

# Tables
from django_ledger.models import EntityModel, AccountModel
from MembersApp.models import Master, Sav_Int_Table
from LoanApp.models import Loan
from RecPayApp.models import Trans
from django.utils import timezone
from datetime import datetime
from .forms import MasterForm
from .models import CreditUnionConfig
from AutoServices.models import ServiceRun


from Report.pdf_builder import Col, build_report_pdf
from Report.utils import render_excel
from django.http import HttpResponse

# Functions
from django.db.models.functions import TruncMonth
from djan_led.utils import get_visible_accounts
from services.transaction_posting_service import process_transaction
from django.core.paginator import Paginator


from django.db import transaction
from django_ledger.models import EntityModel

from MembersApp.models import Master
from RecPayApp.models import Trans
from .forms import DepositWithdrawalForm
from AutoServices.services.runner import latest_runs_for


from datetime import timedelta

@login_required
def supervisor_credit_union_home(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    return render(request, "CreditUnion/supervisor_credit_union_home.html", {'entity': entity})


@login_required
def credit_union_dashboard(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    total_members = Master.objects.filter(entity=entity).count()

    total_active_loans = Loan.objects.filter(
        entity=entity,
        status__in=("ACTIVE", "DISBURSED", "APPROVED"),
    ).count()

    last_run = (
        ServiceRun.objects.filter(entity=entity, kind="main")
        .order_by("-run_date", "-started_at")
        .first()
    )
    last_auto_update = last_run.run_date if last_run else None

    pending_trans_count = Trans.objects.filter(
        entity=entity, journal_status="PENDING"
    ).count()

    context = {
        "now": timezone.localtime(),
        "pending": pending_trans_summary(entity),
        "nightly":      latest_runs_for(entity),
        "nightly_prev": latest_runs_for(entity, run_date=timezone.localdate() - timedelta(days=1)),
        
        # --- tiles ---
        "total_members": total_members,
        "total_active_loans": total_active_loans,
        "last_auto_update": last_auto_update,
        "pending_trans_count": pending_trans_count,
    }
    return render(request, "CreditUnion/credit_union_dashboard.html", context)


def pending_trans_summary(entity):
    """
    Return a summary of PENDING Trans for an entity.

    Returns:
        {
            "total": 7,
            "by_module": {"Savings": 4, "Loans": 2, "RecPayApp": 1},
            "amount": Decimal("1234.56"),
        }
    or None if nothing pending.
    """
    from decimal import Decimal
    from django.db.models import Count, Sum
    from RecPayApp.models import Trans

    qs = Trans.objects.filter(entity=entity, journal_status="PENDING")
    total = qs.count()
    if not total:
        return None

    by_module = (
        qs.values("module")
          .annotate(n=Count("id"))
          .order_by("-n")
    )

    amount = qs.aggregate(s=Sum("amount"))["s"] or Decimal("0.00")

    return {
        "total": total,
        "by_module": {(row["module"] or "Other"): row["n"] for row in by_module},
        "amount": amount,
    }


@login_required
def member_list_manage(request, slug):

    entity = get_object_or_404(EntityModel, slug=slug)
    # Filter members by this entity (you'll need an 'entity' field on Member)
    members = Master.objects.filter(entity=entity)

    """List all active members (exclude deleted)"""
    query = request.GET.get("q", "")
    # Only get members where del_rec is NOT 'Yes' (active members)
    members = Master.objects.all()

    if query:
        members = members.filter(
            Q(full_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(first_name__icontains=query)
            | Q(telephone1__icontains=query)
            | Q(email_address__icontains=query)
        )

    # Pagination
    paginator = Paginator(members, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "members": page_obj,
        "record_count": members.count(),
        "query": query,
    }
    return render(request, "CreditUnion/member_list_manage.html", context)


from django.urls import reverse

@login_required
def member_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        form = MasterForm(request.POST, entity=entity)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.entity = entity
            instance.save()

            percent1 = form.cleaned_data.get("nok_percent1", 0) or 0
            percent2 = form.cleaned_data.get("nok_percent2", 0) or 0
            percent3 = form.cleaned_data.get("nok_percent3", 0) or 0
            total_percent = percent1 + percent2 + percent3

            if total_percent == 100:
                messages.success(
                    request,
                    f"Member {instance.full_name} created successfully! "
                    f"NOK distribution: {percent1}% / {percent2}% / {percent3}%",
                )
            else:
                messages.success(
                    request,
                    f"Member {instance.full_name} created successfully!",
                )

            return redirect("CreditUnion:member_list_manage", slug=entity.slug)

        messages.error(request, "Please correct the errors below.")

    else:
        form = MasterForm(entity=entity)

    context = {
        "form": form,
        "entity": entity,
        "title": "Create New Member",
        "submit_text": "Save Member",
        "cancel_url": reverse("CreditUnion:member_list_manage", args=[entity.slug]),
    }
    return render(request, "CreditUnion/member_create.html", context)

@login_required
def member_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Master, pk=pk)

    if request.method == "POST":
        form = MasterForm(request.POST, entity=entity, instance=member)

        if form.is_valid():
            try:
                # Save with commit=False to assign entity first
                instance = form.save(commit=False)
                instance.entity = entity  # Assign entity BEFORE saving
                instance.save()

                # Get NOK percentages for verification
                percent1 = form.cleaned_data.get("nok_percent1", 0) or 0
                percent2 = form.cleaned_data.get("nok_percent2", 0) or 0
                percent3 = form.cleaned_data.get("nok_percent3", 0) or 0
                total_percent = percent1 + percent2 + percent3

                if total_percent == 100:
                    messages.success(
                        request,
                        f"Member {instance.full_name} updated successfully! "
                        f"NOK distribution: {percent1}% / {percent2}% / {percent3}%",
                    )
                else:
                    messages.success(
                        request, f"Member {instance.full_name} updated successfully!"
                    )

                #  Correct redirect – use named arguments
                return redirect("CreditUnion:member_view", slug=slug, pk=member.id)

            except Exception as e:
                messages.error(request, f"Error updating member: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = MasterForm(instance=member, entity=entity)

    context = {
        "form": form,
        "member": member,
        "entity": entity,
        "title": f"Edit Member: {member.full_name}",
        "submit_text": "Update Member",
        "cancel_url": "members:member_view",
        "cancel_id": member.id,
    }

    return render(request, "CreditUnion/member_create.html", context)


@login_required
def member_view(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    """View detailed member information"""
    member = get_object_or_404(Master, pk=pk)

    # Calculate age
    age = None
    if member.date_of_birth:
        today = datetime.now().date()
        age = (
            today.year
            - member.date_of_birth.year
            - (
                (today.month, today.day)
                < (member.date_of_birth.month, member.date_of_birth.day)
            )
        )

    context = {
        "member": member,
        "age": age,
        "total_guaranteed": member.tot_gua_given,
        "total_guaranted": member.tot_gua_received,
        "total_loans": member.tot_loans,
        "total_deposits": member.tot_deposits,
        "total_shares": member.tot_shares,
    }
    return render(request, "CreditUnion/member_view.html", context)

@login_required
def member_pdf(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Generate PDF for a single member"""
    member = get_object_or_404(Master, pk=pk)

    # Calculate age
    age = None
    if member.date_of_birth:
        today = datetime.now().date()
        age = (
            today.year
            - member.date_of_birth.year
            - (
                (today.month, today.day)
                < (member.date_of_birth.month, member.date_of_birth.day)
            )
        )

    # Create buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    elements = []

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.black,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        spaceAfter=10,
        textColor=colors.black,
    )

    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        spaceBefore=2,
        spaceAfter=2,
        textColor=colors.black,
    )

    # Title
    elements.append(Paragraph("ST. ANDREWS CO-OPERATIVE CREDIT UNION", title_style))
    elements.append(Paragraph("MEMBER INFORMATION", heading_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Member ID and Date
    elements.append(Paragraph(f"<b>Member ID:</b> {member.id}", normal_style))
    elements.append(
        Paragraph(
            f"<b>Date Enrolled:</b> {member.date_enrolled.strftime('%d/%m/%Y') if member.date_enrolled else 'N/A'}",
            normal_style,
        )
    )
    elements.append(Spacer(1, 0.1 * inch))

    # Personal Information Table
    elements.append(Paragraph("PERSONAL INFORMATION", heading_style))

    personal_data = [
        ["Full Name:", member.full_name or f"{member.first_name} {member.last_name}"],
        ["Title:", member.title or "-"],
        ["First Name:", member.first_name or "-"],
        ["Last Name:", member.last_name or "-"],
        ["Other Names:", member.other_names or "-"],
        [
            "Date of Birth:",
            member.date_of_birth.strftime("%d/%m/%Y") if member.date_of_birth else "-",
        ],
        ["Age:", str(age) if age else "-"],
        ["Gender:", member.gender or "-"],
        ["Marital Status:", member.marital_status or "-"],
        ["Church Member:", member.church_member or "-"],
        ["Profession:", member.profession or "-"],
        ["Status:", member.mem_status or "-"],
        #    ['Loan Status:', member.loan_status or '-'],
        ["Role:", member.role or "-"],
    ]

    personal_table = Table(personal_data, colWidths=[1.5 * inch, 4 * inch])
    personal_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(personal_table)
    elements.append(Spacer(1, 0.15 * inch))

    # Contact Information
    elements.append(Paragraph("CONTACT INFORMATION", heading_style))

    contact_data = [
        ["Phone 1:", member.telephone1 or "-"],
        ["Phone 2:", member.telephone2 or "-"],
        ["Email:", member.email_address or "-"],
        ["Residential Address:", member.residential_address or "-"],
        ["Postal Address:", member.postal_address or "-"],
        ["City:", member.city or "-"],
        ["Near Landmark:", member.near_landmark or "-"],
        ["Street Name:", member.street_name or "-"],
        ["GPS Address:", member.gps or "-"],
    ]

    contact_table = Table(contact_data, colWidths=[1.5 * inch, 4 * inch])
    contact_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(contact_table)
    elements.append(Spacer(1, 0.15 * inch))

    # Next of Kin Information
    elements.append(Paragraph("NEXT OF KIN INFORMATION", heading_style))

    nok_data = []
    if member.nok_name1:
        nok_data.append(
            [
                "NOK 1:",
                f"{member.nok_name1} ({member.nok_relation1}) - {member.nok_telephone1}",
            ]
        )
        if member.nok_address1:
            nok_data.append(["", member.nok_address1])
        if member.nok_gps1:
            nok_data.append(["", f"GPS: {member.nok_gps1}"])
        if member.nok_percent1:
            nok_data.append(["", f"Share: {member.nok_percent1}%"])

    if member.nok_name2:
        nok_data.append(
            [
                "NOK 2:",
                f"{member.nok_name2} ({member.nok_relation2}) - {member.nok_telephone2}",
            ]
        )
        if member.nok_address2:
            nok_data.append(["", member.nok_address2])
        if member.nok_gps2:
            nok_data.append(["", f"GPS: {member.nok_gps2}"])
        if member.nok_percent2:
            nok_data.append(["", f"Share: {member.nok_percent2}%"])

    if member.nok_name3:
        nok_data.append(
            [
                "NOK 3:",
                f"{member.nok_name3} ({member.nok_relation3}) - {member.nok_telephone3}",
            ]
        )
        if member.nok_address3:
            nok_data.append(["", member.nok_address3])
        if member.nok_gps3:
            nok_data.append(["", f"GPS: {member.nok_gps3}"])
        if member.nok_percent3:
            nok_data.append(["", f"Share: {member.nok_percent3}%"])

    if not nok_data:
        nok_data = [["No Next of Kin information available", ""]]

    nok_table = Table(nok_data, colWidths=[1.5 * inch, 4 * inch])
    nok_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(nok_table)
    elements.append(Spacer(1, 0.15 * inch))

    # Financial Summary
    elements.append(Paragraph("FINANCIAL SUMMARY", heading_style))

    financial_data = [
        ["Total Deposits:", f"₵{member.tot_deposits:,.2f}"],
        ["Total Shares:", f"₵{member.tot_shares:,.2f}"],
        ["Total Loans:", f"₵{member.tot_loans:,.2f}"],
        ["Guaranteed FOR Member:", f"₵{member.tot_guaranteed:,.2f}"],
        ["Member Guarantees FOR Others:", f"₵{member.tot_guaranted:,.2f}"],
    ]

    financial_table = Table(financial_data, colWidths=[2 * inch, 3.5 * inch])
    financial_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(financial_table)
    elements.append(Spacer(1, 0.15 * inch))

    # Footer
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("-" * 70, normal_style))
    elements.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style
        )
    )
    elements.append(Paragraph(f"Member ID: {member.id}", normal_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    filename = (
        f"member_{member.id}_{member.last_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


@login_required
def member_excel(request, slug, pk):
    """Generate Excel for a single member"""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Master, pk=pk)

    # Calculate age
    age = None
    if member.date_of_birth:
        today = datetime.now().date()
        age = (
            today.year
            - member.date_of_birth.year
            - (
                (today.month, today.day)
                < (member.date_of_birth.month, member.date_of_birth.day)
            )
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
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    current_row = 1

    # Title
    ws.merge_cells(f"A{current_row}:C{current_row}")
    ws[f"A{current_row}"] = "ST. ANDREWS CO-OPERATIVE CREDIT UNION"
    ws[f"A{current_row}"].font = Font(bold=True, size=14)
    ws[f"A{current_row}"].alignment = center_align
    current_row += 1

    ws.merge_cells(f"A{current_row}:C{current_row}")
    ws[f"A{current_row}"] = "MEMBER INFORMATION"
    ws[f"A{current_row}"].font = Font(bold=True, size=12)
    ws[f"A{current_row}"].alignment = center_align
    current_row += 2

    # Member ID and Date
    ws[f"A{current_row}"] = "Member ID:"
    ws[f"B{current_row}"] = member.id
    ws[f"A{current_row}"].font = bold_font
    current_row += 1

    ws[f"A{current_row}"] = "Date Enrolled:"
    ws[f"B{current_row}"] = (
        member.date_enrolled.strftime("%d/%m/%Y") if member.date_enrolled else "-"
    )
    ws[f"A{current_row}"].font = bold_font
    current_row += 2

    # Personal Information
    ws.merge_cells(f"A{current_row}:C{current_row}")
    ws[f"A{current_row}"] = "PERSONAL INFORMATION"
    ws[f"A{current_row}"].font = bold_font
    current_row += 1

    personal_data = [
        ("Full Name:", member.full_name or f"{member.first_name} {member.last_name}"),
        ("Title:", member.title or "-"),
        ("First Name:", member.first_name or "-"),
        ("Last Name:", member.last_name or "-"),
        ("Other Names:", member.other_names or "-"),
        (
            "Date of Birth:",
            member.date_of_birth.strftime("%d/%m/%Y") if member.date_of_birth else "-",
        ),
        ("Age:", str(age) if age else "-"),
        ("Gender:", member.gender or "-"),
        ("Marital Status:", member.marital_status or "-"),
        ("Church Member:", member.church_member or "-"),
        ("Profession:", member.profession or "-"),
        ("Status:", member.mem_status or "-"),
        #    ('Loan Status:', member.loan_status or '-'),
        ("Role:", member.role or "-"),
    ]

    for label, value in personal_data:
        ws.cell(row=current_row, column=1, value=label).font = bold_font
        ws.cell(row=current_row, column=2, value=value)
        current_row += 1

    current_row += 1

    # Contact Information
    ws.merge_cells(f"A{current_row}:C{current_row}")
    ws[f"A{current_row}"] = "CONTACT INFORMATION"
    ws[f"A{current_row}"].font = bold_font
    current_row += 1

    contact_data = [
        ("Phone 1:", member.telephone1 or "-"),
        ("Phone 2:", member.telephone2 or "-"),
        ("Email:", member.email_address or "-"),
        ("Residential Address:", member.residential_address or "-"),
        ("Postal Address:", member.postal_address or "-"),
        ("City:", member.city or "-"),
        ("Near Landmark:", member.near_landmark or "-"),
        ("Street Name:", member.street_name or "-"),
        ("GPS Address:", member.gps or "-"),
    ]

    for label, value in contact_data:
        ws.cell(row=current_row, column=1, value=label).font = bold_font
        ws.cell(row=current_row, column=2, value=value)
        current_row += 1

    current_row += 1

    # Next of Kin Information
    ws.merge_cells(f"A{current_row}:C{current_row}")
    ws[f"A{current_row}"] = "NEXT OF KIN INFORMATION"
    ws[f"A{current_row}"].font = bold_font
    current_row += 1

    if member.nok_name1:
        ws.cell(row=current_row, column=1, value="NOK 1:").font = bold_font
        ws.cell(
            row=current_row,
            column=2,
            value=f"{member.nok_name1} ({member.nok_relation1}) - {member.nok_telephone1}",
        )
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
        ws.cell(
            row=current_row,
            column=2,
            value=f"{member.nok_name2} ({member.nok_relation2}) - {member.nok_telephone2}",
        )
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
        ws.cell(
            row=current_row,
            column=2,
            value=f"{member.nok_name3} ({member.nok_relation3}) - {member.nok_telephone3}",
        )
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
    ws.merge_cells(f"A{current_row}:C{current_row}")
    ws[f"A{current_row}"] = "FINANCIAL SUMMARY"
    ws[f"A{current_row}"].font = bold_font
    current_row += 1

    financial_data = [
        ("Total Deposits:", f"₵{member.tot_deposits:,.2f}"),
        ("Total Shares:", f"₵{member.tot_shares:,.2f}"),
        ("Total Loans:", f"₵{member.tot_loans:,.2f}"),
        ("Guaranteed FOR Member:", f"₵{member.tot_guaranteed:,.2f}"),
        ("Member Guarantees FOR Others:", f"₵{member.tot_guaranted:,.2f}"),
    ]

    for label, value in financial_data:
        ws.cell(row=current_row, column=1, value=label).font = bold_font
        ws.cell(row=current_row, column=2, value=value)
        ws.cell(row=current_row, column=2).alignment = right_align
        current_row += 1

    current_row += 2

    # Footer
    ws.merge_cells(f"A{current_row}:C{current_row}")
    ws[f"A{current_row}"] = f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws[f"A{current_row}"].font = Font(italic=True)
    ws[f"A{current_row}"].alignment = center_align
    current_row += 1

    ws.merge_cells(f"A{current_row}:C{current_row}")
    ws[f"A{current_row}"] = f"Member ID: {member.id}"
    ws[f"A{current_row}"].font = Font(italic=True)
    ws[f"A{current_row}"].alignment = center_align

    # Adjust column widths
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 10

    # Create response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"member_{member.id}_{member.last_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response


def report_modal(request):
    return render(request, "CreditUnion/modal_test.html")


@login_required
def member_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Soft delete a member"""
    member = get_object_or_404(Master, pk=pk)

    # Check if already deleted
    if member.del_rec == "Yes":
        messages.warning(request, f" Member {member.full_name} is already deleted.")
        return redirect("CreditUnion:member_list_manage", slug=entity.slug)
    if request.method == "POST":
        try:
            user = request.user

            # Update deletion fields
            member.del_rec = "Yes"
            member.del_user = user
            member.del_date_time = timezone.now()
            member.del_username = user.username
            member.del_by_name = user.get_full_name() or user.username
            member.save()

            # Single success message
            messages.success(
                request,
                f" Member {member.full_name} (ID: {member.id}) has been deleted successfully.",
            )

        except Exception as e:
            messages.error(request, f" Error deleting member: {str(e)}")

        # Redirect to list page

        return redirect("CreditUnion:member_list_manage", slug=entity.slug)

    # GET request - show confirmation page
    return render(request, "CreditUnion/member_delete_confirm.html", {"member": member})


@login_required
def union_dashboard(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # Access check (same as other views)
    try:
        profile = request.user.djan_led_profile
        if entity not in profile.allowed_entities.all() and entity != profile.default_entity:
            return render(request, 'djan_led/access_denied.html', {'entity': entity})
    except:
        pass

    # --- Statistics ---
    # Members
    total_members = Master.objects.filter(entity=entity, is_deleted=False).count()
    active_members = Master.objects.filter(entity=entity, is_deleted=False, mem_status='Active').count()

    # Loans
    total_loans = Loan.objects.filter(entity=entity).count()
    active_loans = Loan.objects.filter(entity=entity, status='Active').count()
    total_loan_balance = Loan.objects.filter(entity=entity).aggregate(Sum('loan_balance'))['loan_balance__sum'] or Decimal('0')
    total_disbursed = Loan.objects.filter(entity=entity).aggregate(Sum('principal'))['principal__sum'] or Decimal('0')

    # Savings – use Master.tot_deposits as a proxy
    total_savings = Master.objects.filter(entity=entity).aggregate(Sum('tot_deposits'))['tot_deposits__sum'] or Decimal('0')

    # Recent Transactions (last 10)
    recent_trans = Trans.objects.filter(entity=entity).order_by('-date')[:10]

    # Today's date
    today = timezone.now().date()

    context = {
        'entity': entity,
        'total_members': total_members,
        'active_members': active_members,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'total_loan_balance': total_loan_balance,
        'total_disbursed': total_disbursed,
        'total_savings': total_savings,
        'recent_trans': recent_trans,
        'today': today,
    }
    return render(request, 'CreditUnion/credit_union_dashboard.html', context)


@login_required
def run_pending_transactions(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # Only supervisors (or staff) can access – adjust as needed
    if not request.user.is_staff:
        messages.error(request, "You are not authorised.")
        return redirect("djan_led:entity_dashboard", slug=slug)

    # Get all pending transactions for this entity
    pending_trans = Trans.objects.filter(
        entity=entity,
        status="DRAFT",  # or 'PENDING' – adjust to your field
        journal_status="PENDING",  # if you have this field
    ).order_by("-date")

    results = {
        "success": [],
        "failed": [],
        "total": pending_trans.count(),
    }

    if request.method == "POST":
        for trans in pending_trans:
            try:
                result = process_transaction(trans, request.user)
                if result.get("success"):
                    results["success"].append(trans.id)
                else:
                    results["failed"].append(
                        {
                            "id": trans.id,
                            "error": result.get("errors", ["Unknown error"])[0],
                        }
                    )
            except Exception as e:
                results["failed"].append({"id": trans.id, "error": str(e)})

        # Redirect to a results page or re-render with results
        return render(request, "Supervisor/pending_transactions.html", {"entity": entity, "pending_trans": pending_trans, "results": results,
                "processed": True,
            },
        )

    return render(request, "Supervisor/pending_transactions.html", {"entity": entity, "pending_trans": pending_trans, "processed": False})


@login_required
def sav_int_audit(request, entity_slug):
    entity = get_object_or_404(EntityModel, slug=entity_slug)
    member = None
    records = []
    monthly_summary = []
    form = SavIntSearchForm(request.GET or None)

    if request.GET and "search" in request.GET:
        search_term = request.GET.get("search", "").strip()
        # Try to find member by id or last_name
        members = Master.objects.filter(entity=entity, is_deleted=False)
        if search_term.isdigit():
            members = members.filter(entity=entity, id=int(search_term))
        else:
            members = members.filter(entity=entity, last_name__icontains=search_term)

        if members.count() == 1:
            member = members.first()
            records = Sav_Int_Table.objects.filter(
                master=member, entity=entity
            ).order_by("date")

            # Monthly summary
            monthly_summary = (
                records.annotate(month=TruncMonth("date"))
                .values("month")
                .annotate(
                    total_interest=Sum("sav_int"),
                    total_days=Sum("no_of_days"),
                    record_count=Count("id"),
                )
                .order_by("month")
            )
        elif members.count() > 1:
            # Multiple matches; we could show a list, but for simplicity we set a message
            form.add_error(
                "search",
                f"Multiple members found ({members.count()}). Please be more specific.",
            )
        elif search_term:
            form.add_error("search", "No member found with that ID or last name.")

    context = {
        "entity": entity,
        "form": form,
        "member": member,
        "records": records,
        "monthly_summary": monthly_summary,
    }
    return render(request, "CreditUnion/sav_int_audit.html", context)


SAVINGS_CODE = "2021"
DEPOSIT_SUBMODULE = "savings_deposit"
WITHDRAWAL_SUBMODULE = "savings_withdrawal"


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------


@login_required
def deposit_withdrawal_manage(request, slug):
    """Deposit/Withdrawal — single-page form + list."""
    entity = get_object_or_404(EntityModel, slug=slug)

    # ---------- POST: save the form ----------
    if request.method == "POST" and "save" in request.POST:
        form = DepositWithdrawalForm(request.POST, entity=entity, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                trans = form.save()

                # Update member's running totals
                member = trans.member
                if member:
                    amount = trans.amount or Decimal("0")
                    if trans.sub_module == DEPOSIT_SUBMODULE:
                        member.tot_deposits = (
                            member.tot_deposits or Decimal("0")
                        ) + amount
                    else:
                        member.tot_deposit_withdrawal = (
                            member.tot_deposit_withdrawal or Decimal("0")
                        ) + amount
                    member.save(
                        update_fields=["tot_deposits", "tot_deposit_withdrawal"]
                    )

            label = "Deposit" if trans.sub_module == DEPOSIT_SUBMODULE else "Withdrawal"
            messages.success(
                request,
                f"{label} of ₵{trans.amount:,.2f} recorded for {trans.member_name}.",
            )
            return redirect("CreditUnion:deposit_withdrawal_manage", slug=entity.slug)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepositWithdrawalForm(entity=entity, user=request.user)

    # ---------- GET: list + summary ----------
    qs = Trans.objects.filter(
        entity=entity,
        module="credit_union",
        sub_module__in=[DEPOSIT_SUBMODULE, WITHDRAWAL_SUBMODULE],
    ).order_by("-date", "-id")

    search = request.GET.get("q", "").strip()
    txn_filter = request.GET.get("type", "").strip()

    if search:
        qs = qs.filter(
            Q(member_name__icontains=search)
            | Q(rec_vou_no__icontains=search)
            | Q(member_no__icontains=search)
        )
    if txn_filter == "Deposit":
        qs = qs.filter(sub_module=DEPOSIT_SUBMODULE)
    elif txn_filter == "Withdrawal":
        qs = qs.filter(sub_module=WITHDRAWAL_SUBMODULE)

    total_deposits = qs.filter(sub_module=DEPOSIT_SUBMODULE).aggregate(s=Sum("amount"))[
        "s"
    ] or Decimal("0")
    total_withdrawals = qs.filter(sub_module=WITHDRAWAL_SUBMODULE).aggregate(
        s=Sum("amount")
    )["s"] or Decimal("0")

    return render(
        request,
        "CreditUnion/deposit_withdrawal.html",
        {
            "entity": entity,
            "form": form,
            "transactions": qs,
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "net": total_deposits - total_withdrawals,
            "search": search,
            "type_filter": txn_filter,
        },
    )


@login_required
def deposit_withdrawal_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(
        Trans,
        pk=pk,
        entity=entity,
        module="credit_union",
        sub_module__in=[DEPOSIT_SUBMODULE, WITHDRAWAL_SUBMODULE],
    )

    # Guard: don't edit posted journals
    if trans.journal_entry_id:
        messages.warning(
            request, "This record has been posted to journals. Reverse it first."
        )
        return redirect("CreditUnion:deposit_withdrawal_manage", slug=entity.slug)

    if request.method == "POST":
        form = DepositWithdrawalForm(
            request.POST,
            instance=trans,
            entity=entity,
            user=request.user,
        )
        if form.is_valid():
            with transaction.atomic():
                # Reverse old totals before saving
                old_member = trans.member
                old_amount = trans.amount or Decimal("0")
                old_was_deposit = trans.sub_module == DEPOSIT_SUBMODULE

                if old_member:
                    if old_was_deposit:
                        old_member.tot_deposits = max(
                            (old_member.tot_deposits or Decimal("0")) - old_amount,
                            Decimal("0"),
                        )
                    else:
                        old_member.tot_deposit_withdrawal = max(
                            (old_member.tot_deposit_withdrawal or Decimal("0"))
                            - old_amount,
                            Decimal("0"),
                        )
                    old_member.save(
                        update_fields=["tot_deposits", "tot_deposit_withdrawal"]
                    )

                updated = form.save()

                # Apply new totals
                new_member = updated.member
                new_amount = updated.amount or Decimal("0")
                new_is_deposit = updated.sub_module == DEPOSIT_SUBMODULE

                if new_member:
                    if new_is_deposit:
                        new_member.tot_deposits = (
                            new_member.tot_deposits or Decimal("0")
                        ) + new_amount
                    else:
                        new_member.tot_deposit_withdrawal = (
                            new_member.tot_deposit_withdrawal or Decimal("0")
                        ) + new_amount
                    new_member.save(
                        update_fields=["tot_deposits", "tot_deposit_withdrawal"]
                    )

            messages.success(request, "Transaction updated.")
            return redirect(
                "CreditUnion:deposit_withdrawal_manage", slug=entity.slug
            )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepositWithdrawalForm(instance=trans, entity=entity, user=request.user)

    return render(
        request,
        "CreditUnion/deposit_withdrawal.html",
        {
            "entity": entity,
            "form": form,
            "trans": trans,
            "title": "Edit Deposit / Withdrawal",
        },
    )


@login_required
def deposit_withdrawal_view(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(
        Trans,
        pk=pk,
        entity=entity,
        module="credit_union",
        sub_module__in=[DEPOSIT_SUBMODULE, WITHDRAWAL_SUBMODULE],
    )
    return render(
        request,
        "CreditUnion/deposit_withdrawal_view.html",
        {
            "entity": entity,
            "trans": trans,
        },
    )


@login_required
def deposit_withdrawal_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(
        Trans, pk=pk, entity=entity,
        module="credit_union",
        sub_module__in=[DEPOSIT_SUBMODULE, WITHDRAWAL_SUBMODULE],
    )

    # Block delete if already posted to journals
    if trans.journal_entry_id:
        messages.warning(
            request,
            "This transaction has been posted to journals. Reverse the entry first.",
        )
        return redirect("CreditUnion:deposit_withdrawal_manage", slug=entity.slug)

    if request.method == "POST":
        with transaction.atomic():
            member = trans.member
            amount = trans.amount or Decimal("0")

            # Reverse member totals
            if member:
                if trans.sub_module == DEPOSIT_SUBMODULE:
                    member.tot_deposits = max(
                        (member.tot_deposits or Decimal("0")) - amount,
                        Decimal("0"),
                    )
                else:
                    member.tot_deposit_withdrawal = max(
                        (member.tot_deposit_withdrawal or Decimal("0")) - amount,
                        Decimal("0"),
                    )
                member.save(update_fields=["tot_deposits", "tot_deposit_withdrawal"])

            label = "Deposit" if trans.sub_module == DEPOSIT_SUBMODULE else "Withdrawal"
            trans.delete()

        messages.success(request, f"{label} deleted successfully.")
        return redirect("CreditUnion:deposit_withdrawal_manage", slug=entity.slug)

    # GET — show confirm page
    return render(request, "CreditUnion/deposit_withdrawal_delete.html", {"entity": entity, "trans": trans})

# ====================================== Trans Create ========================================
@login_required
def trans_create(request, slug):
    """Credit Union general Receipts & Payments form."""
    entity = get_object_or_404(EntityModel, slug=slug)

    # COA + visible accounts
    try:
        coa = entity.get_default_coa()
    except Exception:
        messages.error(request, "This entity does not have a Chart of Accounts.")
        return redirect("djan_led:chart_of_accounts", slug=entity.slug)

    if not coa:
        messages.error(request, "No Chart of Accounts found for this entity.")
        return redirect("djan_led:chart_of_accounts", slug=entity.slug)

    accounts = get_visible_accounts(request.user, entity)

    # Members of this CU only
    members = Master.objects.filter(entity=entity, is_deleted=False).order_by(
        "last_name", "first_name"
    )

    # Member selection
    selected_member_id = request.GET.get("member_id") or request.POST.get("member_id")
    selected_member = None
    active_loans = []

    if selected_member_id and selected_member_id.isdigit():
        try:
            selected_member = Master.objects.get(
                id=int(selected_member_id), entity=entity
            )
            active_loans = Loan.objects.filter(
                master=selected_member,
                status__in=["Active", "New Loan"],
            ).order_by("-disbursement_date")
        except Master.DoesNotExist:
            selected_member = None
            active_loans = []

    # ---------- POST ----------
    if request.method == "POST":
        if "close" in request.POST:
            return redirect("CreditUnion:credit_union_dashboard", entity.slug)

        if "save" in request.POST:
            form = request.POST  # keep user input for re-render

            # ---- parse & validate ----
            errors = []

            date_str = request.POST.get("date", "").strip()
            trans_no = request.POST.get("trans_no", "").strip()
            trans_type = request.POST.get("trans_type", "").strip()
            amount_str = request.POST.get("amount", "").replace(",", "").strip()
            pay_mode = request.POST.get("pay_mode", "").strip()
            name_type = request.POST.get("name_type", "").strip()
            details = request.POST.get("details", "").strip()

            if not date_str:
                errors.append("Date is required.")
            if not trans_no:
                errors.append("Reference No is required.")
            if trans_type not in ("Receipts", "Payments"):
                errors.append("Type must be Receipts or Payments.")

            # date
            date = None
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            if not date:
                errors.append("Invalid date. Use DD/MM/YYYY.")

            # amount
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    errors.append("Amount must be greater than zero.")
            except Exception:
                amount = None
                errors.append("Amount must be a valid number.")

            # duplicate ref
            if (
                trans_no
                and Trans.objects.filter(
                    entity=entity, module="credit_union", trans_no=trans_no
                ).exists()
            ):
                errors.append(f"Reference No '{trans_no}' already exists.")

            # ledger
            chart_value = request.POST.get("chart_account", "").strip()
            ledger = None
            if not chart_value:
                errors.append("Ledger account is required.")
            else:
                parts = chart_value.split(",")
                if len(parts) != 3 or not parts[0].strip():
                    errors.append("Invalid ledger selection.")
                else:
                    try:
                        ledger = AccountModel.objects.get(
                            pk=parts[0].strip(), coa_model=coa, active=True
                        )
                    except (AccountModel.DoesNotExist, ValueError):
                        errors.append(
                            "Selected ledger account not valid for this entity."
                        )

            if errors:
                for e in errors:
                    messages.error(request, e)
                context = _cu_trans_context(
                    request,
                    entity,
                    accounts,
                    members,
                    selected_member,
                    selected_member_id,
                    active_loans,
                    form,
                )
                return render(request, "CreditUnion/trans_create.html", context)

            # ---- member / non-member ----
            member_obj = None
            member_no = None
            member_name = ""
            non_member_name = ""
            non_member_contact = ""

            if name_type == "Member":
                member_id = request.POST.get("member_id", "")
                if member_id and member_id.isdigit():
                    try:
                        member_obj = Master.objects.get(
                            id=int(member_id), entity=entity
                        )
                        member_no = member_obj.id
                        member_name = member_obj.full_name
                    except Master.DoesNotExist:
                        pass
            elif name_type == "Non Member":
                non_member_name = request.POST.get("non_member_name", "").strip()
                non_member_contact = request.POST.get("non_member_contact", "").strip()

            # ---- loan ----
            loan_obj = None
            loan_id_value = request.POST.get("loan_id", "")
            if loan_id_value and loan_id_value.isdigit():
                try:
                    loan_obj = Loan.objects.get(id=int(loan_id_value))
                except Loan.DoesNotExist:
                    loan_obj = None

            # ---- cheque / transfer ----
            bank = bank_no = bank_branch = momo_no = momo_name = cheque_no = ""
            cheque_date = None

            if pay_mode == "Cheque":
                bank = request.POST.get("bank", "").strip()
                bank_no = request.POST.get("bank_no", "").strip()
                bank_branch = request.POST.get("bank_branch", "").strip()
                cheque_no = request.POST.get("cheque_no", "").strip()
                cd = request.POST.get("cheque_date", "").strip()
                if cd:
                    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                        try:
                            cheque_date = datetime.strptime(cd, fmt).date()
                            break
                        except ValueError:
                            continue
            elif pay_mode == "Transfer":
                momo_no = request.POST.get("momo_no", "").strip()
                momo_name = request.POST.get("momo_name", "").strip()

            rec_vou_no = (
                f"REC:{trans_no}" if trans_type == "Receipts" else f"VOU:{trans_no}"
            )

            # ---- save ----
            try:
                with transaction.atomic():
                    trans = Trans.objects.create(
                        entity=entity,
                        module="credit_union",
                        sub_module="receipts_payments",
                        date=date,
                        trans_no=trans_no,
                        rec_vou_no=rec_vou_no,
                        trans_type=trans_type,
                        amount=amount,
                        pay_mode=pay_mode,
                        purpose=ledger.name,
                        details=details,
                        member=member_obj,
                        member_no=member_no or 0,
                        member_name=member_name,
                        non_member_name=non_member_name,
                        non_member_contact=non_member_contact,
                        loan=loan_obj,
                        bank=bank,
                        bank_no=bank_no,
                        bank_branch=bank_branch,
                        momo_no=momo_no,
                        momo_name=momo_name,
                        cheque_no=cheque_no,
                        cheque_date=cheque_date,
                        ledger_id=str(ledger.pk),
                        ledger_code=str(ledger.code),
                        ledger_name=ledger.name,
                        status="DRAFT",
                        journal_status="PENDING",
                        created_by_id=request.user.id,
                        created_by_name=request.user.get_full_name()
                        or request.user.username,
                        created_by_username=request.user.username,
                    )
            except Exception as e:
                messages.error(request, f"Could not save: {e}")
                import traceback

                traceback.print_exc()
                context = _cu_trans_context(
                    request,
                    entity,
                    accounts,
                    members,
                    selected_member,
                    selected_member_id,
                    active_loans,
                    request.POST,
                )
                return render(request, "CreditUnion/trans_create.html", context)

            messages.success(request, f"Transaction {trans_no} saved successfully.")
            return redirect("CreditUnion:trans_create", entity.slug)

    # ---------- GET ----------
    context = _cu_trans_context(
        request,
        entity,
        accounts,
        members,
        selected_member,
        selected_member_id,
        active_loans,
        None,
    )
    return render(request, "CreditUnion/trans_create.html", context)


def _cu_trans_context(
    request,
    entity,
    accounts,
    members,
    selected_member,
    selected_member_id,
    active_loans,
    form,
):
    """Shared context builder for the CU RP form."""
    # Only CU receipts/payments for THIS entity
    transactions = Trans.objects.filter(
        entity=entity,
        module="credit_union",
        sub_module="receipts_payments",
    ).order_by("-date", "-id")

    total_records = transactions.count()
    receipts = transactions.filter(trans_type="Receipts")
    payments = transactions.filter(trans_type="Payments")

    receipts_count = receipts.count()
    payments_count = payments.count()
    receipts_total = receipts.aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")
    payments_total = payments.aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")

    paginator = Paginator(transactions, 50)
    page_obj = paginator.get_page(request.GET.get("page"))

    return {
        "tran": page_obj,
        "members": members,
        "loans": active_loans,
        "accounts": accounts,
        "selected_member": selected_member,
        "selected_member_id": selected_member_id,
        "total_records": total_records,
        "receipts_count": receipts_count,
        "payments_count": payments_count,
        "receipts_total": receipts_total,
        "payments_total": payments_total,
        "net_balance": receipts_total - payments_total,
        "today": datetime.now().date(),
        "entity": entity,
        "form": form or {},
    }

# ---------------------------------------------------------------------------
# CU RP Trans — View / Edit / Delete / PDF / Excel
# ---------------------------------------------------------------------------
CU_RP_MODULE = "credit_union"
CU_RP_SUBMODULE = "receipts_payments"


def _cu_rp_qs(entity):
    return Trans.objects.filter(
        entity=entity, module=CU_RP_MODULE, sub_module=CU_RP_SUBMODULE,
    )


def _cu_rp_initial(trans):
    """Build initial values dict for the RP form from a Trans instance."""
    return {
        "date": trans.date.strftime("%d/%m/%Y") if trans.date else "",
        "trans_no": trans.trans_no or "",
        "trans_type": trans.trans_type or "Receipts",
        "amount": str(trans.amount) if trans.amount is not None else "",
        "pay_mode": trans.pay_mode or "Cash",
        "details": trans.details or "",
        "name_type": "Member" if trans.member_id else ("Non Member" if trans.non_member_name else "Member"),
        "member_id": trans.member_id or "",
        "non_member_name": trans.non_member_name or "",
        "non_member_contact": trans.non_member_contact or "",
        "ledger_id": trans.ledger_id or "",
        "ledger_code": trans.ledger_code or "",
        "ledger_name": trans.ledger_name or "",
        "cheque_date": trans.cheque_date.strftime("%d/%m/%Y") if trans.cheque_date else "",
        "cheque_no": trans.cheque_no or "",
        "bank": trans.bank or "",
        "bank_branch": trans.bank_branch or "",
        "bank_no": trans.bank_no or "",
        "momo_no": trans.momo_no or "",
        "momo_name": trans.momo_name or "",
    }


@login_required
def trans_view(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(_cu_rp_qs(entity), pk=pk)

    return render(request, "CreditUnion/trans_view.html", {
        "entity": entity,
        "trans": trans,
    })


@login_required
def trans_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(_cu_rp_qs(entity), pk=pk)

    # Guard: don't edit if posted to journals
    if trans.journal_entry_id:
        messages.warning(
            request,
            "This transaction has been posted to journals. Reverse the entry first.",
        )
        return redirect("CreditUnion:trans_view", entity.slug, trans.pk)

    accounts = get_visible_accounts(request.user, entity)
    members = Master.objects.filter(
        entity=entity, is_deleted=False
    ).order_by("last_name", "first_name")

    if request.method == "POST":
        # Update the existing Trans row using the same field mapping
        try:
            trans.date       = datetime.strptime(request.POST.get("date"), "%d/%m/%Y").date()
            trans.trans_no   = request.POST.get("trans_no", "").strip()
            trans.trans_type = request.POST.get("trans_type", "Receipts")
            trans.amount     = Decimal(request.POST.get("amount", "0").replace(",", ""))
            trans.pay_mode   = request.POST.get("pay_mode", "Cash")
            trans.details    = request.POST.get("details", "").strip()
            trans.rec_vou_no = f"REC:{trans.trans_no}" if trans.trans_type == "Receipts" else f"VOU:{trans.trans_no}"

            ledger_id = request.POST.get("ledger_id", "")
            ledger_code = request.POST.get("ledger_code", "")
            ledger_name = request.POST.get("ledger_name", "")
            if ledger_id and ledger_code:
                trans.ledger_id = ledger_id
                trans.ledger_code = ledger_code
                trans.ledger_name = ledger_name
                trans.purpose = ledger_name

            # Member / non-member
            name_type = request.POST.get("name_type", "Member")
            if name_type == "Member":
                member_id = request.POST.get("member_id", "")
                if member_id and member_id.isdigit():
                    m = Master.objects.filter(pk=int(member_id), entity=entity).first()
                    if m:
                        trans.member = m
                        trans.member_no = m.id
                        trans.member_name = m.full_name
                trans.non_member_name = ""
                trans.non_member_contact = ""
            else:
                trans.member = None
                trans.member_no = 0
                trans.member_name = ""
                trans.non_member_name = request.POST.get("non_member_name", "").strip()
                trans.non_member_contact = request.POST.get("non_member_contact", "").strip()

            # Cheque / transfer
            if trans.pay_mode == "Cheque":
                trans.bank = request.POST.get("bank", "").strip()
                trans.bank_no = request.POST.get("bank_no", "").strip()
                trans.bank_branch = request.POST.get("bank_branch", "").strip()
                trans.cheque_no = request.POST.get("cheque_no", "").strip()
                cd = request.POST.get("cheque_date", "").strip()
                trans.cheque_date = datetime.strptime(cd, "%d/%m/%Y").date() if cd else None
                trans.momo_no = ""
                trans.momo_name = ""
            elif trans.pay_mode == "Transfer":
                trans.bank = trans.bank_no = trans.bank_branch = trans.cheque_no = ""
                trans.cheque_date = None
                trans.momo_no = request.POST.get("momo_no", "").strip()
                trans.momo_name = request.POST.get("momo_name", "").strip()
            else:
                trans.bank = trans.bank_no = trans.bank_branch = ""
                trans.cheque_no = ""
                trans.cheque_date = None
                trans.momo_no = trans.momo_name = ""

            trans.save()
            messages.success(request, f"Transaction {trans.trans_no} updated.")
            return redirect("CreditUnion:trans_view", entity.slug, trans.pk)

        except Exception as e:
            messages.error(request, f"Could not update: {e}")
            import traceback
            traceback.print_exc()
    
    initial = _cu_rp_initial(trans)
    if request.method == "POST":
        initial = request.POST
            
    return render(request, "CreditUnion/trans_create.html", {
        "entity": entity,
        "accounts": accounts,
        "members": members,
        "tran": _cu_rp_qs(entity).order_by("-date", "-id")[:50],
        "form": initial,
        "editing": True,
        "trans": trans,
        "today": datetime.now().date(),
    })


@login_required
def trans_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(_cu_rp_qs(entity), pk=pk)

    if trans.journal_entry_id:
        messages.warning(
            request,
            "This transaction has been posted to journals. Reverse the entry first.",
        )
        return redirect("CreditUnion:trans_view", entity.slug, trans.pk)

    if request.method == "POST":
        with transaction.atomic():
            trans.delete()
        messages.success(request, f"Transaction {trans.trans_no} deleted.")
        return redirect("CreditUnion:trans_create", entity.slug)

    return render(request, "CreditUnion/trans_delete.html", {
        "entity": entity,
        "trans": trans,
    })


@login_required
def trans_pdf(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(_cu_rp_qs(entity), pk=pk)
    cfg = getattr(entity, "config", None)

    columns = [Col("Field", 40, "left"), Col("Value", 60, "left")]

    fields = [
        ("Reference No",     trans.rec_vou_no or ""),
        ("Type",             trans.trans_type or ""),
        ("Date",             trans.date.strftime("%d/%m/%Y") if trans.date else ""),
        ("Amount",           f"₵{trans.amount:,.2f}" if trans.amount else ""),
        ("Payment Mode",     trans.pay_mode or ""),
        ("Party",            trans.member_name or trans.non_member_name or ""),
        ("Non-Member Contact", trans.non_member_contact or ""),
        ("Ledger Account",   f"{trans.ledger_code} {trans.ledger_name}".strip()),
        ("Details",          trans.details or ""),
        ("Bank",             trans.bank or ""),
        ("Bank Branch",      trans.bank_branch or ""),
        ("Bank Account No",  trans.bank_no or ""),
        ("Cheque No",        trans.cheque_no or ""),
        ("Cheque Date",      trans.cheque_date.strftime("%d/%m/%Y") if trans.cheque_date else ""),
        ("MoMo No",          trans.momo_no or ""),
        ("MoMo Account Name", trans.momo_name or ""),
        ("Recorded By",      trans.created_by_name or trans.created_by_username or ""),
        ("Recorded On",      trans.created_at.strftime("%d/%m/%Y %H:%M") if trans.created_at else ""),
    ]

    pdf_bytes = build_report_pdf(
        entity=entity,
        entity_config=cfg,
        report_title=f"Transaction — {trans.rec_vou_no}",
        period_label="",
        columns=columns,
        rows=fields,
        totals=None,
        filename=f"trans_{trans.pk}.pdf",
    )
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="trans_{trans.pk}.pdf"'
    return resp


@login_required
def trans_excel(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(_cu_rp_qs(entity), pk=pk)
    cfg = getattr(entity, "config", None)

    rows = [
        ["Reference No",      trans.rec_vou_no or ""],
        ["Type",              trans.trans_type or ""],
        ["Date",              trans.date.strftime("%d/%m/%Y") if trans.date else ""],
        ["Amount",            float(trans.amount or 0)],
        ["Payment Mode",      trans.pay_mode or ""],
        ["Party",             trans.member_name or trans.non_member_name or ""],
        ["Non-Member Contact", trans.non_member_contact or ""],
        ["Ledger Code",       trans.ledger_code or ""],
        ["Ledger Name",       trans.ledger_name or ""],
        ["Details",           trans.details or ""],
        ["Bank",              trans.bank or ""],
        ["Bank Branch",       trans.bank_branch or ""],
        ["Bank Account No",   trans.bank_no or ""],
        ["Cheque No",         trans.cheque_no or ""],
        ["Cheque Date",       trans.cheque_date.strftime("%d/%m/%Y") if trans.cheque_date else ""],
        ["MoMo No",           trans.momo_no or ""],
        ["MoMo Account Name", trans.momo_name or ""],
        ["Recorded By",       trans.created_by_name or trans.created_by_username or ""],
        ["Recorded On",       trans.created_at.strftime("%d/%m/%Y %H:%M") if trans.created_at else ""],
    ]

    return render_excel(
        ["Field", "Value"], rows,
        filename=f"trans_{trans.pk}.xlsx",
        sheet_name="Transaction",
        title=(cfg.organization_name if cfg else "Transaction"),
        subtitle=trans.rec_vou_no or "",
    )


from djan_led.models import EntityConfig
from .forms import CreditUnionConfigForm


## ===========================For Images =======================
@login_required
def member_image_detail(request, slug, pk):
    """Display member details"""
    member = get_object_or_404(Master, pk=pk)
    
    context = {
        'member': member,
    }
    return render(request, 'CreditUnion/member_image_detail.html', context)


@login_required
def member_single_setting(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)

    member = get_object_or_404(Master, pk=pk)
    if request.method == 'POST':
        # Update member fields from POST data
        old_sav_rate = member.sav_int_rate
        old_loan_rate = member.loan_int_rate
        old_defer = member.sav_defer_int_appl

        member.sav_int_rate = request.POST.get('sav_int_rate', 0)
        member.loan_int_rate = request.POST.get('loan_int_rate', 0)
        member.sav_defer_int_appl = request.POST.get(
            'sav_defer_int_appl') == 'on'

        # Update audit fields if changed
        if member.sav_int_rate != old_sav_rate:
            member.sav_int_rate_date = timezone.now()
            member.sav_int_rate_user = request.user
        if member.loan_int_rate != old_loan_rate:
            member.loan_int_rate_date = timezone.now()
            member.loan_int_rate_user = request.user

        member.save()
        messages.success(request, f"Settings updated for {member.full_name}")
        return redirect('CreditUnion:member_list_manage', slug=entity.slug)

    context = {
        'member': member,
        'today': timezone.now(),
        'user': request.user,
    }
    return render(request, 'CreditUnion/member_single_setting.html', context)


@login_required
def member_images(request, slug, pk=None):
    """Manage member images - with search first"""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = None

    # If pk is provided, get that member
    if pk:
        member = get_object_or_404(Master, pk=pk)

    # Handle search
    search_query = request.GET.get("search", "")
    search_results = []

    if search_query:
        search_results = Master.objects.filter(
            Q(full_name__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(id__icontains=search_query)
        ).filter(entity=entity, is_deleted=False)[:20]

    # Handle POST (image upload)
    if request.method == "POST" and member:
        # Handle image uploads
        if "profile_image" in request.FILES:
            member.profile_image = request.FILES["profile_image"]
            member.save()
            messages.success(request, "Profile image uploaded successfully!")

        if "signature" in request.FILES:
            member.signature = request.FILES["signature"]
            member.save()
            messages.success(request, "Signature uploaded successfully!")

        if "id_card_front" in request.FILES:
            member.id_card_front = request.FILES["id_card_front"]
            member.save()
            messages.success(request, "ID card front uploaded successfully!")

        if "id_card_back" in request.FILES:
            member.id_card_back = request.FILES["id_card_back"]
            member.save()
            messages.success(request, "ID card back uploaded successfully!")

        return redirect("CreditUnion:member_images", entity.slug, member.id)

    context = {
        "member": member,
        "search_query": search_query,
        "search_results": search_results,
    }
    return render(request, "CreditUnion/member_images.html", context)


@login_required
def delete_member_image(request, slug, pk, image_type):
    """Delete a specific image from a member"""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Master, pk=pk, is_deleted=False)

    if request.method == "POST":
        image_field = None
        image_name = ""

        if image_type == "profile":
            image_field = member.profile_image
            image_name = "profile image"
        elif image_type == "signature":
            image_field = member.signature
            image_name = "signature"
        elif image_type == "id_front":
            image_field = member.id_card_front
            image_name = "ID card front"
        elif image_type == "id_back":
            image_field = member.id_card_back
            image_name = "ID card back"

        if image_field:
            # Get the file path for logging (optional)
            file_path = image_field.path if hasattr(image_field, "path") else None

            # Delete the file and clear the field
            image_field.delete()  # This deletes file AND clears field

            # Optional: Log the deletion
            print(
                f"Deleted {image_name} for member {member.full_name} (ID: {member.id})"
            )
            if file_path:
                print(f"File deleted: {file_path}")

            messages.success(
                request, f"{image_name.capitalize()} deleted successfully!"
            )
        else:
            messages.warning(request, f"No {image_name} found to delete")

        member.save()
        
        return redirect("CreditUnion:view_member_images", pk=member.id)
    
    return redirect("creditUnion:view_member_images", pk=member.id)

@login_required
def view_member_images(request, slug, pk):
    """View-only display of member images (no upload/delete)"""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Master, pk=pk, is_deleted=False)
    
    context = {
        'member': member,
    }
    return render(request, 'CreditUnion/view_member_images.html', context)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django_ledger.models import EntityModel

from .models import CreditUnionConfig
from .forms import CreditUnionConfigForm


@login_required
def credit_union_config_edit(request, slug):
    """
    Supervisor-facing form to edit this entity's CU config.
    Creates the row on first save if it doesn't exist.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # guard: only CU entities
    cfg = getattr(entity, "config", None)
    if not cfg or cfg.entity_type != "credit_union":
        messages.error(request, f"{entity.name} is not a credit union.")
        return redirect("CreditUnion:credit_union_dashboard", slug=slug)

    cu = getattr(entity, "cu_config", None)
    is_new = cu is None

    if request.method == "POST":
        form = CreditUnionConfigForm(request.POST, instance=cu)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.entity = entity
            obj.save()
            messages.success(
                request,
                f"{'Created' if is_new else 'Updated'} configuration "
                f"for {entity.name}."
            )
            return redirect("CreditUnion:credit_union_config_edit", slug=slug)
    else:
        form = CreditUnionConfigForm(instance=cu)

    return render(request, "CreditUnion/credit_union_config_edit.html", {
        "entity": entity,
        "form":   form,
        "is_new": is_new,
        "cu":     cu,
    })
