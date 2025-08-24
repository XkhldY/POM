"""Email background tasks for sending emails asynchronously."""
from celery import current_task
from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.core.config import settings
from app.db.base import get_db
from app.services.user_service import UserService
from app.services.job_service import JobService
from app.services.company_service import CompanyService
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional, List

logger = get_logger(__name__)


class EmailService:
    """Email service for sending emails."""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   html_body: Optional[str] = None, attachments: List[str] = None) -> bool:
        """Send an email."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    if os.path.exists(attachment):
                        with open(attachment, "rb") as file:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(file.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(attachment)}'
                        )
                        msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False


@celery_app.task(bind=True, name="send_welcome_email")
def send_welcome_email(self, user_id: int):
    """Send welcome email to new user."""
    try:
        logger.info(f"Sending welcome email to user {user_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get user
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Create email service
        email_service = EmailService()
        
        # Prepare email content
        subject = "Welcome to Pomegranate - Your AI-Powered Job Platform!"
        
        body = f"""
        Welcome to Pomegranate, {user.first_name}!
        
        Thank you for joining our AI-powered job platform. We're excited to help you find your next opportunity or hire the perfect candidate.
        
        Here's what you can do next:
        1. Complete your profile to get better job matches
        2. Browse available job postings
        3. Set up job alerts for your preferred positions
        
        If you have any questions, feel free to reach out to our support team.
        
        Best regards,
        The Pomegranate Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to Pomegranate, {user.first_name}!</h2>
            <p>Thank you for joining our AI-powered job platform. We're excited to help you find your next opportunity or hire the perfect candidate.</p>
            
            <h3>Here's what you can do next:</h3>
            <ol>
                <li>Complete your profile to get better job matches</li>
                <li>Browse available job postings</li>
                <li>Set up job alerts for your preferred positions</li>
            </ol>
            
            <p>If you have any questions, feel free to reach out to our support team.</p>
            
            <p>Best regards,<br>The Pomegranate Team</p>
        </body>
        </html>
        """
        
        # Send email
        success = email_service.send_email(
            to_email=user.email,
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        if success:
            logger.info(f"Welcome email sent successfully to user {user_id}")
            return {"status": "success", "user_id": user_id}
        else:
            logger.error(f"Failed to send welcome email to user {user_id}")
            return {"status": "error", "message": "Email sending failed"}
            
    except Exception as e:
        logger.error(f"Welcome email task failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="send_password_reset_email")
def send_password_reset_email(self, user_id: int, reset_token: str):
    """Send password reset email to user."""
    try:
        logger.info(f"Sending password reset email to user {user_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get user
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Create email service
        email_service = EmailService()
        
        # Prepare email content
        subject = "Password Reset Request - Pomegranate"
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        body = f"""
        Hello {user.first_name},
        
        You requested a password reset for your Pomegranate account.
        
        Click the following link to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        The Pomegranate Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello {user.first_name},</p>
            
            <p>You requested a password reset for your Pomegranate account.</p>
            
            <p><a href="{reset_url}">Click here to reset your password</a></p>
            
            <p>This link will expire in 1 hour.</p>
            
            <p>If you didn't request this reset, please ignore this email.</p>
            
            <p>Best regards,<br>The Pomegranate Team</p>
        </body>
        </html>
        """
        
        # Send email
        success = email_service.send_email(
            to_email=user.email,
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        if success:
            logger.info(f"Password reset email sent successfully to user {user_id}")
            return {"status": "success", "user_id": user_id}
        else:
            logger.error(f"Failed to send password reset email to user {user_id}")
            return {"status": "error", "message": "Email sending failed"}
            
    except Exception as e:
        logger.error(f"Password reset email task failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="send_verification_email")
def send_verification_email(self, user_id: int, verification_token: str):
    """Send email verification email to user."""
    try:
        logger.info(f"Sending verification email to user {user_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get user
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Create email service
        email_service = EmailService()
        
        # Prepare email content
        subject = "Verify Your Email - Pomegranate"
        
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        body = f"""
        Hello {user.first_name},
        
        Welcome to Pomegranate! Please verify your email address to complete your registration.
        
        Click the following link to verify your email:
        {verification_url}
        
        This link will expire in 24 hours.
        
        Best regards,
        The Pomegranate Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Verify Your Email</h2>
            <p>Hello {user.first_name},</p>
            
            <p>Welcome to Pomegranate! Please verify your email address to complete your registration.</p>
            
            <p><a href="{verification_url}">Click here to verify your email</a></p>
            
            <p>This link will expire in 24 hours.</p>
            
            <p>Best regards,<br>The Pomegranate Team</p>
        </body>
        </html>
        """
        
        # Send email
        success = email_service.send_email(
            to_email=user.email,
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        if success:
            logger.info(f"Verification email sent successfully to user {user_id}")
            return {"status": "success", "user_id": user_id}
        else:
            logger.error(f"Failed to send verification email to user {user_id}")
            return {"status": "error", "message": "Email sending failed"}
            
    except Exception as e:
        logger.error(f"Verification email task failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="send_job_application_email")
def send_job_application_email(self, application_id: int):
    """Send job application confirmation email."""
    try:
        logger.info(f"Sending job application email for application {application_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get application details
        from app.services.application_service import ApplicationService
        application_service = ApplicationService(db)
        application = application_service.get_application_by_id(application_id)
        
        if not application:
            logger.error(f"Application {application_id} not found")
            return {"status": "error", "message": "Application not found"}
        
        # Get job and company details
        job = application.job
        company = job.company if job.company else None
        
        # Create email service
        email_service = EmailService()
        
        # Prepare email content
        subject = f"Application Submitted - {job.title}"
        
        body = f"""
        Hello {application.applicant.first_name},
        
        Your application for the position "{job.title}" has been submitted successfully.
        
        Job Details:
        - Position: {job.title}
        - Company: {company.name if company else 'Not specified'}
        - Location: {job.city}, {job.state}, {job.country}
        
        Application Status: {application.status}
        
        We'll review your application and get back to you soon. You can track your application status in your dashboard.
        
        Best regards,
        The Pomegranate Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Application Submitted Successfully</h2>
            <p>Hello {application.applicant.first_name},</p>
            
            <p>Your application for the position <strong>"{job.title}"</strong> has been submitted successfully.</p>
            
            <h3>Job Details:</h3>
            <ul>
                <li><strong>Position:</strong> {job.title}</li>
                <li><strong>Company:</strong> {company.name if company else 'Not specified'}</li>
                <li><strong>Location:</strong> {job.city}, {job.state}, {job.country}</li>
            </ul>
            
            <p><strong>Application Status:</strong> {application.status}</p>
            
            <p>We'll review your application and get back to you soon. You can track your application status in your dashboard.</p>
            
            <p>Best regards,<br>The Pomegranate Team</p>
        </body>
        </html>
        """
        
        # Send email
        success = email_service.send_email(
            to_email=application.applicant.email,
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        if success:
            logger.info(f"Job application email sent successfully for application {application_id}")
            return {"status": "success", "application_id": application_id}
        else:
            logger.error(f"Failed to send job application email for application {application_id}")
            return {"status": "error", "message": "Email sending failed"}
            
    except Exception as e:
        logger.error(f"Job application email task failed for application {application_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="send_bulk_emails")
def send_bulk_emails(self, email_data: List[dict]):
    """Send bulk emails to multiple recipients."""
    try:
        logger.info(f"Sending bulk emails to {len(email_data)} recipients")
        
        # Create email service
        email_service = EmailService()
        
        success_count = 0
        failed_count = 0
        
        for email_info in email_data:
            try:
                success = email_service.send_email(
                    to_email=email_info["to_email"],
                    subject=email_info["subject"],
                    body=email_info["body"],
                    html_body=email_info.get("html_body")
                )
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to send bulk email to {email_info.get('to_email', 'unknown')}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Bulk email sending completed. Success: {success_count}, Failed: {failed_count}")
        return {
            "status": "success",
            "success_count": success_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Bulk email task failed: {str(e)}")
        return {"status": "error", "message": str(e)}