"""
Tasks package for background job processing.
"""

from .ai_tasks import *
from .email_tasks import *
from .notification_tasks import *
from .analytics_tasks import *
from .cleanup_tasks import *

__all__ = [
    # AI tasks
    "analyze_profile_async",
    "analyze_job_async",
    "update_profile_scores",
    "generate_recommendations",
    
    # Email tasks
    "send_welcome_email",
    "send_password_reset_email",
    "send_verification_email",
    "send_job_application_email",
    
    # Notification tasks
    "send_notification",
    "send_push_notification",
    "send_sms_notification",
    
    # Analytics tasks
    "generate_daily_analytics",
    "update_search_analytics",
    "process_user_activity",
    
    # Cleanup tasks
    "cleanup_expired_tokens",
    "cleanup_old_logs",
    "cleanup_failed_tasks"
]