"""
Application model for storing job applications
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class ApplicationStatus(str, enum.Enum):
    """Application status enumeration"""
    SUBMITTED = "submitted"
    REVIEWING = "reviewing"
    SHORTLISTED = "shortlisted"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    """Application model for storing job applications"""
    
    # Relationships
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Application details
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False)
    cover_letter = Column(Text, nullable=True)
    resume_url = Column(String(500), nullable=True)
    
    # Application metadata
    applied_at = Column(String(255), nullable=True)
    last_updated = Column(String(255), nullable=True)
    
    # AI matching data
    match_score = Column(Float, nullable=True)  # AI-generated match score (0-100)
    skills_match_percentage = Column(Float, nullable=True)  # Skills match percentage
    experience_match_percentage = Column(Float, nullable=True)  # Experience match percentage
    
    # AI analysis results
    ai_analysis = Column(JSON, nullable=True)  # Detailed AI analysis results
    ai_recommendations = Column(JSON, nullable=True)  # AI-generated recommendations
    
    # Application tracking
    is_favorite = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)  # Internal notes from employer
    
    # Communication
    last_communication = Column(String(255), nullable=True)
    communication_history = Column(JSON, nullable=True)  # List of communication events
    
    # Interview details
    interview_scheduled = Column(String(255), nullable=True)
    interview_notes = Column(Text, nullable=True)
    
    # Offer details
    offer_amount = Column(Integer, nullable=True)
    offer_currency = Column(String(3), default="USD", nullable=False)
    offer_deadline = Column(String(255), nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    applicant = relationship("User", back_populates="applications")
    
    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, applicant_id={self.applicant_id}, status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if application is still active"""
        return self.status not in [
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
            ApplicationStatus.HIRED
        ]
    
    @property
    def is_shortlisted(self) -> bool:
        """Check if application is shortlisted"""
        return self.status in [
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.INTERVIEWING,
            ApplicationStatus.OFFERED,
            ApplicationStatus.HIRED
        ]
    
    @property
    def match_score_display(self) -> str:
        """Get formatted match score"""
        if self.match_score is not None:
            return f"{self.match_score:.1f}%"
        return "Not calculated"
    
    @property
    def status_display(self) -> str:
        """Get human-readable status"""
        status_map = {
            ApplicationStatus.SUBMITTED: "Submitted",
            ApplicationStatus.REVIEWING: "Under Review",
            ApplicationStatus.SHORTLISTED: "Shortlisted",
            ApplicationStatus.INTERVIEWING: "Interviewing",
            ApplicationStatus.OFFERED: "Offer Made",
            ApplicationStatus.HIRED: "Hired",
            ApplicationStatus.REJECTED: "Not Selected",
            ApplicationStatus.WITHDRAWN: "Withdrawn"
        }
        return status_map.get(self.status, self.status.value.title())
    
    def update_status(self, new_status: ApplicationStatus, notes: str = None):
        """Update application status with optional notes"""
        self.status = new_status
        if notes:
            self.notes = notes
        self.last_updated = "now"  # This should be updated with actual timestamp
    
    def calculate_match_score(self, skills_weight: float = 0.6, experience_weight: float = 0.4) -> float:
        """Calculate overall match score based on skills and experience"""
        if self.skills_match_percentage is None or self.experience_match_percentage is None:
            return None
        
        score = (
            (self.skills_match_percentage * skills_weight) +
            (self.experience_match_percentage * experience_weight)
        )
        
        self.match_score = round(score, 2)
        return self.match_score