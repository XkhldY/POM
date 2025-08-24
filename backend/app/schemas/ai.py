"""
AI schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class AIAnalysisRequest(BaseModel):
    """Base schema for AI analysis requests"""
    analysis_type: str = Field(..., regex="^(resume|job|skills|matching|profile|overall)$")
    content: str = Field(..., min_length=10)
    options: Optional[Dict[str, Any]] = None


class ResumeAnalysisRequest(AIAnalysisRequest):
    """Schema for resume analysis requests"""
    analysis_type: str = Field(default="resume", regex="^resume$")
    file_format: Optional[str] = Field(None, regex="^(pdf|doc|docx|txt)$")
    extract_skills: bool = True
    extract_experience: bool = True
    extract_education: bool = True
    extract_contact_info: bool = True
    generate_summary: bool = True


class JobAnalysisRequest(AIAnalysisRequest):
    """Schema for job analysis requests"""
    analysis_type: str = Field(default="job", regex="^job$")
    extract_requirements: bool = True
    extract_skills: bool = True
    extract_experience: bool = True
    classify_job_level: bool = True
    estimate_salary_range: bool = True
    identify_benefits: bool = True


class SkillsExtractionRequest(AIAnalysisRequest):
    """Schema for skills extraction requests"""
    analysis_type: str = Field(default="skills", regex="^skills$")
    skill_categories: Optional[List[str]] = Field(None, regex="^(technical|soft|domain|language|certification)$")
    proficiency_levels: bool = True
    skill_confidence: bool = True
    extract_related_skills: bool = True


class MatchingAnalysisRequest(AIAnalysisRequest):
    """Schema for candidate-job matching requests"""
    analysis_type: str = Field(default="matching", regex="^matching$")
    candidate_profile: str = Field(..., min_length=10)
    job_requirements: str = Field(..., min_length=10)
    include_skill_gaps: bool = True
    include_recommendations: bool = True
    include_risk_factors: bool = True
    calculate_match_score: bool = True


class ProfileAnalysisRequest(AIAnalysisRequest):
    """Schema for profile analysis requests"""
    analysis_type: str = Field(default="profile", regex="^profile$")
    analysis_focus: str = Field(default="overall", regex="^(overall|skills|experience|education|summary)$")
    generate_suggestions: bool = True
    calculate_completeness: bool = True
    identify_improvements: bool = True


class AIAnalysisResponse(BaseModel):
    """Base schema for AI analysis responses"""
    analysis_id: str
    analysis_type: str
    status: str = Field(..., regex="^(success|failed|processing)$")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    processing_time_ms: Optional[float] = None
    timestamp: datetime
    version: str = "1.0.0"


class ResumeAnalysisResponse(AIAnalysisResponse):
    """Schema for resume analysis responses"""
    analysis_type: str = Field(default="resume", regex="^resume$")
    extracted_data: Dict[str, Any]
    skills: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    contact_info: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    recommendations: Optional[List[str]] = None


class JobAnalysisResponse(AIAnalysisResponse):
    """Schema for job analysis responses"""
    analysis_type: str = Field(default="job", regex="^job$")
    extracted_data: Dict[str, Any]
    required_skills: List[Dict[str, Any]]
    preferred_skills: List[Dict[str, Any]]
    experience_requirements: Dict[str, Any]
    job_level: Optional[str] = None
    estimated_salary_range: Optional[Dict[str, Any]] = None
    benefits: Optional[List[str]] = None
    industry_classification: Optional[str] = None


class SkillsExtractionResponse(AIAnalysisResponse):
    """Schema for skills extraction responses"""
    analysis_type: str = Field(default="skills", regex="^skills$")
    extracted_skills: List[Dict[str, Any]]
    skill_categories: Dict[str, List[Dict[str, Any]]]
    confidence_scores: Dict[str, float]
    related_skills: Optional[List[Dict[str, Any]]] = None
    skill_trends: Optional[List[str]] = None


class MatchingAnalysisResponse(AIAnalysisResponse):
    """Schema for candidate-job matching responses"""
    analysis_type: str = Field(default="matching", regex="^matching$")
    overall_match_score: float = Field(..., ge=0.0, le=100.0)
    skill_match_percentage: float = Field(..., ge=0.0, le=100.0)
    experience_match_percentage: float = Field(..., ge=0.0, le=100.0)
    key_strengths: List[str]
    areas_for_improvement: List[str]
    specific_skill_gaps: List[str]
    recommendations: List[str]
    risk_factors: Optional[List[str]] = None
    match_breakdown: Dict[str, Any]


class ProfileAnalysisResponse(AIAnalysisResponse):
    """Schema for profile analysis responses"""
    analysis_type: str = Field(default="profile", regex="^profile$")
    profile_score: float = Field(..., ge=0.0, le=100.0)
    completeness_percentage: float = Field(..., ge=0.0, le=100.0)
    strengths: List[str]
    areas_for_improvement: List[str]
    suggestions: List[str]
    skill_recommendations: Optional[List[str]] = None
    experience_recommendations: Optional[List[str]] = None
    education_recommendations: Optional[List[str]] = None


class AIRecommendation(BaseModel):
    """Schema for AI-generated recommendations"""
    id: str
    type: str = Field(..., regex="^(job|profile|skill|career|interview)$")
    title: str
    description: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    priority: str = Field(..., regex="^(low|medium|high|critical)$")
    category: str
    actionable: bool = True
    created_at: datetime
    expires_at: Optional[datetime] = None


class JobRecommendation(AIRecommendation):
    """Schema for job recommendations"""
    type: str = Field(default="job", regex="^job$")
    job_id: int
    match_score: float = Field(..., ge=0.0, le=100.0)
    matching_skills: List[str]
    skill_gaps: List[str]
    salary_match: Optional[bool] = None
    location_match: Optional[bool] = None
    company_match: Optional[bool] = None


class ProfileRecommendation(AIRecommendation):
    """Schema for profile recommendations"""
    type: str = Field(default="profile", regex="^profile$")
    profile_id: int
    match_score: float = Field(..., ge=0.0, le=100.0)
    matching_skills: List[str]
    experience_match: Optional[bool] = None
    education_match: Optional[bool] = None
    location_match: Optional[bool] = None


class SkillRecommendation(AIRecommendation):
    """Schema for skill recommendations"""
    type: str = Field(default="skill", regex="^skill$")
    skill_name: str
    skill_category: str
    proficiency_level: str
    learning_resources: Optional[List[str]] = None
    estimated_learning_time: Optional[str] = None
    market_demand: Optional[str] = None
    salary_impact: Optional[str] = None


class CareerRecommendation(AIRecommendation):
    """Schema for career recommendations"""
    type: str = Field(default="career", regex="^career$")
    career_path: str
    next_steps: List[str]
    timeline: Optional[str] = None
    required_certifications: Optional[List[str]] = None
    salary_progression: Optional[Dict[str, Any]] = None
    market_outlook: Optional[str] = None


class InterviewRecommendation(AIRecommendation):
    """Schema for interview recommendations"""
    type: str = Field(default="interview", regex="^interview$")
    interview_type: str
    preparation_topics: List[str]
    common_questions: List[str]
    tips: List[str]
    resources: Optional[List[str]] = None
    estimated_prep_time: Optional[str] = None


class AICoverLetterRequest(BaseModel):
    """Schema for AI cover letter generation requests"""
    job_title: str
    company_name: str
    job_description: str
    candidate_profile: str
    tone: str = Field(default="professional", regex="^(professional|friendly|enthusiastic|formal|casual)$")
    length: str = Field(default="medium", regex="^(short|medium|long)$")
    focus_areas: Optional[List[str]] = None
    include_specific_examples: bool = True
    customize_for_company: bool = True


class AICoverLetterResponse(BaseModel):
    """Schema for AI cover letter generation responses"""
    cover_letter: str
    generation_id: str
    word_count: int
    tone_used: str
    focus_areas_covered: List[str]
    customization_level: str
    suggestions: Optional[List[str]] = None
    generated_at: datetime


class AIInterviewPrepRequest(BaseModel):
    """Schema for AI interview preparation requests"""
    job_title: str
    company_name: str
    job_description: str
    candidate_profile: str
    interview_type: str = Field(..., regex="^(phone|video|onsite|technical|behavioral|panel)$")
    preparation_focus: Optional[List[str]] = None
    include_questions: bool = True
    include_tips: bool = True
    include_research: bool = True


class AIInterviewPrepResponse(BaseModel):
    """Schema for AI interview preparation responses"""
    preparation_id: str
    key_talking_points: List[str]
    potential_questions: List[str]
    questions_to_ask: List[str]
    areas_to_emphasize: List[str]
    potential_challenges: List[str]
    company_research_suggestions: List[str]
    preparation_timeline: Optional[str] = None
    generated_at: datetime


class AIServiceStatus(BaseModel):
    """Schema for AI service status"""
    service: str
    model: str
    api_key_configured: bool
    status: str = Field(..., regex="^(operational|degraded|down|not_configured)$")
    response_time_ms: Optional[float] = None
    last_check: datetime
    version: str
    features: List[str]
    rate_limits: Optional[Dict[str, Any]] = None


class AIUsageMetrics(BaseModel):
    """Schema for AI usage metrics"""
    user_id: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens_used: int
    total_cost: Optional[float] = None
    requests_today: int
    requests_this_week: int
    requests_this_month: int
    most_used_features: List[str]
    average_response_time_ms: float
    last_request: Optional[datetime] = None


class AIErrorResponse(BaseModel):
    """Schema for AI error responses"""
    error_type: str
    error_message: str
    error_code: Optional[str] = None
    suggestion: Optional[str] = None
    retry_after: Optional[int] = None
    timestamp: datetime
    request_id: Optional[str] = None


class AIBatchRequest(BaseModel):
    """Schema for AI batch processing requests"""
    batch_id: str
    requests: List[AIAnalysisRequest]
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")
    callback_url: Optional[str] = None
    max_concurrent: int = Field(default=5, ge=1, le=20)
    timeout_seconds: int = Field(default=300, ge=60, le=3600)


class AIBatchResponse(BaseModel):
    """Schema for AI batch processing responses"""
    batch_id: str
    status: str = Field(..., regex="^(processing|completed|failed|partial)$")
    total_requests: int
    completed_requests: int
    failed_requests: int
    results: List[AIAnalysisResponse]
    errors: List[AIErrorResponse]
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_processing_time_ms: Optional[float] = None