"""
Profile service for profile management operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.profile import Profile
from app.models.user import User
from app.core.exceptions import NotFoundError, ValidationError


class ProfileService:
    """Service class for profile operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_profile_by_id(self, profile_id: int) -> Optional[Profile]:
        """Get profile by ID"""
        return self.db.query(Profile).filter(Profile.id == profile_id).first()
    
    def get_profile_by_user_id(self, user_id: int) -> Optional[Profile]:
        """Get profile by user ID"""
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()
    
    def get_profiles(self, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get list of profiles with pagination"""
        return self.db.query(Profile).offset(skip).limit(limit).all()
    
    def create_profile(self, user_id: int, **kwargs) -> Profile:
        """Create a new profile for a user"""
        # Check if profile already exists
        existing_profile = self.get_profile_by_user_id(user_id)
        if existing_profile:
            raise ValidationError("Profile already exists for this user")
        
        # Create profile
        db_profile = Profile(user_id=user_id, **kwargs)
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        
        return db_profile
    
    def update_profile(self, profile_id: int, **kwargs) -> Optional[Profile]:
        """Update profile information"""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            raise NotFoundError("Profile", profile_id)
        
        # Update fields
        for field, value in kwargs.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        # Recalculate profile score
        profile.profile_score = profile.calculate_profile_score()
        profile.is_complete = profile.profile_score >= 80.0
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def update_profile_by_user_id(self, user_id: int, **kwargs) -> Optional[Profile]:
        """Update profile by user ID"""
        profile = self.get_profile_by_user_id(user_id)
        if not profile:
            raise NotFoundError("Profile", f"user_id: {user_id}")
        
        return self.update_profile(profile.id, **kwargs)
    
    def delete_profile(self, profile_id: int) -> bool:
        """Delete a profile"""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return False
        
        self.db.delete(profile)
        self.db.commit()
        return True
    
    def search_profiles(self, query: str, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Search profiles by title, skills, or location"""
        search_filter = or_(
            Profile.title.ilike(f"%{query}%"),
            Profile.city.ilike(f"%{query}%"),
            Profile.state.ilike(f"%{query}%"),
            Profile.country.ilike(f"%{query}%")
        )
        
        return self.db.query(Profile).filter(search_filter).offset(skip).limit(limit).all()
    
    def get_profiles_by_skills(self, skills: List[str], skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get profiles that have specific skills"""
        # This is a simplified search - in production, you'd use vector similarity
        profiles = []
        for profile in self.get_profiles(skip, limit):
            if profile.skills:
                profile_skills = [skill.get("name", "").lower() for skill in profile.skills]
                if any(skill.lower() in profile_skills for skill in skills):
                    profiles.append(profile)
        
        return profiles
    
    def get_profiles_by_location(self, city: str = None, state: str = None, country: str = None, 
                               remote_available: bool = None, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get profiles by location criteria"""
        filters = []
        
        if city:
            filters.append(Profile.city.ilike(f"%{city}%"))
        if state:
            filters.append(Profile.state.ilike(f"%{state}%"))
        if country:
            filters.append(Profile.country.ilike(f"%{country}%"))
        if remote_available is not None:
            filters.append(Profile.is_remote_available == remote_available)
        
        if not filters:
            return self.get_profiles(skip, limit)
        
        return self.db.query(Profile).filter(and_(*filters)).offset(skip).limit(limit).all()
    
    def get_profiles_by_experience(self, min_years: int = None, max_years: int = None, 
                                 skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get profiles by experience level"""
        filters = []
        
        if min_years is not None:
            filters.append(Profile.years_of_experience >= min_years)
        if max_years is not None:
            filters.append(Profile.years_of_experience <= max_years)
        
        if not filters:
            return self.get_profiles(skip, limit)
        
        return self.db.query(Profile).filter(and_(*filters)).offset(skip).limit(limit).all()
    
    def update_ai_analysis(self, profile_id: int, ai_data: Dict[str, Any]) -> Optional[Profile]:
        """Update profile with AI analysis results"""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            raise NotFoundError("Profile", profile_id)
        
        # Update AI-generated fields
        if "skills_vector" in ai_data:
            profile.skills_vector = ai_data["skills_vector"]
        if "experience_vector" in ai_data:
            profile.experience_vector = ai_data["experience_vector"]
        if "profile_score" in ai_data:
            profile.profile_score = ai_data["profile_score"]
        
        profile.last_ai_analysis = "now"  # Should be actual timestamp
        profile.is_complete = profile.profile_score >= 80.0 if profile.profile_score else False
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def get_complete_profiles(self, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get profiles that are marked as complete"""
        return self.db.query(Profile).filter(Profile.is_complete == True).offset(skip).limit(limit).all()
    
    def get_profiles_by_score_range(self, min_score: float, max_score: float, 
                                  skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get profiles within a score range"""
        return self.db.query(Profile).filter(
            and_(
                Profile.profile_score >= min_score,
                Profile.profile_score <= max_score
            )
        ).offset(skip).limit(limit).all()
    
    def get_profiles_count(self) -> int:
        """Get total count of profiles"""
        return self.db.query(Profile).count()
    
    def get_complete_profiles_count(self) -> int:
        """Get count of complete profiles"""
        return self.db.query(Profile).filter(Profile.is_complete == True).count()