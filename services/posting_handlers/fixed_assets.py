"""
FixedAssets post-posting handler.

Registers the existing `apply_posted_depreciation` from
FixedAssets.services with the posting engine.
"""

from services.transaction_posting_service import register_posting_handler
from FixedAssets.services import apply_posted_depreciation

register_posting_handler("depreciation", apply_posted_depreciation)
