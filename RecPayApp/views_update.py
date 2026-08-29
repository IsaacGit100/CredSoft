from django.shortcuts import render
from django.db import models

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Q, Count, F
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from decimal import Decimal

import re
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from django.core.paginator import Paginator

from django import template
register = template.Library()

import json

## Import Tables
from .models import Trans
from MembersApp.models import Master
from UserAuth.models import User
from coa.models import ChartOfAccounts
from LoanApp.models import Loan
from SysSetup.models import SystemSettings

## Import Views
from . import views
from . import views_pdf
from . import views_excel


def update_trans(request):
    trans = Trans.objects.select_related('master').order_by('id')
    sys_set = SystemSettings.objects.first()
    
    today = date.today()
    last_proc_date = sys_set.last_trans_proc_date
    
    deposit = master.tot_deposits or Decimal(0.00)
    amount = trans.amount or Decimal(0.00)
     
    today = timezone.now()
          


def Loan_Repayment(request):
    trans=trans.objects.all()
    if request.method == 'POST':
        
        amount_str = request.POST.get('amount', '0').strip()
        amount_clean = amount_str.replace(',', '').replace(' ', '')
        amount = Decimal(amount_clean)
        
        if trans.ledger_name == 'Loan_Repayments':
            loans = trans.loans
            loan_int = loans.int_calc
            if amount >= loan_int:
                loans.tot_int = loans.tot_int + loan_int
                amt_left = amount - loans.tot_int
                loans.tot_ded = loans.tot_ded + amt_left
            else:
                loans.tot_int = loans.tot_int + amount
        
  
        
        