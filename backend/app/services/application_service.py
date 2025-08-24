"""
Application service for job application management operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc

from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.user import User
from app.core.exceptions import NotFoundError, ValidationError


class ApplicationService:
    """Service class for application operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_application_by_id(self, application_id: int) -> Optional[Application]:
        """Get application by ID"""
        return self.db.query(Application).filter(Application.id == application_id).first()
    
    def get_applications(self, skip: int = 0, limit: int = 100, status: ApplicationStatus = None) -> List[Application]:
        """Get list of applications with pagination and optional status filter"""
        query = self.db.query(Application)
        
        if status:
            query = query.filter(Application.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_applications_by_job(self, job_id: int, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get applications for a specific job"""
        return self.db.query(Application).filter(Application.job_id == job_id).offset(skip).limit(limit).all()
    
    def get_applications_by_applicant(self, applicant_id: int, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get applications by a specific applicant"""
        return self.db.query(Application).filter(Application.applicant_id == applicant_id).offset(skip).limit(limit).all()
    
    def get_applications_by_employer(self, employer_id: int, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get applications for jobs posted by a specific employer"""
        # Join with Job table to filter by employer
        return self.db.query(Application).join(Job).filter(Job.employer_id == employer_id).offset(skip).limit(limit).all()
    
    def create_application(self, **kwargs) -> Application:
        """Create a new job application"""
        # Check if user has already applied for this job
        existing_application = self.db.query(Application).filter(
            and_(
                Application.job_id == kwargs["job_id"],
                Application.applicant_id == kwargs["applicant_id"]
            )
        ).first()
        
        if existing_application:
            raise ValidationError("User has already applied for this job")
        
        # Check if job is open for applications
        job = self.db.query(Job).filter(Job.id == kwargs["job_id"]).first()
        if not job or not job.is_open_for_applications:
            raise ValidationError("Job is not open for applications")
        
        # Create application
        db_application = Application(**kwargs)
        self.db.add(db_application)
        
        # Increment job application count
        job.increment_applications()
        
        self.db.commit()
        self.db.refresh(db_application)
        
        return db_application
    
    def update_application(self, application_id: int, **kwargs) -> Optional[Application]:
        """Update application information"""
        application = self.get_application_by_id(application_id)
        if not application:
            raise NotFoundError("Application", application_id)
        
        # Update fields
        for field, value in kwargs.items():
            if hasattr(application, field):
                setattr(application, field, value)
        
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def update_application_status(self, application_id: int, new_status: ApplicationStatus, notes: str = None) -> Optional[Application]:
        """Update application status with optional notes"""
        application = self.get_application_by_id(application_id)
        if not application:
            raise NotFoundError("Application", application_id)
        
        application.update_status(new_status, notes)
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def delete_application(self, application_id: int) -> bool:
        """Delete an application"""
        application = self.get_application_by_id(application_id)
        if not application:
            return False
        
        # Decrement job application count
        job = self.db.query(Job).filter(Job.id == application.job_id).first()
        if job:
            job.current_applications = max(0, job.current_applications - 1)
        
        self.db.delete(application)
        self.db.commit()
        return True
    
    def withdraw_application(self, application_id: int) -> Optional[Application]:
        """Withdraw an application"""
        application = self.get_application_by_id(application_id)
        if not application:
            raise NotFoundError("Application", application_id)
        
        if application.status not in [ApplicationStatus.SUBMITTED, ApplicationStatus.REVIEWING]:
            raise ValidationError("Application cannot be withdrawn in current status")
        
        application.status = ApplicationStatus.WITHDRAWN
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def shortlist_application(self, application_id: int, notes: str = None) -> Optional[Application]:
        """Shortlist an application"""
        application = self.get_application_by_id(application_id)
        if not application:
            raise NotFoundError("Application", application_id)
        
        if application.status not in [ApplicationStatus.SUBMITTED, ApplicationStatus.REVIEWING]:
            raise ValidationError("Application cannot be shortlisted in current status")
        
        application.status = ApplicationStatus.SHORTLISTED
        if notes:
            application.notes = notes
        
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def reject_application(self, application_id: int, notes: str = None) -> Optional[Application]:
        """Reject an application"""
        application = self.get_application_by_id(application_id)
        if not application:
            raise NotFoundError("Application", application_id)
        
        application.status = ApplicationStatus.REJECTED
        if notes:
            application.notes = notes
        
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def get_applications_by_status(self, status: ApplicationStatus, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get applications with a specific status"""
        return self.db.query(Application).filter(Application.status == status).offset(skip).limit(limit).all()
    
    def get_active_applications(self, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get active applications (not rejected, withdrawn, or hired)"""
        return self.db.query(Application).filter(
            Application.status.in_([
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.REVIEWING,
                ApplicationStatus.SHORTLISTED,
                ApplicationStatus.INTERVIEWING,
                ApplicationStatus.OFFERED
            ])
        ).offset(skip).limit(limit).all()
    
    def get_shortlisted_applications(self, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get shortlisted applications"""
        return self.db.query(Application).filter(
            Application.status.in_([
                ApplicationStatus.SHORTLISTED,
                ApplicationStatus.INTERVIEWING,
                ApplicationStatus.OFFERED,
                ApplicationStatus.HIRED
            ])
        ).offset(skip).limit(limit).all()
    
    def search_applications(self, query: str, skip: int = 0, limit: int = 100) -> List[Application]:
        """Search applications by cover letter content"""
        return self.db.query(Application).filter(
            Application.cover_letter.ilike(f"%{query}%")
        ).offset(skip).limit(limit).all()
    
    def get_applications_count(self, status: ApplicationStatus = None) -> int:
        """Get total count of applications with optional status filter"""
        query = self.db.query(Application)
        if status:
            query = query.filter(Application.status == status)
        return query.count()
    
    def get_active_applications_count(self) -> int:
        """Get count of active applications"""
        return self.db.query(Application).filter(
            Application.status.in_([
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.REVIEWING,
                ApplicationStatus.SHORTLISTED,
                ApplicationStatus.INTERVIEWING,
                ApplicationStatus.OFFERED
            ])
        ).count()
    
    def get_shortlisted_applications_count(self) -> int:
        """Get count of shortlisted applications"""
        return self.db.query(Application).filter(
            Application.status.in_([
                ApplicationStatus.SHORTLISTED,
                ApplicationStatus.INTERVIEWING,
                ApplicationStatus.OFFERED,
                ApplicationStatus.HIRED
            ])
        ).count()