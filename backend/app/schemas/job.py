"""
Job schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from app.models.job import JobStatus, JobType, ExperienceLevel


class JobBase(BaseModel):
    """Base job schema"""
    title: str = Field(..., max_length=200)
    description: str = Field(..., min_length=10)
    company_id: Optional[int] = None
    employer_id: Optional[int] = None
    
    # Job details
    job_type: JobType
    experience_level: ExperienceLevel
    department: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    
    # Location
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_remote: bool = False
    remote_work_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    # Requirements
    skills_required: Optional[List[Dict[str, Any]]] = None
    skills_preferred: Optional[List[Dict[str, Any]]] = None
    experience_years_min: Optional[int] = Field(None, ge=0)
    experience_years_max: Optional[int] = Field(None, ge=0)
    education_required: Optional[str] = Field(None, max_length=100)
    certifications_required: Optional[List[str]] = None
    
    # Compensation
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    salary_currency: str = Field(default="USD", max_length=3)
    salary_period: str = Field(default="yearly", regex="^(yearly|monthly|hourly)$")
    benefits: Optional[List[str]] = None
    
    # Application details
    application_deadline: Optional[datetime] = None
    max_applications: Optional[int] = Field(None, ge=1)
    application_instructions: Optional[str] = None
    
    # Additional information
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    application_url: Optional[str] = Field(None, max_length=500)
    
    @validator('salary_max')
    def validate_salary_range(cls, v, values):
        if v is not None and 'salary_min' in values:
            min_salary = values['salary_min']
            if min_salary is not None and v < min_salary:
                raise ValueError('Maximum salary must be greater than minimum salary')
        return v
    
    @validator('experience_years_max')
    def validate_experience_range(cls, v, values):
        if v is not None and 'experience_years_min' in values:
            min_years = values['experience_years_min']
            if min_years is not None and v < min_years:
                raise ValueError('Maximum experience years must be greater than minimum')
        return v
    
    @validator('skills_required', 'skills_preferred')
    def validate_skills(cls, v):
        if v is not None:
            for skill in v:
                if not isinstance(skill, dict) or 'name' not in skill:
                    raise ValueError('Each skill must have a name')
        return v


class JobCreate(JobBase):
    """Schema for job creation"""
    pass


class JobUpdate(JobBase):
    """Schema for job updates"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None


class JobResponse(JobBase):
    """Schema for job response"""
    id: int
    slug: str
    status: JobStatus
    views_count: int
    current_applications: int
    max_applications: Optional[int] = None
    
    # AI-generated data
    skills_vector: Optional[List[float]] = None
    requirements_vector: Optional[List[float]] = None
    last_ai_analysis: Optional[str] = None
    
    # Metadata
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[List[str]] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobSearchRequest(BaseModel):
    """Schema for job search requests"""
    query: Optional[str] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    location: Optional[str] = None
    remote_only: Optional[bool] = None
    min_salary: Optional[int] = Field(None, ge=0)
    max_salary: Optional[int] = Field(None, ge=0)
    industry: Optional[str] = None
    skills: Optional[List[str]] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("relevance", regex="^(relevance|date|salary|views)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")


class JobSearchResponse(BaseModel):
    """Schema for job search responses"""
    jobs: List[JobResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class JobStats(BaseModel):
    """Schema for job statistics"""
    total_jobs: int
    published_jobs: int
    draft_jobs: int
    closed_jobs: int
    archived_jobs: int
    jobs_by_type: Dict[str, int]
    jobs_by_experience_level: Dict[str, int]
    jobs_by_industry: Dict[str, int]
    jobs_by_location: Dict[str, int]
    average_salary: Optional[float] = None
    total_applications: int
    total_views: int


class JobApplicationRequest(BaseModel):
    """Schema for job application requests"""
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    expected_salary: Optional[int] = Field(None, ge=0)
    earliest_start_date: Optional[datetime] = None
    additional_questions: Optional[Dict[str, str]] = None


class JobApplicationResponse(BaseModel):
    """Schema for job application responses"""
    id: int
    job_id: int
    applicant_id: int
    status: str
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    expected_salary: Optional[int] = None
    earliest_start_date: Optional[datetime] = None
    additional_questions: Optional[Dict[str, str]] = None
    ai_match_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobRecommendation(BaseModel):
    """Schema for job recommendations"""
    job: JobResponse
    match_score: float
    matching_skills: List[str]
    skill_gaps: List[str]
    recommendations: List[str]


class JobAnalytics(BaseModel):
    """Schema for job analytics"""
    job_id: int
    views_count: int
    applications_count: int
    application_rate: float
    average_application_quality: Optional[float] = None
    top_applicant_sources: List[str]
    time_to_fill: Optional[int] = None  # in days
    conversion_funnel: Dict[str, int]
    performance_metrics: Dict[str, Any]