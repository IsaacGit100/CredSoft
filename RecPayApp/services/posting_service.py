# services/services_trans_posting.py
# NO top-level model imports! All imports are inside methods.

from decimal import Decimal
from django.db import transaction as db_transaction
from django.db.models.functions import JSONArray
from django.utils import timezone

from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import datetime
from RecPayApp.models import Trans
from FinanceApp.models import JournalEntry, JournalLine, GeneralLedger
from coa.models import ChartOfAccounts
from MembersApp.models import Master
from LoanApp.models import Loan, LoanTransaction, LoanRepayment


class TransactionPostingService:
    """
    Transaction Posting Service - Handles all accounting entries
    """

    def __init__(self, transaction, user):
        self.transaction = transaction
        self.user = user
        self.results = {
            'success': False,
            'errors': [],
            'journal_entry': None,
            'journal_lines': [],
            'member_update': None,
            'state_trans': None,
            'state_update': None,
        }

    def process(self):
        """Process the transaction posting"""
        if self.transaction.status == 'POSTED':
            self.results['success'] = True
            self.results['message'] = "Transaction already posted."
            return self.results
        try:
            print(f"\n{'='*60}")
            print(f"POSTING TRANSACTION: {self.transaction.rec_vou_no}")
            print(f"{'='*60}")

            with db_transaction.atomic():

                # Step 1: Get the GL Account
                gl_account = self._get_gl_account()
                if not gl_account:
                    error_msg = f"Account {self.transaction.ledger_code} not found"
                    print(f"❌ {error_msg}")
                    self.results['errors'].append(error_msg)
                    return self.results

                # Step 2: Get Cash Account
                cash_account = self._get_cash_account()
                if not cash_account:
                    error_msg = f"Cash account not found for mode: {self.transaction.pay_mode}"
                    print(f"❌ {error_msg}")
                    self.results['errors'].append(error_msg)
                    return self.results

                print(f"✓ Cash account: {cash_account.accountno} - {cash_account.name}")

                # Step 3: Create Journal Entry
                journal = self._create_journal_entry()
                self.results['journal_entry'] = journal
                print(f"✓ Created journal: {journal.entry_number}")

                # Step 4: Create Journal Lines
                if self.transaction.trans_type == 'Receipts':
                    lines = self._create_receipt_lines(journal, gl_account, cash_account)
                else:
                    lines = self._create_payment_lines(journal, gl_account, cash_account)

                self.results['journal_lines'] = lines
                print(f"✓ Created {len(lines)} journal lines")

                # Step 5: Update General Ledger
                self._update_ledger(journal)
                print(f"✓ Updated general ledger")

                # Step 6: Update Member Balance
                member_update = self._update_member_balance()
                self.results['member_update'] = member_update
                print(f"✓ Updated member balance")
                
                # Step 6b: Update Loan and Loan_Repayment Tables
                self._update_loan_table()
                print(f"✓ Updated loan table")

                # Step 7: Create State Transaction Record
                state_trans = self._create_state_trans()
                self.results['state_trans'] = state_trans
                print(f"✓ Created state transaction record")

                # Step 8: Create State Update Record (based on member_update)
                state_update = self._create_state_update(member_update)
                self.results['state_update'] = state_update
                print(f"✓ Created state update record")

                # Step 9: Archive journal to state tables (if models exist)
                self._archive_journal(journal)
                print(f"✓ Archived journal to state tables")

                # Step 10: Update Transaction Status
                self.transaction.status = 'POSTED'
                self.transaction.posted_at = timezone.now()
                self.transaction.save()
                print(f"✓ Transaction marked as POSTED")

                self.results['success'] = True
                print(f"\n✅ SUCCESS: Transaction {self.transaction.rec_vou_no} posted!")
                print(f"{'='*60}\n")
                return self.results

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            self.results['errors'].append(str(e))
            return self.results

    # --------------------------------------------------------------------------
    # Private methods – imports are inside each method to avoid AppRegistryNotReady
    # --------------------------------------------------------------------------

    def _get_gl_account(self):
        """Get GL account from ChartOfAccounts"""
        from coa.models import ChartOfAccounts

        try:
            return ChartOfAccounts.objects.get(accountno=self.transaction.ledger_code)
        except ChartOfAccounts.DoesNotExist:
            return None

    def _get_cash_account(self):
        """Get cash account based on payment mode"""
        from coa.models import ChartOfAccounts

        account_map = {
            'Cash': '10101001',
            'Cheque': '10102001',
            'Transfer': '10103001',
        }
        account_code = account_map.get(self.transaction.pay_mode, '10101001')
        try:
            return ChartOfAccounts.objects.get(accountno=account_code)
        except ChartOfAccounts.DoesNotExist:
            return None

    def _create_journal_entry(self):
        """Create journal entry header"""
        from FinanceApp.models import JournalEntry
        from datetime import datetime

        date_str = datetime.now().strftime('%Y%m%d')
        last_journal = JournalEntry.objects.filter(
            entry_number__startswith=f'JV-{date_str}'
        ).count()
        entry_number = f'JV-{date_str}-{last_journal + 1:04d}'

        journal = JournalEntry.objects.create(
            entry_number=entry_number,
            entry_date=self.transaction.date,
            description=f"{self.transaction.trans_type}: {self.transaction.details or self.transaction.ledger_name}",
            source_trans=self.transaction,
            status='POSTED',
            posted=True,
            posted_at=timezone.now(),
            posted_by=self.user
        )
        return journal

    def _create_receipt_lines(self, journal, gl_account, cash_account):
        """Create journal lines for receipt (money coming in)"""
        from FinanceApp.models import JournalLine

        lines = []
        # Debit: Cash account
        debit_line = JournalLine.objects.create(
            journal=journal,
            account=cash_account,
            member=self.transaction.member,
            debit=self.transaction.amount,
            credit=0,
            line_description=f"Cash received from {self._get_party_name()}"
        )
        lines.append(debit_line)

        # Credit: GL Account
        credit_line = JournalLine.objects.create(
            journal=journal,
            account=gl_account,
            member=self.transaction.member,
            debit=0,
            credit=self.transaction.amount,
            line_description=f"Credit to {gl_account.name}"
        )
        lines.append(credit_line)
        return lines

    def _create_payment_lines(self, journal, gl_account, cash_account):
        """Create journal lines for payment (money going out)"""
        from FinanceApp.models import JournalLine

        lines = []
        # Debit: GL Account
        debit_line = JournalLine.objects.create(
            journal=journal,
            account=gl_account,
            member=self.transaction.member,
            debit=self.transaction.amount,
            credit=0,
            line_description=f"Payment for {gl_account.name}"
        )
        lines.append(debit_line)

        # Credit: Cash account
        credit_line = JournalLine.objects.create(
            journal=journal,
            account=cash_account,
            member=self.transaction.member,
            debit=0,
            credit=self.transaction.amount,
            line_description=f"Cash paid to {self._get_party_name()}"
        )
        lines.append(credit_line)
        return lines

    def _get_party_name(self):
        """Get the party name (member or non-member)"""
        if self.transaction.member:
            return self.transaction.member.full_name
        return self.transaction.non_member_name or "Unknown"

    def _update_ledger(self, journal):
        """Update general ledger balances"""
        from FinanceApp.models import GeneralLedger

        for line in journal.lines.all():
            ledger, created = GeneralLedger.objects.get_or_create(
                account=line.account,
                defaults={'current_balance': 0}
            )

            if line.debit > 0:
                # Debit increases Assets and Expenses, decreases Liabilities and Income
                if line.account.account_type in ['ASSET', 'EXPENSE']:
                    ledger.current_balance += line.debit
                else:
                    ledger.current_balance -= line.debit
            else:
                # Credit increases Liabilities and Income, decreases Assets and Expenses
                if line.account.account_type in ['LIABILITY', 'INCOME', 'EQUITY']:
                    ledger.current_balance += line.credit
                else:
                    ledger.current_balance -= line.credit

            ledger.save()

    def _update_member_balance(self):
        """Update member's stored balance fields (savings, shares, loans)"""
        if not self.transaction.member:
            return None

        member = self.transaction.member
        ledger_name = self.transaction.ledger_name.lower() if self.transaction.ledger_name else ''

        old_values = {
            'tot_deposits': member.tot_deposits or 0,
            'tot_deposit_withdrawal': member.tot_deposit_withdrawal or 0,
            'tot_shares': member.tot_shares or 0,
            'tot_shares_withdrawal': member.tot_shares_withdrawal or 0,
            'tot_dividend': member.tot_dividend or 0,
            'tot_dividend_withdrawal': member.tot_dividend_withdrawal or 0,
            'enrollment_fees': member.enrollment_fees or 0,
            'tot_interest_accrued': member.tot_interest_accrued or 0,
            'sav_avail_bal': member.sav_avail_bal if hasattr(member, 'sav_avail_bal') else 0,
        }

        # Update based on ledger name
        if 'savings deposit' in ledger_name:
            member.tot_deposits = (member.tot_deposits or 0) + self.transaction.amount
            print(f"  → Updated tot_deposits: {old_values['tot_deposits']} → {member.tot_deposits}")
        elif 'savings withdrawal' in ledger_name:
            member.tot_deposit_withdrawal = (member.tot_deposit_withdrawal or 0) + self.transaction.amount
            print(f"  → Updated tot_deposit_withdrawal: {old_values['tot_deposit_withdrawal']} → {member.tot_deposit_withdrawal}")
        elif 'shares' in ledger_name and 'withdrawal' not in ledger_name:
            member.tot_shares = (member.tot_shares or 0) + self.transaction.amount
            print(f"  → Updated tot_shares: {old_values['tot_shares']} → {member.tot_shares}")
        elif 'shares withdrawal' in ledger_name:
            member.tot_shares_withdrawal = (member.tot_shares_withdrawal or 0) + self.transaction.amount
            print(f"  → Updated tot_shares_withdrawal: {old_values['tot_shares_withdrawal']} → {member.tot_shares_withdrawal}")
        elif 'dividend' in ledger_name and 'withdrawal' not in ledger_name:
            member.tot_dividend = (member.tot_dividend or 0) + self.transaction.amount
            print(f"  → Updated tot_dividend: {old_values['tot_dividend']} → {member.tot_dividend}")
        elif 'dividend withdrawal' in ledger_name:
            member.tot_dividend_withdrawal = (member.tot_dividend_withdrawal or 0) + self.transaction.amount
            print(f"  → Updated tot_dividend_withdrawal: {old_values['tot_dividend_withdrawal']} → {member.tot_dividend_withdrawal}")
        elif 'enrollment fees' in ledger_name:
            member.enrollment_fees = (member.enrollment_fees or 0) + self.transaction.amount
            print(f"  → Updated enrollment_fees: {old_values['enrollment_fees']} → {member.enrollment_fees}")
        elif 'loan_disbursements' in ledger_name:
            member.loan_last_disb_princ = self.transaction.amount
            member.loan_last_disb_date = self.transaction.date
            member.loan_disb_tot = (member.loan_disb_tot or 0) + self.transaction.amount
            member.loan_disb_cnt = (member.loan_disb_cnt or 0) + 1
            member.loan_last_id = self.transaction.loan_id
            print(f"  → Updated loan_disbursements: {self.transaction.amount}")
        elif 'loan_repayments' in ledger_name:
            member.loan_last_repayment_amt = self.transaction.amount
            member.loan_last_repayment_date = self.transaction.date
            member.loan_tot_repayment = (member.loan_tot_repayment or 0) + self.transaction.amount
            member.loan_repayment_cnt = (member.loan_repayment_cnt or 0) + 1
            member.loan_last_repayment_id = self.transaction.loan_id
            print(f"  → Updated loan_repayments: {self.transaction.amount}")

        member.save()

        new_values = {
            'tot_deposits': member.tot_deposits or 0,
            'tot_deposit_withdrawal': member.tot_deposit_withdrawal or 0,
            'tot_shares': member.tot_shares or 0,
            'tot_shares_withdrawal': member.tot_shares_withdrawal or 0,
            'tot_dividend': member.tot_dividend or 0,
            'tot_dividend_withdrawal': member.tot_dividend_withdrawal or 0,
            'enrollment_fees': member.enrollment_fees or 0,
            'tot_interest_accrued': member.tot_interest_accrued or 0,
            'sav_avail_bal': member.sav_avail_bal if hasattr(member, 'sav_avail_bal') else 0,
        }

        return {
            'member_id': member.id,
            'member_name': member.full_name,
            'old_values': old_values,
            'new_values': new_values,
            'amount': self.transaction.amount,
            'ledger_name': self.transaction.ledger_name
        }

    def _create_state_trans(self):
        """Create State Transaction record for audit"""
        from services.models import StateTrans
        
        state_trans = StateTrans.objects.create(
            state_date=timezone.now(),
            rec_vou_no=self.transaction.rec_vou_no,
            trans_no=self.transaction.trans_no,
            date=self.transaction.date,
            trans_type=self.transaction.trans_type, 
            amount=self.transaction.amount,
            pay_mode=self.transaction.pay_mode,
            loan=self.transaction.loan,
            master=self.transaction.member,
            non_member_name=self.transaction.non_member_name or '',
            non_member_contact=self.transaction.non_member_contact or '',
            bank_date=self.transaction.bank_date,
            bank=self.transaction.bank or '',
            bank_no=self.transaction.bank_no or '',
            bank_branch=self.transaction.bank_branch or '',
            cheque_date=self.transaction.cheque_date,
            cheque_no=self.transaction.cheque_no or '',
            momo_no=self.transaction.momo_no or '',
            momo_name=self.transaction.momo_name or '',
            ledger_id=self.transaction.ledger_id or '',
            ledger_code=self.transaction.ledger_code or '',
            ledger_name=self.transaction.ledger_name or '',
            purpose=self.transaction.purpose or '',
            details=self.transaction.details or '',
            posted_at=self.transaction.posted_at,
            created_at=self.transaction.created_at,
            created_by=self.transaction.created_by,
            updated_at=self.transaction.updated_at,
            updated_by=self.transaction.updated_by,
            
            created_by_who_id=self.transaction.created_by_id,
            created_by_name=self.transaction.created_by_name,
            created_by_username=self.transaction.created_by_username,
            
            
        )
        return state_trans
    
    
    def _create_state_update(self, member_update):
        """Create State Update record for audit trail (uses only existing fields)"""
        from services.models import StateUpdate

        if not member_update:
            return None

        old = member_update['old_values']
        new = member_update['new_values']

        # Build only the fields that exist in StateUpdate (from your earlier model definition)
        state_update = StateUpdate.objects.create(
            state_update_date=timezone.now(),
            trans_amount=self.transaction.amount,
            
            ledger_id=self.transaction.ledger_id or '',
            ledger_code=self.transaction.ledger_code or '',
            ledger_name=self.transaction.ledger_name or '',
            
            
            old_shares=old.get('tot_shares', 0),
            new_shares=new.get('tot_shares', 0),
            old_shares_withdrawal=old.get('tot_shares_withdrawal', 0),
            new_shares_withdrawal=new.get('tot_shares_withdrawal', 0),
            old_deposit=old.get('tot_deposits', 0),
            new_deposit=new.get('tot_deposits', 0),
            old_deposit_withdrawal=old.get('tot_deposit_withdrawal', 0),
            new_deposit_withdrawal=new.get('tot_deposit_withdrawal', 0),
            old_dividend=old.get('tot_dividend', 0),
            new_dividend=new.get('tot_dividend', 0),
            old_dividend_withdrawal=old.get('tot_dividend_withdrawal', 0),
            new_dividend_withdrawal=new.get('tot_dividend_withdrawal', 0),
            old_enrollment_fees=old.get('enrollment_fees', 0),
            new_enrollment_fees=new.get('enrollment_fees', 0),
            old_int_accrued=old.get('tot_interest_accrued', 0),
            new_int_accrued=new.get('tot_interest_accrued', 0),
            old_available_balance=old.get('sav_avail_bal', 0),
            new_available_balance=new.get('sav_avail_bal', 0),
            created_at=timezone.now(),
            created_by=self.user,
            updated_at=timezone.now(),
            updated_by=self.user,
        )
        return state_update

    def _archive_journal(self, journal):
        """Copy journal entry and lines to state tables for permanent audit."""
        from services.models import StateJournalEntry, StateJournalLine

        StateJournalEntry.objects.create(
            original_id=journal.id,
            entry_number=journal.entry_number,
            entry_date=journal.entry_date,
            description=journal.description,
            source_trans_id=journal.source_trans.id if journal.source_trans else None,
            status=journal.status,
            posted=journal.posted,
            posted_at=journal.posted_at,
            posted_by_id=journal.posted_by.id if journal.posted_by else None,
        )

        for line in journal.lines.all():
            StateJournalLine.objects.create(
                original_id=line.id,
                journal_entry_number=journal.entry_number,
                account_code=line.account.accountno,
                member_id=line.member.id if line.member else None,
                debit=line.debit,
                credit=line.credit,
                line_description=line.line_description,
            )
    
    def _update_loan_table(self):
        """Update Loan table based on the transaction (disbursement or repayment)."""
        loan = self.transaction.loan
        if not loan:
            return

        ledger_name = self.transaction.ledger_name.lower() if self.transaction.ledger_name else ''

    # ---------- DISBURSEMENT ----------
        if 'loan disbursements' in ledger_name and loan.status == 'New Loan':
            loan.rec_vou_no = self.transaction.rec_vou_no
            loan.disbursement_date = self.transaction.date
            loan.status = 'Active'
            loan.loan_trans_amount = self.transaction.amount
            from dateutil.relativedelta import relativedelta
            loan.next_repayment_date = self.transaction.date + relativedelta(months=1)
            loan.save()
            print(f"✓ Updated Loan {loan.id}: disbursed, next repayment {loan.next_repayment_date}")
            return

        # ---------- REPAYMENT ----------
        if 'loan repayments' in ledger_name:
           
            old_balance = loan.loan_balance
            amount = self.transaction.amount
            remaining = amount

            # 1. Interest due (monthly)
        #    monthly_rate = (loan.interest_rate / 100) / 12
            interest_due = loan.due_interest
          

            # 2. Apply to interest first
            if interest_due > 0:
                if remaining >= interest_due:
                    loan.tot_int = (loan.tot_int or 0) + interest_due
                    loan.last_interest_paid = interest_due
                    
                    if remaining > loan.loan_balance:
                        loan_cred = remaining - loan.loan_balance 
                        loan.loan_credit_balance = loan_cred
                        loan.last_repayment_paid = loan.loan_balance
                        loan.tot_ded = (loan.tot_ded or 0) + loan.loan_balance
                        loan.loan_balance = 0
                        loan.status = "Credit"
                    else: 
                        remaining = remaining - interest_due  
                        loan.loan_balance = (loan.loan_balance or 0) - remaining
                        loan.last_repayment_paid = remaining
                        loan.tot_ded = (loan.tot_ded or 0) + remaining
                    
                    
                else:       # Amount Paid = Interest and Interest First
                    loan.tot_int = (loan.tot_int or 0) + remaining
                    loan.last_interest_paid = remaining
                    loan.last_repayment_paid = 0
                    loan.tot_ded = (loan.tot_ded or 0) + 0  # No Deduction because the amount paid is lower than interest and Interest First
                    remaining = 0

            # 3. Principal portion
            principal_paid = remaining
#            if principal_paid > 0:
#                loan.tot_ded = (loan.tot_ded or 0) + principal_paid
#                loan.loan_balance -= principal_paid
#                loan.last_repayment_paid = principal_paid

            # 4. Update last repayment info
            loan.last_repayment_date = self.transaction.date
            loan.last_repayment_amount = amount

            # 5. Update status if completed
            if loan.loan_balance <= 0:
                loan.status = 'Completed'
                loan.completion_date = self.transaction.date
                
            if loan.loan_credit_balance > 0:
                loan.status = 'Credit'
                
                
            loan.last_payment_date = self.transaction.date
            loan.save()

            # 6. Process guarantor redemptions (if any principal was paid)
            redeemed_details = []
            if principal_paid > 0:
                redeemed_details = self._update_guarantors(principal_paid, loan)

            # 7. Create audit record in LoanRepayment
            self._update_loan_repayment_table(loan, old_balance, redeemed_details)

            print(f"✓ Loan repayment processed: interest {interest_due:.2f}, principal {principal_paid:.2f}, new balance {loan.loan_balance:.2f}")
        
    
    
    
        def _process_loan_repayment(self):
            """
        Process a loan repayment transaction.
        Assumes self.transaction is a Receipt with ledger_name containing 'loan repayments'.
        """
        loan = self.transaction.loan
        if not loan:
            return

        amount = self.transaction.amount
        remaining = amount

        # 1. Calculate interest for the period (monthly)
        # Monthly interest rate = annual_rate / 100 / 12
        monthly_rate = (loan.interest_rate / 100) / 12
        interest_due = loan.loan_balance * monthly_rate

        # Interest portion
        if interest_due > 0:
            if remaining >= interest_due:
                loan.tot_int = (loan.tot_int or 0) + interest_due
                remaining -= interest_due
            else:
                loan.tot_int = (loan.tot_int or 0) + remaining
                remaining = 0

        # 2. Principal portion (remaining amount)
        principal_paid = remaining
        if principal_paid > 0:
    #        loan.tot_ded = (loan.tot_ded or 0) + principal_paid
    #        loan.loan_balance -= principal_paid

            # 3. Update guarantors – redeem proportionally
            self._update_guarantors(principal_paid, loan)

        # 4. Update loan status
        if loan.loan_balance <= 0:
            loan.status = 'Completed'
            loan.completion_date = self.transaction.date
        else:
            loan.status = 'Active'

        # 5. Update last repayment info
        loan.last_repayment_date = self.transaction.date
        loan.last_repayment_amount = amount

        loan.save()
        print(f"✓ Loan repayment processed: interest {interest_due:.2f}, principal {principal_paid:.2f}, new balance {loan.loan_balance:.2f}")
        
        
        

    def _update_guarantors(self, principal_paid, loan):
        """Distribute principal repayment among guarantors until fully redeemed."""
        
        from LoanApp.models import Guarantor

        guarantors = Guarantor.objects.filter(loan=loan, redeemed_status__in=['', 'Partial']).order_by('id')
        if not guarantors:
            return []

        remaining = principal_paid
        redeemed_details = []
        for guarantor in guarantors:
            if remaining <= 0:
                break
            guaranteed = guarantor.guaranteed_amount
            redeemed = guarantor.redeemed_amount or 0
            still_owing = guaranteed - redeemed
            if still_owing <= 0:
                continue
            to_redeem = min(remaining, still_owing)
            guarantor.redeemed_amount = redeemed + to_redeem
            remaining -= to_redeem
            if guarantor.redeemed_amount >= guaranteed:
                guarantor.redeemed_status = 'Redeemed'
            else:
                guarantor.redeemed_status = 'Partial'
            guarantor.save()
            redeemed_details.append({
                'guarantor_id': guarantor.id,
                'master_id': guarantor.master.id,
                'loan_id': loan.id,
                'master_name': guarantor.master.full_name,
                'guaranteed_amount': float(guaranteed),
                'redeemed_amount': float(guarantor.redeemed_amount),
                'redeemed_in_this_transaction': float(to_redeem),
            })
            print(f"  → Guarantor {guarantor.master.full_name} redeemed ₵{to_redeem:.2f}")
        return redeemed_details
               
    def _update_loan_repayment_table(self, loan, old_balance, guarantor_details):
        """Create an audit record for a loan repayment."""
        from LoanApp.models import LoanRepayment

        loan_repay = LoanRepayment.objects.create(
            loan=loan,
            master=loan.master,
            trans=self.transaction,
            trans_amount=self.transaction.amount,
            trans_date=self.transaction.date,
            old_loan_balance=old_balance,
            new_loan_balance=loan.loan_balance,
            gua_redeemed_details=guarantor_details,
            interest_paid=loan.last_interest_paid if hasattr(loan, 'last_interest_paid') else 0,
            repayment_paid=loan.last_repayment_paid if hasattr(loan, 'last_repayment_paid') else 0,
            payment_date=self.transaction.date,
            notes=f"Loan repayment for {self.transaction.date}",
            created_by=self.user,
       )
        return loan_repay
           
# ----------------------------------------------------------------------
# Helper function for easy calling
# ----------------------------------------------------------------------
def process_transaction(transaction, user):
    """Process a transaction - simple helper"""
    processor = TransactionPostingService(transaction, user)
#   processor = TransactionProcessor(transaction, user)
    return processor.process()