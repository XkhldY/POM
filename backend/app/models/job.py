"""
Job model for storing job postings and requirements
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"


class JobType(str, enum.Enum):
    """Job type enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class ExperienceLevel(str, enum.Enum):
    """Experience level enumeration"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class Job(Base):
    """Job model for storing job postings and requirements"""
    
    # Basic information
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    employer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Job details
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT, nullable=False)
    experience_level = Column(Enum(ExperienceLevel), nullable=True)
    
    # Location
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    is_remote = Column(Boolean, default=False, nullable=False)
    is_hybrid = Column(Boolean, default=False, nullable=False)
    
    # Requirements
    skills_required = Column(JSON, nullable=True)  # List of required skills
    skills_preferred = Column(JSON, nullable=True)  # List of preferred skills
    experience_years_min = Column(Integer, nullable=True)
    experience_years_max = Column(Integer, nullable=True)
    
    # Compensation
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(3), default="USD", nullable=False)
    benefits = Column(JSON, nullable=True)  # List of benefits
    
    # Application details
    application_deadline = Column(String(255), nullable=True)
    max_applications = Column(Integer, nullable=True)
    current_applications = Column(Integer, default=0, nullable=False)
    
    # AI-generated data
    skills_vector = Column(JSON, nullable=True)  # Vector representation of required skills
    requirements_vector = Column(JSON, nullable=True)  # Vector representation of requirements
    last_ai_analysis = Column(String(255), nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # List of tags for categorization
    industry = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # SEO and visibility
    slug = Column(String(255), nullable=True, unique=True, index=True)
    views_count = Column(Integer, default=0, nullable=False)
    applications_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    employer = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job")
    
    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company_id={self.company_id})>"
    
    @property
    def full_location(self) -> str:
        """Get full location string"""
        parts = [self.city, self.state, self.country]
        return ", ".join([part for part in parts if part])
    
    @property
    def salary_range(self) -> str:
        """Get formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,} {self.salary_currency}"
        elif self.salary_min:
            return f"${self.salary_min:,}+ {self.salary_currency}"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,} {self.salary_currency}"
        else:
            return "Salary not specified"
    
    @property
    def is_open_for_applications(self) -> bool:
        """Check if job is open for applications"""
        return (
            self.status == JobStatus.PUBLISHED and
            (self.max_applications is None or self.current_applications < self.max_applications)
        )
    
    @property
    def required_skills_list(self) -> list:
        """Get list of required skill names"""
        if self.skills_required:
            return [skill.get("name", "") for skill in self.skills_required if skill.get("name")]
        return []
    
    @property
    def preferred_skills_list(self) -> list:
        """Get list of preferred skill names"""
        if self.skills_preferred:
            return [skill.get("name", "") for skill in self.skills_preferred if skill.get("name")]
        return []
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
    
    def increment_applications(self):
        """Increment application count"""
        self.current_applications += 1
        self.applications_count += 1