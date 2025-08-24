"""
Company model for storing company information
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Company(Base):
    """Company model for storing company information"""
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    
    # Company details
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)  # e.g., "1-10", "11-50", "51-200"
    founded_year = Column(Integer, nullable=True)
    
    # Location
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    is_remote_friendly = Column(Boolean, default=False, nullable=False)
    
    # Company information
    logo_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    mission_statement = Column(Text, nullable=True)
    
    # Social media
    linkedin_url = Column(String(500), nullable=True)
    twitter_url = Column(String(500), nullable=True)
    facebook_url = Column(String(500), nullable=True)
    
    # Additional details
    benefits = Column(JSON, nullable=True)  # List of company benefits
    culture_tags = Column(JSON, nullable=True)  # List of culture-related tags
    technologies = Column(JSON, nullable=True)  # List of technologies used
    
    # Company status
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # SEO and visibility
    slug = Column(String(255), nullable=True, unique=True, index=True)
    
    # Relationships
    jobs = relationship("Job", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', industry='{self.industry}')>"
    
    @property
    def full_location(self) -> str:
        """Get full location string"""
        parts = [self.city, self.state, self.country]
        return ", ".join([part for part in parts if part])
    
    @property
    def display_name(self) -> str:
        """Get display name with verification status"""
        if self.is_verified:
            return f"{self.name} ✓"
        return self.name