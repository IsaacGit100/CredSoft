"""
Base Service Class - All services inherit from this
"""
from django.db import transaction
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class BaseService:
    """
    Base service with common functionality
    """
    
    @classmethod
    def log_action(cls, action, details):
        """Log service actions"""
        logger.info(f"[{cls.__name__}] {action}: {details}")
    
    @classmethod
    def handle_error(cls, error, context):
        """Handle errors consistently"""
        logger.error(f"[{cls.__name__}] Error: {str(error)}", exc_info=True)
        return {
            'success': False,
            'error': str(error),
            'context': context
        }
    
    @classmethod
    def validate_amount(cls, amount):
        """Validate amount is positive"""
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
            return amount
        except:
            raise ValueError(f"Invalid amount: {amount}")