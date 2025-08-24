"""
Profile endpoints for profile management
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.profile_service import ProfileService
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

router = APIRouter()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new profile for the current user
    """
    profile_service = ProfileService(db)
    
    try:
        profile = profile_service.create_profile(
            user_id=current_user.id,
            **profile_data.dict(exclude_unset=True)
        )
        
        return ProfileResponse.from_orm(profile)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current user's profile
    """
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse.from_orm(profile)


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user's profile
    """
    profile_service = ProfileService(db)
    
    try:
        profile = profile_service.update_profile_by_user_id(
            user_id=current_user.id,
            **profile_data.dict(exclude_unset=True)
        )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return ProfileResponse.from_orm(profile)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a profile by ID
    """
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_id(profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse.from_orm(profile)


@router.get("/", response_model=List[ProfileResponse])
async def get_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get list of profiles with pagination
    """
    profile_service = ProfileService(db)
    profiles = profile_service.get_profiles(skip=skip, limit=limit)
    
    return [ProfileResponse.from_orm(profile) for profile in profiles]


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete current user's profile
    """
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    success = profile_service.delete_profile(profile.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile"
        )


@router.post("/me/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload resume for current user's profile
    """
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, DOC, DOCX, and TXT files are allowed."
        )
    
    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 10MB."
        )
    
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first."
        )
    
    # TODO: Implement file upload to storage service
    # For now, just update the profile with file information
    try:
        profile_service.update_profile(
            profile.id,
            resume_filename=file.filename,
            resume_uploaded_at="now"  # Should be actual timestamp
        )
        
        return {
            "message": "Resume uploaded successfully",
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )


@router.get("/search/", response_model=List[ProfileResponse])
async def search_profiles(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Search profiles by query
    """
    profile_service = ProfileService(db)
    profiles = profile_service.search_profiles(query=query, skip=skip, limit=limit)
    
    return [ProfileResponse.from_orm(profile) for profile in profiles]


@router.get("/by-skills/", response_model=List[ProfileResponse])
async def get_profiles_by_skills(
    skills: str,  # Comma-separated skills
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get profiles that have specific skills
    """
    profile_service = ProfileService(db)
    skills_list = [skill.strip() for skill in skills.split(",")]
    profiles = profile_service.get_profiles_by_skills(skills=skills_list, skip=skip, limit=limit)
    
    return [ProfileResponse.from_orm(profile) for profile in profiles]


@router.get("/by-location/", response_model=List[ProfileResponse])
async def get_profiles_by_location(
    city: str = None,
    state: str = None,
    country: str = None,
    remote_available: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get profiles by location criteria
    """
    profile_service = ProfileService(db)
    profiles = profile_service.get_profiles_by_location(
        city=city,
        state=state,
        country=country,
        remote_available=remote_available,
        skip=skip,
        limit=limit
    )
    
    return [ProfileResponse.from_orm(profile) for profile in profiles]


@router.get("/by-experience/", response_model=List[ProfileResponse])
async def get_profiles_by_experience(
    min_years: int = None,
    max_years: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get profiles by experience level
    """
    profile_service = ProfileService(db)
    profiles = profile_service.get_profiles_by_experience(
        min_years=min_years,
        max_years=max_years,
        skip=skip,
        limit=limit
    )
    
    return [ProfileResponse.from_orm(profile) for profile in profiles]


@router.get("/complete/", response_model=List[ProfileResponse])
async def get_complete_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get profiles that are marked as complete
    """
    profile_service = ProfileService(db)
    profiles = profile_service.get_complete_profiles(skip=skip, limit=limit)
    
    return [ProfileResponse.from_orm(profile) for profile in profiles]


@router.get("/stats/count")
async def get_profiles_count(db: Session = Depends(get_db)) -> Any:
    """
    Get profile statistics
    """
    profile_service = ProfileService(db)
    
    return {
        "total_profiles": profile_service.get_profiles_count(),
        "complete_profiles": profile_service.get_complete_profiles_count()
    }