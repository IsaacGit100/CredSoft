# behavior_mapper.py
"""
Maps COA behaviors to Master model fields and update rules
"""

BEHAVIOR_MASTER_MAP = {
    # Asset behaviors
    'MEMBER_LOAN': {
        'field': 'tot_loans',
        'direction': 'increase_on_debit',  # Debit increases, Credit decreases
        'description': 'Member loan balance',
        'affects_member': True,
    },
    'CASH': {
        'field': None,  # Cash doesn't directly affect member
        'affects_member': False,
        'description': 'Cash/bank account',
    },
    'RECEIVABLE': {
        'field': None,
        'affects_member': False,
        'description': 'Accounts receivable',
    },
    
    # Liability behaviors
    'MEMBER_SAVINGS': {
        'field': 'tot_deposits',
        'direction': 'increase_on_credit',  # Credit increases, Debit decreases
        'description': 'Member savings deposits',
        'affects_member': True,
    },
    'MEMBER_SHARES': {
        'field': 'tot_shares',
        'direction': 'increase_on_credit',
        'description': 'Member shares',
        'affects_member': True,
    },
    
    # Income behaviors
    'INTEREST_INCOME': {
        'field': None,  # Income doesn't directly affect member
        'description': 'Interest earned on loans',
        'affects_member': False,
    },
    'FEE_INCOME': {
        'field': None,
        'description': 'Fees charged to members',
        'affects_member': False,
    },
    
    # Expense behaviors
    'INTEREST_EXPENSE': {
        'field': None,
        'description': 'Interest paid on savings',
        'affects_member': False,
    },
    'OPERATING_EXPENSE': {
        'field': None,
        'description': 'Operating expenses',
        'affects_member': False,
    },
    
    # Special behaviors
    'LOAN_DISBURSEMENT': {
        'field': 'tot_loans',
        'direction': 'increase_on_debit',
        'description': 'New loan disbursed to member',
        'affects_member': True,
    },
    'LOAN_REPAYMENT': {
        'field': 'tot_loans',
        'direction': 'decrease_on_debit',  # Debit decreases loan balance
        'description': 'Member loan repayment',
        'affects_member': True,
    },
}

def get_behavior_info(behavior_code):
    """Get behavior information"""
    return BEHAVIOR_MASTER_MAP.get(behavior_code, {
        'field': None,
        'affects_member': False,
        'direction': None,
        'description': 'Unknown behavior',
    })