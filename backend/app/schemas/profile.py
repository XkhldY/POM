"""
Profile schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class ProfileBase(BaseModel):
    """Base profile schema"""
    title: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = None
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    
    # Location
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_remote_available: bool = False
    
    # Skills and expertise
    skills: Optional[List[Dict[str, Any]]] = None
    languages: Optional[List[Dict[str, Any]]] = None
    
    # Education
    education: Optional[List[Dict[str, Any]]] = None
    
    # Work experience
    experience: Optional[List[Dict[str, Any]]] = None
    
    # Social profiles
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    
    # Preferences
    salary_expectation_min: Optional[int] = Field(None, ge=0)
    salary_expectation_max: Optional[int] = Field(None, ge=0)
    preferred_work_types: Optional[List[str]] = None
    preferred_industries: Optional[List[str]] = None
    
    @validator('salary_expectation_max')
    def validate_salary_range(cls, v, values):
        if v is not None and 'salary_expectation_min' in values:
            min_salary = values['salary_expectation_min']
            if min_salary is not None and v < min_salary:
                raise ValueError('Maximum salary must be greater than minimum salary')
        return v
    
    @validator('skills')
    def validate_skills(cls, v):
        if v is not None:
            for skill in v:
                if not isinstance(skill, dict) or 'name' not in skill:
                    raise ValueError('Each skill must have a name')
        return v
    
    @validator('languages')
    def validate_languages(cls, v):
        if v is not None:
            for language in v:
                if not isinstance(language, dict) or 'name' not in language:
                    raise ValueError('Each language must have a name')
        return v


class ProfileCreate(ProfileBase):
    """Schema for profile creation"""
    pass


class ProfileUpdate(ProfileBase):
    """Schema for profile updates"""
    pass


class ProfileResponse(ProfileBase):
    """Schema for profile response"""
    id: int
    user_id: int
    resume_url: Optional[str] = None
    resume_filename: Optional[str] = None
    resume_uploaded_at: Optional[str] = None
    
    # AI-generated data
    skills_vector: Optional[List[float]] = None
    experience_vector: Optional[List[float]] = None
    last_ai_analysis: Optional[str] = None
    
    # Profile status
    is_complete: bool
    profile_score: Optional[float] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProfileSearchRequest(BaseModel):
    """Schema for profile search requests"""
    query: Optional[str] = None
    skills: Optional[List[str]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    remote_available: Optional[bool] = None
    min_experience: Optional[int] = Field(None, ge=0)
    max_experience: Optional[int] = Field(None, ge=0)
    min_salary: Optional[int] = Field(None, ge=0)
    max_salary: Optional[int] = Field(None, ge=0)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("relevance", regex="^(relevance|date|experience|score)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")


class ProfileSearchResponse(BaseModel):
    """Schema for profile search responses"""
    profiles: List[ProfileResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ProfileStats(BaseModel):
    """Schema for profile statistics"""
    total_profiles: int
    complete_profiles: int
    incomplete_profiles: int
    profiles_with_resume: int
    average_profile_score: Optional[float] = None
    profiles_by_experience_level: Dict[str, int]
    profiles_by_location: Dict[str, int]
    top_skills: List[Dict[str, Any]]


class ResumeUploadResponse(BaseModel):
    """Schema for resume upload response"""
    message: str
    filename: str
    file_size: Optional[int] = None
    upload_timestamp: datetime


class AIAnalysisRequest(BaseModel):
    """Schema for AI analysis requests"""
    profile_id: int
    analysis_type: str = Field(..., regex="^(skills|experience|overall)$")


class AIAnalysisResponse(BaseModel):
    """Schema for AI analysis responses"""
    profile_id: int
    analysis_type: str
    analysis_result: Dict[str, Any]
    confidence_score: float
    analysis_timestamp: datetime
    processing_time_ms: Optional[int] = None