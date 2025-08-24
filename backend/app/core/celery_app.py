"""Celery configuration for background tasks."""
from celery import Celery
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create Celery instance
celery_app = Celery(
    "pomegranate",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.ai_tasks",
        "app.tasks.email_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.analytics_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.ai_tasks.*": {"queue": "ai"},
        "app.tasks.email_tasks.*": {"queue": "email"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
        "app.tasks.analytics_tasks.*": {"queue": "analytics"},
    },
    
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Task execution settings
    task_always_eager=settings.ENVIRONMENT == "test",  # Execute tasks synchronously in tests
    task_eager_propagates=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Beat scheduler settings (for periodic tasks)
    beat_schedule={
        "cleanup-expired-tokens": {
            "task": "app.tasks.cleanup_tasks.cleanup_expired_tokens",
            "schedule": 3600.0,  # Every hour
        },
        "update-profile-scores": {
            "task": "app.tasks.ai_tasks.update_profile_scores",
            "schedule": 86400.0,  # Every day
        },
        "generate-analytics": {
            "task": "app.tasks.analytics_tasks.generate_daily_analytics",
            "schedule": 86400.0,  # Every day at midnight
        },
    },
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Worker pool settings
    worker_pool="prefork",
    worker_concurrency=4,
    
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
    
    # Security
    security_key=settings.SECRET_KEY,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    
    # Queue settings
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    # Rate limiting
    task_annotations={
        "*": {
            "rate_limit": "100/m",  # 100 tasks per minute
        },
        "app.tasks.ai_tasks.*": {
            "rate_limit": "10/m",  # 10 AI tasks per minute
        },
        "app.tasks.email_tasks.*": {
            "rate_limit": "50/m",  # 50 email tasks per minute
        },
    }
)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks after Celery configuration."""
    logger.info("Celery periodic tasks configured")


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    logger.info(f"Request: {self.request!r}")
    return "Debug task completed"


# Health check task
@celery_app.task(bind=True, name="health_check")
def health_check(self):
    """Health check task for monitoring."""
    try:
        # Basic health check
        return {
            "status": "healthy",
            "task_id": self.request.id,
            "worker": self.request.hostname,
            "timestamp": self.request.timestamp
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "task_id": self.request.id
        }


# Task monitoring
@celery_app.task(bind=True, name="monitor_tasks")
def monitor_tasks(self):
    """Monitor task queue status."""
    try:
        inspect = celery_app.control.inspect()
        
        # Get active tasks
        active = inspect.active()
        
        # Get reserved tasks
        reserved = inspect.reserved()
        
        # Get registered tasks
        registered = inspect.registered()
        
        # Get stats
        stats = inspect.stats()
        
        return {
            "active_tasks": active or {},
            "reserved_tasks": reserved or {},
            "registered_tasks": registered or {},
            "worker_stats": stats or {},
            "timestamp": self.request.timestamp
        }
        
    except Exception as e:
        logger.error(f"Task monitoring failed: {str(e)}")
        return {
            "error": str(e),
            "timestamp": self.request.timestamp
        }


# Task cleanup
@celery_app.task(bind=True, name="cleanup_failed_tasks")
def cleanup_failed_tasks(self):
    """Clean up failed tasks from result backend."""
    try:
        # This would typically clean up failed task results
        # Implementation depends on your result backend
        logger.info("Failed tasks cleanup completed")
        return {"status": "completed", "cleaned_tasks": 0}
        
    except Exception as e:
        logger.error(f"Failed tasks cleanup failed: {str(e)}")
        return {"status": "failed", "error": str(e)}


# Export the Celery app
__all__ = ["celery_app"]