"""
Application schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from app.models.application import ApplicationStatus


class ApplicationBase(BaseModel):
    """Base application schema"""
    job_id: int
    applicant_id: int
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    expected_salary: Optional[int] = Field(None, ge=0)
    earliest_start_date: Optional[datetime] = None
    additional_questions: Optional[Dict[str, str]] = None
    source: Optional[str] = Field(None, max_length=100)  # How they found the job
    referral_name: Optional[str] = Field(None, max_length=100)
    
    # Application preferences
    is_remote_ok: bool = True
    is_relocation_ok: bool = False
    preferred_work_schedule: Optional[str] = Field(None, max_length=50)
    
    # Additional information
    portfolio_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    other_urls: Optional[List[str]] = None
    
    @validator('earliest_start_date')
    def validate_start_date(cls, v):
        if v is not None and v < datetime.now():
            raise ValueError('Earliest start date cannot be in the past')
        return v
    
    @validator('expected_salary')
    def validate_salary(cls, v):
        if v is not None and v < 0:
            raise ValueError('Expected salary cannot be negative')
        return v


class ApplicationCreate(ApplicationBase):
    """Schema for application creation"""
    pass


class ApplicationUpdate(BaseModel):
    """Schema for application updates"""
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    expected_salary: Optional[int] = Field(None, ge=0)
    earliest_start_date: Optional[datetime] = None
    additional_questions: Optional[Dict[str, str]] = None
    is_remote_ok: Optional[bool] = None
    is_relocation_ok: Optional[bool] = None
    preferred_work_schedule: Optional[str] = Field(None, max_length=50)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    other_urls: Optional[List[str]] = None


class ApplicationResponse(ApplicationBase):
    """Schema for application response"""
    id: int
    status: ApplicationStatus
    ai_match_score: Optional[float] = None
    skill_match_percentage: Optional[float] = None
    experience_match_percentage: Optional[float] = None
    
    # AI analysis
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_recommendations: Optional[List[str]] = None
    ai_risk_factors: Optional[List[str]] = None
    
    # Tracking
    is_favorite: bool = False
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Communication history
    communication_history: Optional[List[Dict[str, Any]]] = None
    
    # Interview details
    interview_scheduled: Optional[datetime] = None
    interview_type: Optional[str] = None
    interview_location: Optional[str] = None
    interview_notes: Optional[str] = None
    
    # Offer details
    offer_made: Optional[datetime] = None
    offer_amount: Optional[int] = None
    offer_currency: Optional[str] = None
    offer_status: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    status_updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApplicationStatusUpdate(BaseModel):
    """Schema for updating application status"""
    status: ApplicationStatus
    notes: Optional[str] = None
    next_steps: Optional[str] = None
    scheduled_date: Optional[datetime] = None


class ApplicationSearchRequest(BaseModel):
    """Schema for application search requests"""
    query: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    job_id: Optional[int] = None
    applicant_id: Optional[int] = None
    employer_id: Optional[int] = None
    min_match_score: Optional[float] = Field(None, ge=0, le=100)
    max_match_score: Optional[float] = Field(None, ge=0, le=100)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("created_at", regex="^(created_at|updated_at|match_score|status)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")


class ApplicationSearchResponse(BaseModel):
    """Schema for application search responses"""
    applications: List[ApplicationResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ApplicationStats(BaseModel):
    """Schema for application statistics"""
    total_applications: int
    applications_by_status: Dict[str, int]
    applications_by_job: Dict[int, int]
    applications_by_applicant: Dict[int, int]
    average_match_score: Optional[float] = None
    applications_today: int
    applications_this_week: int
    applications_this_month: int
    conversion_rate: Optional[float] = None


class ApplicationNote(BaseModel):
    """Schema for application notes"""
    id: int
    application_id: int
    author_id: int
    note_type: str = Field(..., regex="^(general|interview|feedback|decision)$")
    note_text: str = Field(..., min_length=1)
    is_private: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationNoteCreate(BaseModel):
    """Schema for creating application notes"""
    note_type: str = Field(..., regex="^(general|interview|feedback|decision)$")
    note_text: str = Field(..., min_length=1)
    is_private: bool = False


class ApplicationNoteUpdate(BaseModel):
    """Schema for updating application notes"""
    note_type: Optional[str] = Field(None, regex="^(general|interview|feedback|decision)$")
    note_text: Optional[str] = Field(None, min_length=1)
    is_private: Optional[bool] = None


class ApplicationCommunication(BaseModel):
    """Schema for application communication"""
    id: int
    application_id: int
    sender_id: int
    recipient_id: int
    communication_type: str = Field(..., regex="^(email|sms|in_app|phone)$")
    subject: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=1)
    is_read: bool = False
    is_replied: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApplicationCommunicationCreate(BaseModel):
    """Schema for creating application communication"""
    recipient_id: int
    communication_type: str = Field(..., regex="^(email|sms|in_app|phone)$")
    subject: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=1)


class ApplicationInterview(BaseModel):
    """Schema for application interviews"""
    id: int
    application_id: int
    interview_type: str = Field(..., regex="^(phone|video|onsite|technical|behavioral|panel)$")
    scheduled_date: datetime
    duration_minutes: int = Field(..., ge=15, le=480)
    location: Optional[str] = None
    video_url: Optional[str] = None
    interviewer_ids: List[int]
    notes: Optional[str] = None
    status: str = Field(..., regex="^(scheduled|completed|cancelled|rescheduled)$")
    feedback: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationInterviewCreate(BaseModel):
    """Schema for creating application interviews"""
    interview_type: str = Field(..., regex="^(phone|video|onsite|technical|behavioral|panel)$")
    scheduled_date: datetime
    duration_minutes: int = Field(..., ge=15, le=480)
    location: Optional[str] = None
    video_url: Optional[str] = None
    interviewer_ids: List[int]
    notes: Optional[str] = None


class ApplicationOffer(BaseModel):
    """Schema for application offers"""
    id: int
    application_id: int
    offer_amount: int = Field(..., ge=0)
    offer_currency: str = Field(default="USD", max_length=3)
    offer_type: str = Field(..., regex="^(full_time|part_time|contract|internship)$")
    benefits: Optional[List[str]] = None
    start_date: datetime
    offer_deadline: datetime
    notes: Optional[str] = None
    status: str = Field(..., regex="^(pending|accepted|rejected|expired|withdrawn)$")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationOfferCreate(BaseModel):
    """Schema for creating application offers"""
    offer_amount: int = Field(..., ge=0)
    offer_currency: str = Field(default="USD", max_length=3)
    offer_type: str = Field(..., regex="^(full_time|part_time|contract|internship)$")
    benefits: Optional[List[str]] = None
    start_date: datetime
    offer_deadline: datetime
    notes: Optional[str] = None


class ApplicationWithdrawal(BaseModel):
    """Schema for application withdrawal"""
    application_id: int
    withdrawal_reason: str = Field(..., min_length=1)
    feedback: Optional[str] = None
    is_reconsideration_possible: bool = False
    withdrawal_date: datetime = Field(default_factory=datetime.utcnow)