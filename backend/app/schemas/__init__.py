"""
Schemas package for Pydantic models
"""

from .auth import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenData,
    PasswordReset,
    PasswordResetConfirm,
    EmailVerification
)

from .user import (
    UserUpdate,
    UserListResponse,
    UserPasswordChange,
    UserPasswordReset,
    UserPasswordResetConfirm,
    UserEmailVerification,
    UserResendVerification,
    UserProfileUpdate,
    UserNotificationPreferences,
    UserPrivacySettings,
    UserAccountSettings,
    UserStats,
    UserSearchRequest,
    UserSearchResponse,
    UserActivity,
    UserSession,
    UserConnection,
    UserConnectionRequest,
    UserConnectionUpdate
)

from .profile import (
    ProfileBase,
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileSearchRequest,
    ProfileSearchResponse,
    ProfileStats,
    ResumeUploadResponse,
    AIAnalysisRequest,
    AIAnalysisResponse
)

from .job import (
    JobBase,
    JobCreate,
    JobUpdate,
    JobResponse,
    JobSearchRequest,
    JobSearchResponse,
    JobStats,
    JobApplicationRequest,
    JobApplicationResponse,
    JobRecommendation,
    JobAnalytics
)

from .company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanySearchRequest,
    CompanySearchResponse,
    CompanyStats,
    CompanyReview,
    CompanyReviewCreate,
    CompanyReviewUpdate,
    CompanyInsights,
    CompanyVerification,
    CompanyContact
)

from .application import (
    ApplicationBase,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationStatusUpdate,
    ApplicationSearchRequest,
    ApplicationSearchResponse,
    ApplicationStats,
    ApplicationNote,
    ApplicationNoteCreate,
    ApplicationNoteUpdate,
    ApplicationCommunication,
    ApplicationCommunicationCreate,
    ApplicationInterview,
    ApplicationInterviewCreate,
    ApplicationOffer,
    ApplicationOfferCreate,
    ApplicationWithdrawal
)

from .search import (
    SearchRequest,
    JobSearchRequest,
    ProfileSearchRequest,
    CompanySearchRequest,
    GlobalSearchRequest,
    SearchResponse,
    JobSearchResponse,
    ProfileSearchResponse,
    CompanySearchResponse,
    GlobalSearchResponse,
    SearchSuggestion,
    SearchSuggestionsResponse,
    SearchFacet,
    SearchFacetsResponse,
    SearchFilter,
    AdvancedSearchRequest,
    SearchMetadata,
    SearchAnalytics,
    SearchHistory,
    SearchHistoryCreate,
    SearchPreferences,
    SearchPreferencesUpdate,
    SavedSearch,
    SavedSearchCreate,
    SavedSearchUpdate
)

from .ai import (
    AIAnalysisRequest,
    ResumeAnalysisRequest,
    JobAnalysisRequest,
    SkillsExtractionRequest,
    MatchingAnalysisRequest,
    ProfileAnalysisRequest,
    AIAnalysisResponse,
    ResumeAnalysisResponse,
    JobAnalysisResponse,
    SkillsExtractionResponse,
    MatchingAnalysisResponse,
    ProfileAnalysisResponse,
    AIRecommendation,
    JobRecommendation,
    ProfileRecommendation,
    SkillRecommendation,
    CareerRecommendation,
    InterviewRecommendation,
    AICoverLetterRequest,
    AICoverLetterResponse,
    AIInterviewPrepRequest,
    AIInterviewPrepResponse,
    AIServiceStatus,
    AIUsageMetrics,
    AIErrorResponse,
    AIBatchRequest,
    AIBatchResponse
)

__all__ = [
    # Auth schemas
    "UserBase", "UserCreate", "UserLogin", "UserResponse", "Token", "TokenData",
    "PasswordReset", "PasswordResetConfirm", "EmailVerification",
    
    # User schemas
    "UserUpdate", "UserListResponse", "UserPasswordChange", "UserPasswordReset",
    "UserPasswordResetConfirm", "UserEmailVerification", "UserResendVerification",
    "UserProfileUpdate", "UserNotificationPreferences", "UserPrivacySettings",
    "UserAccountSettings", "UserStats", "UserSearchRequest", "UserSearchResponse",
    "UserActivity", "UserSession", "UserConnection", "UserConnectionRequest",
    "UserConnectionUpdate",
    
    # Profile schemas
    "ProfileBase", "ProfileCreate", "ProfileUpdate", "ProfileResponse",
    "ProfileSearchRequest", "ProfileSearchResponse", "ProfileStats",
    "ResumeUploadResponse", "AIAnalysisRequest", "AIAnalysisResponse",
    
    # Job schemas
    "JobBase", "JobCreate", "JobUpdate", "JobResponse", "JobSearchRequest",
    "JobSearchResponse", "JobStats", "JobApplicationRequest", "JobApplicationResponse",
    "JobRecommendation", "JobAnalytics",
    
    # Company schemas
    "CompanyBase", "CompanyCreate", "CompanyUpdate", "CompanyResponse",
    "CompanySearchRequest", "CompanySearchResponse", "CompanyStats", "CompanyReview",
    "CompanyReviewCreate", "CompanyReviewUpdate", "CompanyInsights",
    "CompanyVerification", "CompanyContact",
    
    # Application schemas
    "ApplicationBase", "ApplicationCreate", "ApplicationUpdate", "ApplicationResponse",
    "ApplicationStatusUpdate", "ApplicationSearchRequest", "ApplicationSearchResponse",
    "ApplicationStats", "ApplicationNote", "ApplicationNoteCreate", "ApplicationNoteUpdate",
    "ApplicationCommunication", "ApplicationCommunicationCreate", "ApplicationInterview",
    "ApplicationInterviewCreate", "ApplicationOffer", "ApplicationOfferCreate",
    "ApplicationWithdrawal",
    
    # Search schemas
    "SearchRequest", "JobSearchRequest", "ProfileSearchRequest", "CompanySearchRequest",
    "GlobalSearchRequest", "SearchResponse", "JobSearchResponse", "ProfileSearchResponse",
    "CompanySearchResponse", "GlobalSearchResponse", "SearchSuggestion",
    "SearchSuggestionsResponse", "SearchFacet", "SearchFacetsResponse", "SearchFilter",
    "AdvancedSearchRequest", "SearchMetadata", "SearchAnalytics", "SearchHistory",
    "SearchHistoryCreate", "SearchPreferences", "SearchPreferencesUpdate",
    "SavedSearch", "SavedSearchCreate", "SavedSearchUpdate",
    
    # AI schemas
    "AIAnalysisRequest", "ResumeAnalysisRequest", "JobAnalysisRequest",
    "SkillsExtractionRequest", "MatchingAnalysisRequest", "ProfileAnalysisRequest",
    "AIAnalysisResponse", "ResumeAnalysisResponse", "JobAnalysisResponse",
    "SkillsExtractionResponse", "MatchingAnalysisResponse", "ProfileAnalysisResponse",
    "AIRecommendation", "JobRecommendation", "ProfileRecommendation", "SkillRecommendation",
    "CareerRecommendation", "InterviewRecommendation", "AICoverLetterRequest",
    "AICoverLetterResponse", "AIInterviewPrepRequest", "AIInterviewPrepResponse",
    "AIServiceStatus", "AIUsageMetrics", "AIErrorResponse", "AIBatchRequest",
    "AIBatchResponse"
]