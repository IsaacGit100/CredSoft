from datetime import datetime
from decimal import Decimal

def parse_ddmmyyyy(date_str):
    """Convert dd/mm/yyyy string to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y').date()
    except ValueError:
        return None

def parse_currency(amount_str):
    """Convert ₵1,234.56 or 1,234.56 to Decimal."""
    if not amount_str:
        return None
    cleaned = amount_str.replace('₵', '').replace(',', '').strip()
    try:
        return Decimal(cleaned)
    except:
        return None
    
def format_date_for_input(date_obj):
    return date_obj.strftime('%Y-%m-%d') if date_obj else ''

def format_number_for_input(num):
    return f"{num:.2f}" if num else ''