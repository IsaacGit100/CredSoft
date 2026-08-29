
from decimal import Decimal
from datetime import date
from .models import StateAndy  # your source model
from MembersApp.models import Master
from django.contrib import messages
from django.shortcuts import render
from datetime import datetime

from AndyApp.models import Mastandy, StateAndy
from RecPayApp.models import Trans

from Supervisor.views import member_list_delete
from django.core.exceptions import ObjectDoesNotExist
from coa.models import ChartOfAccounts
from UserAuth.models import User
from django.shortcuts import render, redirect

from django.utils import timezone


# Get today's date safely (timezone-aware)
today_date = timezone.now().date()

# Create your views here.


def andy_home(request, slug):
    return render(request, 'AndyApp/andy_home.html')


def master_list(request, slug):
    masts = Mastandy.objects.all()
    return render(request, 'AndyApp/master_list.html', {'masts': masts})


def trans_update(request, slug):
    if request.method == 'POST':
        states = StateAndy.objects.all()
        cnt = states.count()
        print(cnt)
        tot_trans_cnt = 0
        receipt_cnt = 0
        receipt_amt = Decimal('0.00')
        payments_cnt = 0
        payments_amt = Decimal('0.00')
        
        
        
        for state in states:
            
            # Get member
            try:
                master = Master.objects.get(pk=state.master_id)
                master_name = master.full_name
                master_id = master
            except ObjectDoesNotExist:
                master_name = 'Name Does Not Exist'
                master = None
                
            m_old_trans_id = 0    
            m_old_trans_id = state.id
            
            # Determine ledger details
            if state.state_code == 'Savings' or state.state_code == 'savings_interest' or state.state_code == 'Savings_interest':
                m_ledger_id = 19
                m_ledger_code = '20101001'
                m_ledger_name = 'Savings Deposit'
                m_details = ''
            elif state.state_code == 'Withdrawal' or state.state_code == 'Withdrawals':
                m_ledger_id = 20
                m_ledger_code = '20101002'
                m_ledger_name = 'Savings Withdrawal'
                m_details = ''
            elif state.state_code == 'Shares':
                m_ledger_id = 23
                m_ledger_code = '20101001'
                m_ledger_name = 'Share Capital'
                m_details = ''
            elif state.state_code == 'Shares Withdrawal':
                m_ledger_id = 24
                m_ledger_code = '20101002'
                m_ledger_name = 'Share Withdrawal'
                m_details = ''
            elif state.state_code == 'Savings Interest' or state.state_code == 'savings_interest':
                m_ledger_id = 21
                m_ledger_code = '20101003'
                m_ledger_name = 'Savings Interest'
                m_details = ''
            elif state.state_code == 'B/F':
                m_ledger_id = 23
                m_ledger_code = '20101001'
                m_ledger_name = 'Savings Deposit'
                m_details = 'B/F'
            else:
                m_ledger_id = 0
                m_ledger_code = '99999999'
                m_ledger_name = state.state_code
                m_details = 'No Records Identified'

            # Determine transaction type
            if state.trans_type == 'cr' or state.trans_type == 'Cr':
                m_trans_type = 'Receipts'
                m_rec_vou_no = f'REC:{state.rec_no}'
                receipt_cnt += 1
                receipt_amt += state.amount
                
            elif state.trans_type == 'dr' or state.trans_type == 'Dr':
                m_trans_type = 'Payments'
                m_rec_vou_no = f'VOU:{state.rec_no}'
                payments_cnt += 1
                payments_amt += state.amount
            else:
                m_trans_type = state.trans_type
                m_rec_vou_no = f'UNK:{state.rec_no}'

            tot_trans_cnt += 1

            # Create Trans 
            print(f"Old Trans ID: {m_old_trans_id} News Trans ID: {state.id}, Name: {master_name}, Ledger Name: {m_ledger_name}")
            Trans.objects.create(
                old_trans_id = m_old_trans_id,
                status='DRAFT',
                rec_vou_no=m_rec_vou_no,
                date=state.date,
                amount=state.amount,
                trans_no=state.rec_no,
                trans_type=m_trans_type,
                
                member_no=master,
                member=master,
                member_name=master_name,
                
                non_member_name='',
                non_member_contact='',
                
                bank_date=None,
                bank='',
                bank_no='',
                bank_branch='',
                cheque_date=None,
                cheque_no='',
                
                momo_no='',
                momo_name='',
                
                pay_mode='Cash',
                
                ledger_id=m_ledger_id,
                ledger_code=m_ledger_code,
                ledger_name=m_ledger_name,
                details=m_details,
                purpose=m_ledger_name,
                other_purpose='',
                loan=None,
                loan_name='',
                posted_at=None,
                created_at=timezone.now(),
                created_by=None,   # or a User instance if you have a migration user
                updated_at=timezone.now(),
                updated_by=None,
                created_by_name='Migration',
                created_by_username='Migration',

            )

        # After loop, show summary
        messages.success(
            request, f'Successfully copied {tot_trans_cnt} records from AndyState to Trans!')
        context = {
            'tot_trans_cnt': tot_trans_cnt,
            'receipt_cnt': receipt_cnt,
            'receipt_amt': receipt_amt,
            'payments_cnt': payments_cnt,
            'payments_amt': payments_amt,
        }
        return render(request, 'AndyApp/transfer_complete.html', context)

    # GET request – show confirmation form
    return render(request, 'AndyApp/confirm_transfer.html')


  





   
   

    