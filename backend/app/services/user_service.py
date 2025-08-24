"""
User service for user management operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service class for user operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email_or_username(self, email_or_username: str) -> Optional[User]:
        """Get user by email or username"""
        return self.db.query(User).filter(
            or_(User.email == email_or_username, User.username == email_or_username)
        ).first()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,  # Users need to verify email
            is_superuser=False
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user (soft delete by setting is_active to False)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        user = self.get_user_by_email_or_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def verify_user_email(self, user_id: int) -> bool:
        """Verify user email address"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_verified = True
        user.email_verification_token = None
        self.db.commit()
        return True
    
    def set_email_verification_token(self, user_id: int, token: str) -> bool:
        """Set email verification token for user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.email_verification_token = token
        self.db.commit()
        return True
    
    def set_password_reset_token(self, user_id: int, token: str) -> bool:
        """Set password reset token for user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.password_reset_token = token
        self.db.commit()
        return True
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.hashed_password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        self.db.commit()
        return True
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.last_login = "now"  # This should be updated with actual timestamp
        self.db.commit()
        return True
    
    def get_active_users_count(self) -> int:
        """Get count of active users"""
        return self.db.query(User).filter(User.is_active == True).count()
    
    def get_verified_users_count(self) -> int:
        """Get count of verified users"""
        return self.db.query(User).filter(User.is_verified == True).count()
    
    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by name, email, or username"""
        search_filter = or_(
            User.first_name.ilike(f"%{query}%"),
            User.last_name.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%"),
            User.username.ilike(f"%{query}%")
        )
        
        return self.db.query(User).filter(search_filter).offset(skip).limit(limit).all()