"""
Notification module for contract updates.

This module provides functionality for:
- Email notifications (SMTP)
- DingTalk notifications (future)
- Notification templates
- Message formatting
"""

from .email import EmailNotifier
from .template import NotificationTemplate

__all__ = [
    "EmailNotifier",
    "NotificationTemplate",
]
