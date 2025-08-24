"""
Search schemas for request/response validation
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

from app.schemas.job import JobResponse
from app.schemas.profile import ProfileResponse
from app.schemas.company import CompanyResponse


class SearchRequest(BaseModel):
    """Base search request schema"""
    query: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("relevance", regex="^(relevance|date|name|score)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")


class JobSearchRequest(SearchRequest):
    """Schema for job search requests"""
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    remote_only: Optional[bool] = None
    min_salary: Optional[int] = Field(None, ge=0)
    max_salary: Optional[int] = Field(None, ge=0)
    industry: Optional[str] = None
    skills: Optional[List[str]] = None
    company_id: Optional[int] = None
    employer_id: Optional[int] = None
    date_posted: Optional[str] = Field(None, regex="^(today|week|month|year|all)$")


class ProfileSearchRequest(SearchRequest):
    """Schema for profile search requests"""
    skills: Optional[List[str]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    remote_available: Optional[bool] = None
    min_experience: Optional[int] = Field(None, ge=0)
    max_experience: Optional[int] = Field(None, ge=0)
    min_salary: Optional[int] = Field(None, ge=0)
    max_salary: Optional[int] = Field(None, ge=0)
    education_level: Optional[str] = None
    languages: Optional[List[str]] = None
    profile_completeness: Optional[str] = Field(None, regex="^(complete|incomplete|all)$")


class CompanySearchRequest(SearchRequest):
    """Schema for company search requests"""
    industry: Optional[str] = None
    company_size: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    remote_friendly: Optional[bool] = None
    verified_only: bool = False
    founded_after: Optional[int] = Field(None, ge=1800)
    founded_before: Optional[int] = Field(None, le=2100)
    benefits: Optional[List[str]] = None
    technologies: Optional[List[str]] = None


class GlobalSearchRequest(SearchRequest):
    """Schema for global search requests"""
    entity_types: List[str] = Field(default=["jobs", "profiles", "companies"], 
                                   regex="^(jobs|profiles|companies)$")
    filters: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Base search response schema"""
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    query: Optional[str] = None
    filters_applied: Optional[Dict[str, Any]] = None
    search_time_ms: Optional[float] = None


class JobSearchResponse(SearchResponse):
    """Schema for job search responses"""
    jobs: List[JobResponse]
    facets: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class ProfileSearchResponse(SearchResponse):
    """Schema for profile search responses"""
    profiles: List[ProfileResponse]
    facets: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class CompanySearchResponse(SearchResponse):
    """Schema for company search responses"""
    companies: List[CompanyResponse]
    facets: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class GlobalSearchResponse(BaseModel):
    """Schema for global search responses"""
    query: str
    total_count: int
    search_time_ms: Optional[float] = None
    results: Dict[str, Dict[str, Any]]


class SearchSuggestion(BaseModel):
    """Schema for search suggestions"""
    text: str
    type: str = Field(..., regex="^(job_title|company_name|location|skill|industry)$")
    count: Optional[int] = None
    relevance_score: Optional[float] = None


class SearchSuggestionsResponse(BaseModel):
    """Schema for search suggestions response"""
    query: str
    suggestions: Dict[str, List[SearchSuggestion]]
    total_suggestions: int


class SearchFacet(BaseModel):
    """Schema for search facets"""
    name: str
    values: List[Dict[str, Any]]
    total_count: int


class SearchFacetsResponse(BaseModel):
    """Schema for search facets response"""
    query: Optional[str] = None
    facets: Dict[str, SearchFacet]
    total_facets: int


class SearchFilter(BaseModel):
    """Schema for search filters"""
    field: str
    operator: str = Field(..., regex="^(eq|ne|gt|gte|lt|lte|in|nin|contains|starts_with|ends_with)$")
    value: Union[str, int, float, bool, List[Any]]
    label: Optional[str] = None


class AdvancedSearchRequest(BaseModel):
    """Schema for advanced search requests"""
    query: Optional[str] = None
    filters: List[SearchFilter]
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("relevance", regex="^(relevance|date|name|score|salary|experience)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")
    entity_types: List[str] = Field(default=["jobs"], regex="^(jobs|profiles|companies)$")
    include_facets: bool = True
    include_suggestions: bool = True


class SearchMetadata(BaseModel):
    """Schema for search metadata"""
    query_id: Optional[str] = None
    search_type: str
    entity_type: str
    filters_applied: Dict[str, Any]
    sort_applied: Dict[str, str]
    pagination_applied: Dict[str, int]
    search_performance: Dict[str, Any]
    timestamp: str


class SearchAnalytics(BaseModel):
    """Schema for search analytics"""
    total_searches: int
    searches_today: int
    searches_this_week: int
    searches_this_month: int
    average_search_time_ms: float
    most_popular_queries: List[Dict[str, Any]]
    search_conversion_rate: Optional[float] = None
    top_searched_skills: List[str]
    top_searched_locations: List[str]
    top_searched_industries: List[str]


class SearchHistory(BaseModel):
    """Schema for search history"""
    id: int
    user_id: int
    query: str
    filters_applied: Dict[str, Any]
    results_count: int
    search_time_ms: float
    clicked_results: Optional[List[int]] = None
    created_at: str
    
    class Config:
        from_attributes = True


class SearchHistoryCreate(BaseModel):
    """Schema for creating search history"""
    query: str
    filters_applied: Dict[str, Any]
    results_count: int
    search_time_ms: float
    clicked_results: Optional[List[int]] = None


class SearchPreferences(BaseModel):
    """Schema for search preferences"""
    user_id: int
    default_page_size: int = Field(20, ge=10, le=100)
    default_sort_by: str = Field("relevance", regex="^(relevance|date|name|score)$")
    default_sort_order: str = Field("desc", regex="^(asc|desc)$")
    save_search_history: bool = True
    enable_search_suggestions: bool = True
    enable_search_analytics: bool = True
    preferred_job_types: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_industries: Optional[List[str]] = None
    salary_range: Optional[Dict[str, int]] = None
    experience_range: Optional[Dict[str, int]] = None
    
    class Config:
        from_attributes = True


class SearchPreferencesUpdate(BaseModel):
    """Schema for updating search preferences"""
    default_page_size: Optional[int] = Field(None, ge=10, le=100)
    default_sort_by: Optional[str] = Field(None, regex="^(relevance|date|name|score)$")
    default_sort_order: Optional[str] = Field(None, regex="^(asc|desc)$")
    save_search_history: Optional[bool] = None
    enable_search_suggestions: Optional[bool] = None
    enable_search_analytics: Optional[bool] = None
    preferred_job_types: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_industries: Optional[List[str]] = None
    salary_range: Optional[Dict[str, int]] = None
    experience_range: Optional[Dict[str, int]] = None


class SavedSearch(BaseModel):
    """Schema for saved searches"""
    id: int
    user_id: int
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    query: str
    filters: Dict[str, Any]
    entity_types: List[str]
    is_active: bool = True
    notification_frequency: Optional[str] = Field(None, regex="^(daily|weekly|monthly|never)$")
    last_run: Optional[str] = None
    results_count: Optional[int] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class SavedSearchCreate(BaseModel):
    """Schema for creating saved searches"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    query: str
    filters: Dict[str, Any]
    entity_types: List[str]
    notification_frequency: Optional[str] = Field(None, regex="^(daily|weekly|monthly|never)$")


class SavedSearchUpdate(BaseModel):
    """Schema for updating saved searches"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    entity_types: Optional[List[str]] = None
    is_active: Optional[bool] = None
    notification_frequency: Optional[str] = Field(None, regex="^(daily|weekly|monthly|never)$")