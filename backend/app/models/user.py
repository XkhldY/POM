"""
User model for authentication and user management
"""

from sqlalchemy import Boolean, Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class User(Base):
    """User model for authentication and user management"""
    
    # User identification
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Account status
    last_login = Column(DateTime(timezone=True), nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Additional fields
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    jobs = relationship("Job", back_populates="employer")
    applications = relationship("Application", back_populates="applicant")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.is_active and self.is_verified
    
    def can_access_admin(self) -> bool:
        """Check if user can access admin features"""
        return self.is_superuser and self.is_active