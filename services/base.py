from django.db import transaction
from decimal import Decimal


class BaseService:
    """Base class for services - provides common helpers."""

    def __init__(self, entity, user=None):
        self.entity = entity
        self.user = user

    def log_error(self, message):
        print(f"[ERROR] {message}")  # Replace with proper logging later
