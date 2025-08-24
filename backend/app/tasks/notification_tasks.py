"""Notification background tasks for sending notifications asynchronously."""
from celery import current_task
from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.core.config import settings
from app.db.base import get_db
from app.services.user_service import UserService
from typing import Optional, Dict, Any, List
import json
import requests

logger = get_logger(__name__)


class NotificationService:
    """Notification service for sending various types of notifications."""
    
    def __init__(self):
        self.push_api_key = settings.PUSH_API_KEY
        self.sms_api_key = settings.SMS_API_KEY
        self.sms_api_secret = settings.SMS_API_SECRET
        self.sms_from_number = settings.SMS_FROM_NUMBER
    
    def send_push_notification(self, user_id: int, title: str, body: str, 
                              data: Optional[Dict[str, Any]] = None) -> bool:
        """Send push notification to user."""
        try:
            # This would integrate with a push notification service like Firebase
            # For now, just log the notification
            logger.info(f"Push notification sent to user {user_id}: {title} - {body}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send push notification to user {user_id}: {str(e)}")
            return False
    
    def send_sms_notification(self, phone_number: str, message: str) -> bool:
        """Send SMS notification."""
        try:
            # This would integrate with an SMS service like Twilio
            # For now, just log the SMS
            logger.info(f"SMS sent to {phone_number}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return False
    
    def send_in_app_notification(self, user_id: int, title: str, message: str, 
                                notification_type: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Send in-app notification."""
        try:
            # This would store the notification in the database
            # For now, just log the notification
            logger.info(f"In-app notification sent to user {user_id}: {title} - {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send in-app notification to user {user_id}: {str(e)}")
            return False


@celery_app.task(bind=True, name="send_notification")
def send_notification(self, user_id: int, title: str, message: str, 
                     notification_type: str = "general", data: Optional[Dict[str, Any]] = None):
    """Send a notification to a user."""
    try:
        logger.info(f"Sending {notification_type} notification to user {user_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get user
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Create notification service
        notification_service = NotificationService()
        
        # Send in-app notification
        in_app_success = notification_service.send_in_app_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            data=data
        )
        
        # Send push notification if user has push notifications enabled
        push_success = True
        if user.notification_preferences and user.notification_preferences.get("push_enabled", False):
            push_success = notification_service.send_push_notification(
                user_id=user_id,
                title=title,
                body=message,
                data=data
            )
        
        # Send SMS if user has SMS notifications enabled and phone number
        sms_success = True
        if (user.notification_preferences and 
            user.notification_preferences.get("sms_enabled", False) and 
            user.phone):
            sms_success = notification_service.send_sms_notification(
                phone_number=user.phone,
                message=f"{title}: {message}"
            )
        
        # Determine overall success
        overall_success = in_app_success and push_success and sms_success
        
        if overall_success:
            logger.info(f"Notification sent successfully to user {user_id}")
            return {
                "status": "success",
                "user_id": user_id,
                "notification_type": notification_type,
                "in_app": in_app_success,
                "push": push_success,
                "sms": sms_success
            }
        else:
            logger.warning(f"Some notification methods failed for user {user_id}")
            return {
                "status": "partial_success",
                "user_id": user_id,
                "notification_type": notification_type,
                "in_app": in_app_success,
                "push": push_success,
                "sms": sms_success
            }
            
    except Exception as e:
        logger.error(f"Notification task failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="send_push_notification")
def send_push_notification(self, user_id: int, title: str, body: str, 
                          data: Optional[Dict[str, Any]] = None):
    """Send push notification to user."""
    try:
        logger.info(f"Sending push notification to user {user_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get user
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Check if user has push notifications enabled
        if not user.notification_preferences or not user.notification_preferences.get("push_enabled", False):
            logger.info(f"Push notifications disabled for user {user_id}")
            return {"status": "skipped", "message": "Push notifications disabled"}
        
        # Create notification service
        notification_service = NotificationService()
        
        # Send push notification
        success = notification_service.send_push_notification(
            user_id=user_id,
            title=title,
            body=body,
            data=data
        )
        
        if success:
            logger.info(f"Push notification sent successfully to user {user_id}")
            return {"status": "success", "user_id": user_id}
        else:
            logger.error(f"Failed to send push notification to user {user_id}")
            return {"status": "error", "message": "Push notification failed"}
            
    except Exception as e:
        logger.error(f"Push notification task failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="send_sms_notification")
def send_sms_notification(self, user_id: int, message: str):
    """Send SMS notification to user."""
    try:
        logger.info(f"Sending SMS notification to user {user_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get user
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Check if user has phone number
        if not user.phone:
            logger.warning(f"No phone number for user {user_id}")
            return {"status": "skipped", "message": "No phone number"}
        
        # Check if user has SMS notifications enabled
        if not user.notification_preferences or not user.notification_preferences.get("sms_enabled", False):
            logger.info(f"SMS notifications disabled for user {user_id}")
            return {"status": "skipped", "message": "SMS notifications disabled"}
        
        # Create notification service
        notification_service = NotificationService()
        
        # Send SMS notification
        success = notification_service.send_sms_notification(
            phone_number=user.phone,
            message=message
        )
        
        if success:
            logger.info(f"SMS notification sent successfully to user {user_id}")
            return {"status": "success", "user_id": user_id}
        else:
            logger.error(f"Failed to send SMS notification to user {user_id}")
            return {"status": "error", "message": "SMS notification failed"}
            
    except Exception as e:
        logger.error(f"SMS notification task failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="send_bulk_notifications")
def send_bulk_notifications(self, notification_data: List[Dict[str, Any]]):
    """Send bulk notifications to multiple users."""
    try:
        logger.info(f"Sending bulk notifications to {len(notification_data)} users")
        
        # Create notification service
        notification_service = NotificationService()
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for notification_info in notification_data:
            try:
                user_id = notification_info["user_id"]
                title = notification_info["title"]
                message = notification_info["message"]
                notification_type = notification_info.get("notification_type", "general")
                data = notification_info.get("data")
                
                # Send notification
                result = send_notification.delay(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    data=data
                )
                
                if result.get("status") == "success":
                    success_count += 1
                elif result.get("status") == "skipped":
                    skipped_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to queue notification for user {notification_info.get('user_id', 'unknown')}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Bulk notifications queued. Success: {success_count}, Skipped: {skipped_count}, Failed: {failed_count}")
        return {
            "status": "success",
            "success_count": success_count,
            "skipped_count": skipped_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Bulk notifications task failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="send_job_alert_notification")
def send_job_alert_notification(self, user_id: int, job_data: Dict[str, Any]):
    """Send job alert notification to user."""
    try:
        logger.info(f"Sending job alert notification to user {user_id}")
        
        title = "New Job Alert"
        message = f"New job posted: {job_data.get('title', 'Unknown Position')} at {job_data.get('company_name', 'Unknown Company')}"
        
        data = {
            "type": "job_alert",
            "job_id": job_data.get("job_id"),
            "company_id": job_data.get("company_id"),
            "action_url": f"/jobs/{job_data.get('job_id')}"
        }
        
        # Send notification
        result = send_notification.delay(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="job_alert",
            data=data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Job alert notification task failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="send_application_status_notification")
def send_application_status_notification(self, user_id: int, application_data: Dict[str, Any]):
    """Send application status update notification to user."""
    try:
        logger.info(f"Sending application status notification to user {user_id}")
        
        status = application_data.get("status", "updated")
        job_title = application_data.get("job_title", "Unknown Position")
        company_name = application_data.get("company_name", "Unknown Company")
        
        title = "Application Status Update"
        message = f"Your application for {job_title} at {company_name} has been {status}"
        
        data = {
            "type": "application_update",
            "application_id": application_data.get("application_id"),
            "job_id": application_data.get("job_id"),
            "status": status,
            "action_url": f"/applications/{application_data.get('application_id')}"
        }
        
        # Send notification
        result = send_notification.delay(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="application_update",
            data=data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Application status notification task failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}