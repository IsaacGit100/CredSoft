# utils.py
import io
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import xlsxwriter
from .models import Trans
from datetime import date
from django.utils import timezone

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    
    try:
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
    except Exception as e:
        print(f"PDF generation error: {e}")
    
    return None

def export_transactions_excel(transactions):
    output = io.BytesIO()
    
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Transactions')
    
    # Define formats
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    money_format = workbook.add_format({'num_format': '#,##0.00'})
    
    # Write headers
    headers = ['Date', 'Trans No', 'Type', 'Member Name', 'Non-Member Name', 
               'Purpose', 'Amount', 'Pay Mode', 'Details']
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Write data
    for row, trans in enumerate(transactions, start=1):
        worksheet.write(row, 0, trans.date, date_format)
        worksheet.write(row, 1, trans.trans_no)
        worksheet.write(row, 2, trans.trans_type)
        worksheet.write(row, 3, trans.member_name)
        worksheet.write(row, 4, trans.non_member_name)
        worksheet.write(row, 5, trans.purpose)
        worksheet.write(row, 6, float(trans.amount), money_format)
        worksheet.write(row, 7, trans.pay_mode)
        worksheet.write(row, 8, trans.details)
    
    # Adjust column widths
    worksheet.set_column('A:A', 12)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 10)
    worksheet.set_column('D:E', 20)
    worksheet.set_column('F:F', 15)
    worksheet.set_column('G:G', 12)
    worksheet.set_column('H:H', 10)
    worksheet.set_column('I:I', 25)
    
    workbook.close()
    
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=transactions.xlsx'
    
    return response


from datetime import datetime, time, date
from decimal import Decimal
from django.contrib.auth.models import User


from decimal import Decimal
from django.utils import timezone


def post_trans_to_ledger(trans):
    """
    Create a Journal Entry in django-ledger from a Trans record.
    Returns the JournalEntry UUID or None if fails.
    
    """
    from django_ledger.models import EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel
    try:
        # 1. Get entity
        if hasattr(trans, 'entity') and trans.entity:
            entity = trans.entity
        else:
            user = trans.created_by
            if hasattr(user, 'djan_led_profile'):
                profile = user.djan_led_profile
                entity = profile.default_entity
            else:
                print(" User has no profile or default entity.")
                return None
        if not entity:
            print(" No entity found for transaction.")
            return None

        # 2. Convert date → timezone‑aware datetime
        if isinstance(trans.date, datetime):
            if timezone.is_naive(trans.date):
                entry_datetime = timezone.make_aware(trans.date)
            else:
                entry_datetime = trans.date
        elif isinstance(trans.date, date):
            naive = datetime.combine(trans.date, time.min)
            entry_datetime = timezone.make_aware(naive)
        else:
            naive = datetime.strptime(str(trans.date), '%Y-%m-%d')
            entry_datetime = timezone.make_aware(naive)

        print(f" Entry datetime: {entry_datetime} (type: {type(entry_datetime)})")

        # 3. Get or create ledger
        ledger = LedgerModel.objects.filter(entity=entity).first()
        if not ledger:
            ledger = LedgerModel.objects.create(entity=entity, name='Default Ledger')
            
            
            
        # 4. Find the target account (the one selected in the transaction)
        target_account = None
        if trans.ledger_code:
            try:
                target_account = AccountModel.objects.get(coa_model__entity=entity, code=trans.ledger_code)
            except AccountModel.DoesNotExist:
                print(f" Account with code '{trans.ledger_code}' not found, trying by name.")
        if not target_account and trans.ledger_name:
            # Try to find by name (case‑insensitive)
            accounts = AccountModel.objects.filter(
                coa_model__entity=entity,
                name__icontains=trans.ledger_name
            )
            if accounts.count() == 1:
                target_account = accounts.first()
            elif accounts.count() > 1:
                print(f" Multiple accounts found for '{trans.ledger_name}', using first.")
                target_account = accounts.first()
            else:
                print(f" No account found for '{trans.ledger_name}'.")

        if not target_account:
            print(f" Target account not found for trans: ledger_code='{trans.ledger_code}', ledger_name='{trans.ledger_name}'")
            return None

        # 5. Find the Cash/Bank account (for the opposite side)
        # Try to find a Cash or Bank account
        cash_account = AccountModel.objects.filter(
            coa_model__entity=entity,
            code__in=['1010', '1020', '1211', '1212']
        ).first()
        if not cash_account:
            # Fallback: find any asset account with 'Cash' or 'Bank' in name
            cash_account = AccountModel.objects.filter(
                coa_model__entity=entity,
                name__icontains='Cash'
            ).first()
        if not cash_account:
            cash_account = AccountModel.objects.filter(
                coa_model__entity=entity,
                name__icontains='Bank'
            ).first()

        if not cash_account:
            print(" No Cash/Bank account found. Please create one (code: 1010, 1020, 1211, or 1212).")
            return None

        # 6. Determine which account is debit and which is credit
        if trans.trans_type == 'Receipts':
            # Receipt: Debit Cash, Credit Target
            debit_account = cash_account
            credit_account = target_account
        else:  # Payments
            # Payment: Debit Target, Credit Cash
            debit_account = target_account
            credit_account = cash_account

        # 7. Create Journal Entry (posted=False)
        je = JournalEntryModel.objects.create(
            ledger=ledger,
            timestamp=entry_datetime,
            description=trans.details or f"Trans #{trans.trans_no}",
            posted=False,
        )

        # 8. Create TWO transactions (debit + credit)
        TransactionModel.objects.create(
            journal_entry=je,
            account=debit_account,
            amount=trans.amount,
            tx_type='debit'
        )
        TransactionModel.objects.create(
            journal_entry=je,
            account=credit_account,
            amount=trans.amount,
            tx_type='credit'
        )

        # 9. Post the entry (this will validate that debits = credits)
        je.posted = True
        je.save()

        # 10. Update Trans
        trans.journal_entry_id = je.uuid
        trans.journal_status = 'POSTED'
        trans.save()

        print(f" Posted transaction #{trans.id} - Journal Entry {je.uuid}")
        return je.uuid

    except Exception as e:
        print(f" Error in post_trans_to_ledger: {e}")
        import traceback
        traceback.print_exc()
        return None
