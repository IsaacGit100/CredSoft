from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import date
import logging

logger = logging.getLogger(__name__)

from MembersApp.models import Master
from RecPayApp.models import Trans
from LoanApp.model import Loan
from coa.models import ChartOfAccounts


# ============================================
# MAIN ORCHESTRATOR - Calls all the routines
# ============================================

class TransactionProcessor:
    """
    Main orchestrator - reads trans record and coordinates all updates
    This is the ONLY routine you call from your view
    """
    
    @classmethod
    def process_transaction(cls, trans_record, user=None):
        """
        MAIN ENTRY POINT - Process a single transaction
        
        STEP 1: Read trans record
        STEP 2: Call each update routine
        STEP 3: Return combined results
        
        This is the "main program" you mentioned
        """
        
        logger.info(f"Starting to process transaction: {trans_record.rec_vou_no}")
        
        # Use database transaction - everything succeeds or nothing changes
        with db_transaction.atomic():
            
            # STEP 1: Update Master table (member balances)
            master_result = cls.update_master(trans_record)
            
            # STEP 2: Create Statement record (member statement)
           # statement_result = cls.create_statement(trans_record)
            
            # STEP 3: Create Journal Entry (accounting header)
           # journal_entry_result = cls.create_journal_entry(trans_record, user)
            
            # STEP 4: Create Journal Lines (accounting details)
           # journal_lines_result = cls.create_journal_lines(trans_record, journal_entry_result['entry'])
            
            # STEP 5: Update Balance Sheet (if needed)
          #  balancesheet_result = cls.update_balance_sheet(trans_record)
            
            # STEP 6: Update transaction status
          #  trans_record.status = 'PROCESSED'
          #  trans_record.processed_at = timezone.now()
          #  trans_record.save()
            
          #  logger.info(f"Successfully processed transaction: {trans_record.rec_vou_no}")
            
          #  return {
          #      'success': True,
          #      'message': f'Transaction {trans_record.rec_vou_no} processed successfully',
          #      'master': master_result,
          #      'statement': statement_result,
         #       'journal_entry': journal_entry_result,
         #       'journal_lines': journal_lines_result,
         #       'balancesheet': balancesheet_result,

    
    # ============================================
    # ROUTINE 1: Update Master Table
    # ============================================
    
    @classmethod
    def update_master(cls, trans_record):
       
        if not trans_record.member:
            return {'skipped': True, 'reason': 'No member associated'}
        
        member = trans_record.member
        
        # Store old values for audit
        old_deposits = member.tot_deposits
        old_withdrawals = member.tot_deposit_withdrawal
        old_balance = member.available_balance  # Using your 
        old_shares = member.shares 
        old_shares_withdrawal = member.shares_withdrawal
        old_dividend = member.dividend
        old_dividend_withdrawal = member.dividend_withdrawal
        old_int_accrued = member.int_accrued   
        old_available_balance = member.available_balance
        
        
        # Update based on transaction type
        if trans_record.trans_type == 'Receipts' and trans_record.ledger_name == 'Savings Deposit' and trans_record.amount > 0:
            member.tot_deposits += trans_record.amount
            member.mem_status = 'Active'
            
            action = "DEPOSIT"
            logger.info(f"DEPOSIT: Member {member.id} - Adding {trans_record.amount}")
            
        if trans_record.trans_type == 'Payments' and trans_record.ledger_name == 'Savings Withdrawal' and trans_record.amount > 0:
            member.tot_deposit_withdrawal +=trans_record.amount
            
            action = "WITHDRAWAL"
            logger.info(f"WITHDRAWAL: Member {member.id} - Removing {trans_record.amount}")
            
        if trans_record.trans_type == 'Receipts' and trans_record.ledger_name=='Dividend' and trans_record.amount > 0:
            member.tot_dividend += trans_record.amount
            member.mem_status = 'Active'
            
            action = "DIVIDEND"
            logger.info(f"DEPOSIT: Member {member.id} - Adding {trans_record.amount}")
            
        if trans_record.trans_type == 'Payments' and trans_record.ledger_name=='Dividend Withdrawal' and trans_record.amount > 0:
            member.dividend_withdrawal += trans_record.amount
            member.mem_status = 'Active'
            
            action = "DIVIDEND WITHDRAWAL"
            logger.info(f"DEPOSIT: Member {member.id} - Adding {trans_record.amount}")
        
            
        if trans_record.trans_type == 'Receipts' and trans_record.ledger_name=='Shares' and trans_record.amount > 0:
            member.tot_dividend += trans_record.amount
            member.mem_status = 'Active'
            
            action = "SHARES"
            logger.info(f"DEPOSIT: Member {member.id} - Adding {trans_record.amount}")
            
        if trans_record.trans_type == 'Payments' and trans_record.ledger_name=='Shares Withdrawal' and trans_record.amount > 0:
            member.dividend_withdrawal += trans_record.amount
            member.mem_status = 'Active'
            
            action = "SHARES WITHDRAWAL"
            logger.info(f"DEPOSIT: Member {member.id} - Adding {trans_record.amount}")
        
        # Save the updated member record
        member.save()
        
        # Get new balance (automatically calculated by property)
        new_balance = member.sav_avail_bal
        
        logger.info(f"Master updated: Balance {old_balance} → {new_balance}")
        
        return {
            'success': True,
            'member_id': member.id,
            'member_name': member.full_name,
            'action': action,
            'amount': trans_record.amount,
            'old_balance': old_balance,
            'new_balance': new_balance,
            'old_deposits': old_deposits,
            'new_deposits': member.tot_deposits,
            'old_withdrawals': old_withdrawals,
            'new_withdrawals': member.tot_deposit_withdrawal,
        }
    
    # ============================================
    # ROUTINE 2: Create Statement Record
    # ============================================
    
    @classmethod
    def create_statement(cls, trans_record):
        """
        ROUTINE 2: Create a statement record for member's passbook
        
        WHAT IT DOES:
        - Creates a line item in the member's statement
        - Shows date, description, debit, credit, balance
        
        INPUT: Transaction record
        OUTPUT: Created statement record
        """
        
        from MembersApp.models import MemberStatement  # Create this model
        
        # Only create statement for member transactions
        if not trans_record.member:
            return {'skipped': True, 'reason': 'No member associated'}
        
        member = trans_record.member
        
        # Calculate running balance
        previous_balance = cls._get_previous_statement_balance(member, trans_record.date)
        
        if trans_record.trans_type == 'Receipts':
            debit = trans_record.amount  # Money IN
            credit = Decimal('0.00')
            new_balance = previous_balance + trans_record.amount
        else:
            debit = Decimal('0.00')
            credit = trans_record.amount  # Money OUT
            new_balance = previous_balance - trans_record.amount
        
        # Create description
        description = f"{trans_record.purpose} - {trans_record.details}" if trans_record.details else trans_record.purpose
        
        # Create statement record
        statement = MemberStatement.objects.create(
            member=member,
            date=trans_record.date,
            transaction_ref=trans_record.rec_vou_no,
            description=description,
            debit=debit,
            credit=credit,
            balance=new_balance,
            transaction_type=trans_record.trans_type,
            created_by=trans_record.created_by,
        )
        
        logger.info(f"Statement created for member {member.id}: Balance {previous_balance} → {new_balance}")
        
        return {
            'success': True,
            'statement_id': statement.id,
            'member_id': member.id,
            'previous_balance': previous_balance,
            'new_balance': new_balance,
            'debit': debit,
            'credit': credit,
        }
 