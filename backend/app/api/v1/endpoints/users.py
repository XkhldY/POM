"""
User endpoints for user management
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_current_user, get_current_superuser
from app.services.user_service import UserService
from app.schemas.user import UserUpdate, UserResponse, UserListResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_my_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user information
    """
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_user(
            current_user.id, **user_data.dict(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(updated_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete current user account
    """
    user_service = UserService(db)
    
    success = user_service.delete_user(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user by ID
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user can view this profile
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    return UserResponse.from_orm(user)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get list of users with pagination (superuser only)
    """
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    
    return [UserResponse.from_orm(user) for user in users]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update user information (superuser only)
    """
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_user(
            user_id, **user_data.dict(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(updated_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete user account (superuser only)
    """
    user_service = UserService(db)
    
    # Prevent superuser from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )


@router.post("/{user_id}/verify", response_model=UserResponse)
async def verify_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify a user account (superuser only)
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Update user verification status
        updated_user = user_service.update_user(
            user_id, is_verified=True
        )
        
        return UserResponse.from_orm(updated_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Activate a user account (superuser only)
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Update user activation status
        updated_user = user_service.update_user(
            user_id, is_active=True
        )
        
        return UserResponse.from_orm(updated_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Deactivate a user account (superuser only)
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent superuser from deactivating themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    try:
        # Update user activation status
        updated_user = user_service.update_user(
            user_id, is_active=False
        )
        
        return UserResponse.from_orm(updated_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/search/", response_model=List[UserResponse])
async def search_users(
    query: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Search users by query (superuser only)
    """
    user_service = UserService(db)
    users = user_service.search_users(query=query, skip=skip, limit=limit)
    
    return [UserResponse.from_orm(user) for user in users]


@router.get("/stats/count")
async def get_users_count(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user statistics (superuser only)
    """
    user_service = UserService(db)
    
    return {
        "total_users": user_service.get_active_users_count(),
        "verified_users": user_service.get_verified_users_count(),
        "active_users": user_service.get_active_users_count()
    }


@router.get("/stats/overview")
async def get_users_overview(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get comprehensive user overview (superuser only)
    """
    user_service = UserService(db)
    
    # Get recent users (last 30 days)
    from datetime import datetime, timedelta
    recent_date = datetime.utcnow() - timedelta(days=30)
    
    # This would require additional methods in UserService
    # For now, return basic stats
    stats = {
        "total_users": user_service.get_active_users_count(),
        "verified_users": user_service.get_verified_users_count(),
        "active_users": user_service.get_active_users_count(),
        "recent_users": 0,  # TODO: Implement this
        "users_by_status": {
            "active": user_service.get_active_users_count(),
            "inactive": 0,  # TODO: Implement this
            "verified": user_service.get_verified_users_count(),
            "unverified": 0  # TODO: Implement this
        }
    }
    
    return stats


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str = Query(...),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Reset user password (superuser only)
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Reset user password
        success = user_service.reset_password(user_id, new_password)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password"
            )
        
        return {"message": "Password reset successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me/preferences")
async def get_my_preferences(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user preferences
    """
    # TODO: Implement user preferences system
    return {
        "message": "User preferences not yet implemented",
        "user_id": current_user.id
    }


@router.put("/me/preferences")
async def update_my_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user preferences
    """
    # TODO: Implement user preferences system
    return {
        "message": "User preferences not yet implemented",
        "user_id": current_user.id,
        "preferences": preferences
    }