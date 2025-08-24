"""
Company schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl


class CompanyBase(BaseModel):
    """Base company schema"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    founded_year: Optional[int] = Field(None, ge=1800, le=2100)
    
    # Location
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_remote_friendly: bool = False
    
    # Branding
    logo_url: Optional[HttpUrl] = None
    banner_url: Optional[HttpUrl] = None
    mission_statement: Optional[str] = None
    vision_statement: Optional[str] = None
    
    # Social media
    linkedin_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    facebook_url: Optional[HttpUrl] = None
    instagram_url: Optional[HttpUrl] = None
    
    # Company details
    benefits: Optional[List[str]] = None
    culture_tags: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    
    # Contact information
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_address: Optional[str] = None
    
    @validator('founded_year')
    def validate_founded_year(cls, v):
        if v is not None and v > datetime.now().year:
            raise ValueError('Founded year cannot be in the future')
        return v
    
    @validator('company_size')
    def validate_company_size(cls, v):
        if v is not None:
            valid_sizes = [
                "1-10", "11-50", "51-200", "201-500", 
                "501-1000", "1001-5000", "5001-10000", "10000+"
            ]
            if v not in valid_sizes:
                raise ValueError(f'Company size must be one of: {", ".join(valid_sizes)}')
        return v


class CompanyCreate(CompanyBase):
    """Schema for company creation"""
    pass


class CompanyUpdate(CompanyBase):
    """Schema for company updates"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    founded_year: Optional[int] = Field(None, ge=1800, le=2100)


class CompanyResponse(CompanyBase):
    """Schema for company response"""
    id: int
    slug: str
    is_verified: bool
    is_active: bool
    
    # SEO
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[List[str]] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CompanySearchRequest(BaseModel):
    """Schema for company search requests"""
    query: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    remote_friendly: Optional[bool] = None
    verified_only: bool = False
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("relevance", regex="^(relevance|name|date|size)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")


class CompanySearchResponse(BaseModel):
    """Schema for company search responses"""
    companies: List[CompanyResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class CompanyStats(BaseModel):
    """Schema for company statistics"""
    total_companies: int
    verified_companies: int
    active_companies: int
    companies_by_industry: Dict[str, int]
    companies_by_size: Dict[str, int]
    companies_by_location: Dict[str, int]
    remote_friendly_companies: int
    average_founded_year: Optional[int] = None


class CompanyReview(BaseModel):
    """Schema for company reviews"""
    id: int
    company_id: int
    reviewer_id: int
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., max_length=200)
    review_text: str = Field(..., min_length=10)
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    is_verified_employee: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompanyReviewCreate(BaseModel):
    """Schema for creating company reviews"""
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., max_length=200)
    review_text: str = Field(..., min_length=10)
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    is_verified_employee: bool = False


class CompanyReviewUpdate(BaseModel):
    """Schema for updating company reviews"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    review_text: Optional[str] = Field(None, min_length=10)
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None


class CompanyInsights(BaseModel):
    """Schema for company insights"""
    company_id: int
    total_jobs_posted: int
    total_applications_received: int
    average_application_quality: Optional[float] = None
    popular_job_categories: List[str]
    average_salary_range: Optional[Dict[str, int]] = None
    employee_satisfaction_score: Optional[float] = None
    hiring_trends: Dict[str, Any]
    market_position: Optional[str] = None


class CompanyVerification(BaseModel):
    """Schema for company verification"""
    company_id: int
    verification_type: str = Field(..., regex="^(email|phone|document|manual)$")
    verification_status: str = Field(..., regex="^(pending|approved|rejected)$")
    verification_notes: Optional[str] = None
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompanyContact(BaseModel):
    """Schema for company contact information"""
    company_id: int
    primary_contact: Optional[str] = None
    primary_email: Optional[str] = Field(None, max_length=255)
    primary_phone: Optional[str] = Field(None, max_length=20)
    secondary_contact: Optional[str] = None
    secondary_email: Optional[str] = Field(None, max_length=255)
    secondary_phone: Optional[str] = Field(None, max_length=20)
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    business_hours: Optional[Dict[str, str]] = None
    
    class Config:
        from_attributes = True