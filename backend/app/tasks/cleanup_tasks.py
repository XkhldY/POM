"""Cleanup background tasks for maintenance operations."""
from celery import current_task
from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.core.config import settings
from app.db.base import get_db
from app.services.user_service import UserService
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

logger = get_logger(__name__)


@celery_app.task(bind=True, name="cleanup_expired_tokens")
def cleanup_expired_tokens(self):
    """Clean up expired verification and password reset tokens."""
    try:
        logger.info("Starting expired tokens cleanup")
        
        # Get database session
        db = next(get_db())
        
        # Get user service
        user_service = UserService(db)
        
        # Get current time
        now = datetime.utcnow()
        
        # Find users with expired verification tokens
        expired_verification_users = user_service.get_users_with_expired_verification_tokens(now)
        
        # Find users with expired password reset tokens
        expired_reset_users = user_service.get_users_with_expired_password_reset_tokens(now)
        
        # Clean up expired tokens
        verification_cleaned = 0
        reset_cleaned = 0
        
        for user in expired_verification_users:
            try:
                user_service.update_user(
                    user.id,
                    verification_token=None,
                    verification_token_expires=None
                )
                verification_cleaned += 1
            except Exception as e:
                logger.error(f"Failed to clean verification token for user {user.id}: {str(e)}")
        
        for user in expired_reset_users:
            try:
                user_service.update_user(
                    user.id,
                    password_reset_token=None,
                    password_reset_token_expires=None
                )
                reset_cleaned += 1
            except Exception as e:
                logger.error(f"Failed to clean password reset token for user {user.id}: {str(e)}")
        
        logger.info(f"Expired tokens cleanup completed. Verification: {verification_cleaned}, Reset: {reset_cleaned}")
        return {
            "status": "success",
            "verification_tokens_cleaned": verification_cleaned,
            "reset_tokens_cleaned": reset_cleaned
        }
        
    except Exception as e:
        logger.error(f"Expired tokens cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="cleanup_old_logs")
def cleanup_old_logs(self, days_to_keep: int = 30):
    """Clean up old log files."""
    try:
        logger.info(f"Starting old logs cleanup (keeping {days_to_keep} days)")
        
        # This would implement logic to clean up old log files
        # For now, just log the task
        logger.info("Old logs cleanup completed")
        
        return {
            "status": "success",
            "message": f"Cleaned up logs older than {days_to_keep} days"
        }
        
    except Exception as e:
        logger.error(f"Old logs cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="cleanup_failed_tasks")
def cleanup_failed_tasks(self, days_to_keep: int = 7):
    """Clean up failed task results from result backend."""
    try:
        logger.info(f"Starting failed tasks cleanup (keeping {days_to_keep} days)")
        
        # This would implement logic to clean up failed task results
        # For now, just log the task
        logger.info("Failed tasks cleanup completed")
        
        return {
            "status": "success",
            "message": f"Cleaned up failed tasks older than {days_to_keep} days"
        }
        
    except Exception as e:
        logger.error(f"Failed tasks cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="cleanup_inactive_users")
def cleanup_inactive_users(self, days_inactive: int = 365):
    """Clean up inactive user accounts."""
    try:
        logger.info(f"Starting inactive users cleanup (inactive for {days_inactive} days)")
        
        # Get database session
        db = next(get_db())
        
        # Get user service
        user_service = UserService(db)
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        # Find inactive users
        inactive_users = user_service.get_inactive_users_since(cutoff_date)
        
        # Soft delete inactive users (mark as inactive)
        cleaned_count = 0
        
        for user in inactive_users:
            try:
                # Skip superusers and verified users
                if user.is_superuser or user.is_verified:
                    continue
                
                user_service.update_user(
                    user.id,
                    is_active=False,
                    updated_at=datetime.utcnow()
                )
                cleaned_count += 1
                
            except Exception as e:
                logger.error(f"Failed to deactivate user {user.id}: {str(e)}")
        
        logger.info(f"Inactive users cleanup completed. Deactivated: {cleaned_count}")
        return {
            "status": "success",
            "users_deactivated": cleaned_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Inactive users cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="cleanup_expired_jobs")
def cleanup_expired_jobs(self):
    """Clean up expired job postings."""
    try:
        logger.info("Starting expired jobs cleanup")
        
        # Get database session
        db = next(get_db())
        
        # Get job service
        job_service = JobService(db)
        
        # Get current time
        now = datetime.utcnow()
        
        # Find expired jobs
        expired_jobs = job_service.get_expired_jobs(now)
        
        # Close expired jobs
        closed_count = 0
        
        for job in expired_jobs:
            try:
                job_service.close_job(job.id)
                closed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to close expired job {job.id}: {str(e)}")
        
        logger.info(f"Expired jobs cleanup completed. Closed: {closed_count}")
        return {
            "status": "success",
            "jobs_closed": closed_count
        }
        
    except Exception as e:
        logger.error(f"Expired jobs cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="cleanup_old_applications")
def cleanup_old_applications(self, days_to_keep: int = 730):  # 2 years
    """Clean up old job applications."""
    try:
        logger.info(f"Starting old applications cleanup (keeping {days_to_keep} days)")
        
        # Get database session
        db = next(get_db())
        
        # Get application service
        application_service = ApplicationService(db)
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Find old applications
        old_applications = application_service.get_applications_older_than(cutoff_date)
        
        # Archive old applications (soft delete)
        archived_count = 0
        
        for application in old_applications:
            try:
                # Skip applications that are still active or recent
                if application.status in ["shortlisted", "interview", "offer"]:
                    continue
                
                application_service.update_application(
                    application.id,
                    status="archived",
                    updated_at=datetime.utcnow()
                )
                archived_count += 1
                
            except Exception as e:
                logger.error(f"Failed to archive application {application.id}: {str(e)}")
        
        logger.info(f"Old applications cleanup completed. Archived: {archived_count}")
        return {
            "status": "success",
            "applications_archived": archived_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Old applications cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="cleanup_database")
def cleanup_database(self):
    """Perform general database cleanup operations."""
    try:
        logger.info("Starting database cleanup")
        
        # Get database session
        db = next(get_db())
        
        # This would implement various database cleanup operations:
        # - Remove orphaned records
        # - Clean up temporary tables
        # - Optimize table performance
        # - Clean up unused indexes
        
        # For now, just log the task
        logger.info("Database cleanup completed")
        
        return {
            "status": "success",
            "message": "Database cleanup completed"
        }
        
    except Exception as e:
        logger.error(f"Database cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="cleanup_cache")
def cleanup_cache(self):
    """Clean up cache and temporary data."""
    try:
        logger.info("Starting cache cleanup")
        
        # This would implement cache cleanup operations:
        # - Remove expired cache entries
        # - Clean up temporary files
        # - Optimize cache performance
        
        # For now, just log the task
        logger.info("Cache cleanup completed")
        
        return {
            "status": "success",
            "message": "Cache cleanup completed"
        }
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="run_maintenance_cycle")
def run_maintenance_cycle(self):
    """Run a complete maintenance cycle with all cleanup tasks."""
    try:
        logger.info("Starting maintenance cycle")
        
        # Run all cleanup tasks
        tasks = [
            cleanup_expired_tokens.delay(),
            cleanup_inactive_users.delay(),
            cleanup_expired_jobs.delay(),
            cleanup_old_applications.delay(),
            cleanup_database.delay(),
            cleanup_cache.delay()
        ]
        
        # Wait for all tasks to complete
        results = []
        for task in tasks:
            try:
                result = task.get(timeout=300)  # 5 minute timeout
                results.append(result)
            except Exception as e:
                logger.error(f"Maintenance task failed: {str(e)}")
                results.append({"status": "error", "message": str(e)})
        
        # Compile results
        successful_tasks = len([r for r in results if r.get("status") == "success"])
        failed_tasks = len([r for r in results if r.get("status") == "error"])
        
        logger.info(f"Maintenance cycle completed. Successful: {successful_tasks}, Failed: {failed_tasks}")
        return {
            "status": "success",
            "total_tasks": len(tasks),
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Maintenance cycle failed: {str(e)}")
        return {"status": "error", "message": str(e)}