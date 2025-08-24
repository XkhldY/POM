"""
User schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, EmailStr


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, regex="^(male|female|other|prefer_not_to_say)$")
    
    # Location
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = None
    
    # Preferences
    language: str = Field(default="en", max_length=5)
    currency: str = Field(default="USD", max_length=3)
    notification_preferences: Optional[Dict[str, bool]] = None
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v is not None and v > datetime.now():
            raise ValueError('Date of birth cannot be in the future')
        return v


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('confirm_password')
    def validate_password_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdate(BaseModel):
    """Schema for user updates"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, regex="^(male|female|other|prefer_not_to_say)$")
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = None
    language: Optional[str] = Field(None, max_length=5)
    currency: Optional[str] = Field(None, max_length=3)
    notification_preferences: Optional[Dict[str, bool]] = None
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    social_links: Optional[Dict[str, str]] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    email_verified_at: Optional[datetime] = None
    phone_verified_at: Optional[datetime] = None
    
    # Profile information
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    
    # Account status
    last_login: Optional[datetime] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list response"""
    users: List[UserResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    remember_me: bool = False


class UserPasswordChange(BaseModel):
    """Schema for user password change"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str = Field(..., min_length=8)
    
    @validator('confirm_new_password')
    def validate_password_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v


class UserPasswordReset(BaseModel):
    """Schema for user password reset request"""
    email: EmailStr


class UserPasswordResetConfirm(BaseModel):
    """Schema for user password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str = Field(..., min_length=8)
    
    @validator('confirm_new_password')
    def validate_password_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v


class UserEmailVerification(BaseModel):
    """Schema for user email verification"""
    token: str


class UserResendVerification(BaseModel):
    """Schema for resending user verification email"""
    email: EmailStr


class UserProfileUpdate(BaseModel):
    """Schema for user profile updates"""
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    social_links: Optional[Dict[str, str]] = None
    professional_title: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    twitter_url: Optional[str] = Field(None, max_length=500)


class UserNotificationPreferences(BaseModel):
    """Schema for user notification preferences"""
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    in_app_notifications: bool = True
    
    # Specific notification types
    job_alerts: bool = True
    application_updates: bool = True
    profile_views: bool = True
    skill_recommendations: bool = True
    company_updates: bool = False
    marketing_emails: bool = False
    
    # Frequency preferences
    digest_frequency: str = Field(default="weekly", regex="^(daily|weekly|monthly|never)$")
    quiet_hours_start: Optional[str] = Field(None, regex="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, regex="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")


class UserPrivacySettings(BaseModel):
    """Schema for user privacy settings"""
    profile_visibility: str = Field(default="public", regex="^(public|private|connections_only)$")
    show_email: bool = False
    show_phone: bool = False
    show_location: bool = True
    show_salary: bool = False
    show_company: bool = True
    allow_profile_views: bool = True
    allow_messages: bool = True
    allow_connection_requests: bool = True
    data_sharing: bool = False
    analytics_tracking: bool = True


class UserAccountSettings(BaseModel):
    """Schema for user account settings"""
    two_factor_enabled: bool = False
    session_timeout_minutes: int = Field(default=480, ge=15, le=1440)  # 8 hours default
    max_concurrent_sessions: int = Field(default=5, ge=1, le=10)
    require_password_change_days: Optional[int] = Field(None, ge=30, le=365)
    account_deletion_delay_days: int = Field(default=30, ge=7, le=90)


class UserStats(BaseModel):
    """Schema for user statistics"""
    total_users: int
    active_users: int
    verified_users: int
    users_today: int
    users_this_week: int
    users_this_month: int
    users_by_status: Dict[str, int]
    users_by_location: Dict[str, int]
    average_profile_completeness: Optional[float] = None


class UserSearchRequest(BaseModel):
    """Schema for user search requests"""
    query: str
    status: Optional[str] = Field(None, regex="^(active|inactive|verified|unverified|all)$")
    role: Optional[str] = Field(None, regex="^(user|employer|admin|superuser|all)$")
    location: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("created_at", regex="^(created_at|updated_at|last_login|name|email)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")


class UserSearchResponse(BaseModel):
    """Schema for user search responses"""
    users: List[UserResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    query: str
    filters_applied: Dict[str, Any]


class UserActivity(BaseModel):
    """Schema for user activity"""
    id: int
    user_id: int
    activity_type: str = Field(..., regex="^(login|logout|profile_update|job_apply|search|message|connection)$")
    description: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserSession(BaseModel):
    """Schema for user session"""
    id: int
    user_id: int
    session_token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


class UserConnection(BaseModel):
    """Schema for user connections"""
    id: int
    user_id: int
    connected_user_id: int
    connection_type: str = Field(..., regex="^(colleague|friend|mentor|mentee|alumni|other)$")
    status: str = Field(..., regex="^(pending|accepted|rejected|blocked)$")
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserConnectionRequest(BaseModel):
    """Schema for user connection requests"""
    connected_user_id: int
    connection_type: str = Field(..., regex="^(colleague|friend|mentor|mentee|alumni|other)$")
    message: Optional[str] = Field(None, max_length=500)


class UserConnectionUpdate(BaseModel):
    """Schema for updating user connections"""
    status: str = Field(..., regex="^(accepted|rejected|blocked)$")
    message: Optional[str] = Field(None, max_length=500)