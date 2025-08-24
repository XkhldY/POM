"""
Profile model for storing detailed user profile information
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Profile(Base):
    """Profile model for storing detailed user profile information"""
    
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)
    
    # Professional information
    title = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    
    # Location
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    is_remote_available = Column(Boolean, default=False, nullable=False)
    
    # Skills and expertise
    skills = Column(JSON, nullable=True)  # List of skill objects with name, level, years
    languages = Column(JSON, nullable=True)  # List of language objects with name, proficiency
    
    # Education
    education = Column(JSON, nullable=True)  # List of education objects
    
    # Work experience
    experience = Column(JSON, nullable=True)  # List of experience objects
    
    # Resume and documents
    resume_url = Column(String(500), nullable=True)
    resume_filename = Column(String(255), nullable=True)
    resume_uploaded_at = Column(String(255), nullable=True)
    
    # Social profiles
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    
    # Preferences
    salary_expectation_min = Column(Integer, nullable=True)
    salary_expectation_max = Column(Integer, nullable=True)
    preferred_work_types = Column(JSON, nullable=True)  # List of work type preferences
    preferred_industries = Column(JSON, nullable=True)  # List of industry preferences
    
    # AI-generated data
    skills_vector = Column(JSON, nullable=True)  # Vector representation of skills
    experience_vector = Column(JSON, nullable=True)  # Vector representation of experience
    last_ai_analysis = Column(String(255), nullable=True)
    
    # Profile status
    is_complete = Column(Boolean, default=False, nullable=False)
    profile_score = Column(Float, nullable=True)  # AI-generated profile completeness score
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<Profile(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
    
    @property
    def full_location(self) -> str:
        """Get full location string"""
        parts = [self.city, self.state, self.country]
        return ", ".join([part for part in parts if part])
    
    @property
    def skills_list(self) -> list:
        """Get list of skill names"""
        if self.skills:
            return [skill.get("name", "") for skill in self.skills if skill.get("name")]
        return []
    
    @property
    def experience_summary(self) -> str:
        """Get summary of work experience"""
        if self.experience:
            total_years = sum(exp.get("duration_years", 0) for exp in self.experience)
            return f"{total_years} years of experience"
        return "No experience listed"
    
    def calculate_profile_score(self) -> float:
        """Calculate profile completeness score"""
        score = 0.0
        total_fields = 8
        
        if self.title:
            score += 1
        if self.summary:
            score += 1
        if self.skills:
            score += 1
        if self.experience:
            score += 1
        if self.education:
            score += 1
        if self.resume_url:
            score += 1
        if self.city and self.country:
            score += 1
        if self.salary_expectation_min:
            score += 1
        
        return (score / total_fields) * 100