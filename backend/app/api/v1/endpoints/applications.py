"""
Application endpoints for job application management
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.application_service import ApplicationService
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter()


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new job application
    """
    application_service = ApplicationService(db)
    
    try:
        application = application_service.create_application(
            applicant_id=current_user.id,
            **application_data.dict(exclude_unset=True)
        )
        
        return ApplicationResponse.from_orm(application)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get an application by ID
    """
    application_service = ApplicationService(db)
    application = application_service.get_application_by_id(application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if user can view this application
    if application.applicant_id != current_user.id:
        # TODO: Add employer authorization check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this application"
        )
    
    return ApplicationResponse.from_orm(application)


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: int,
    application_data: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update an application
    """
    application_service = ApplicationService(db)
    application = application_service.get_application_by_id(application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if user can update this application
    if application.applicant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this application"
        )
    
    try:
        updated_application = application_service.update_application(
            application_id, **application_data.dict(exclude_unset=True)
        )
        return ApplicationResponse.from_orm(updated_application)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete an application
    """
    application_service = ApplicationService(db)
    application = application_service.get_application_by_id(application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if user can delete this application
    if application.applicant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this application"
        )
    
    success = application_service.delete_application(application_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application"
        )


@router.post("/{application_id}/withdraw", response_model=ApplicationResponse)
async def withdraw_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Withdraw an application
    """
    application_service = ApplicationService(db)
    application = application_service.get_application_by_id(application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if user can withdraw this application
    if application.applicant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to withdraw this application"
        )
    
    try:
        withdrawn_application = application_service.withdraw_application(application_id)
        return ApplicationResponse.from_orm(withdrawn_application)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{application_id}/shortlist", response_model=ApplicationResponse)
async def shortlist_application(
    application_id: int,
    notes: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Shortlist an application (employer only)
    """
    application_service = ApplicationService(db)
    application = application_service.get_application_by_id(application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # TODO: Add employer authorization check
    # For now, allow any authenticated user
    
    try:
        shortlisted_application = application_service.shortlist_application(
            application_id, notes=notes
        )
        return ApplicationResponse.from_orm(shortlisted_application)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{application_id}/reject", response_model=ApplicationResponse)
async def reject_application(
    application_id: int,
    notes: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Reject an application (employer only)
    """
    application_service = ApplicationService(db)
    application = application_service.get_application_by_id(application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # TODO: Add employer authorization check
    # For now, allow any authenticated user
    
    try:
        rejected_application = application_service.reject_application(
            application_id, notes=notes
        )
        return ApplicationResponse.from_orm(rejected_application)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get list of applications with pagination and optional status filter
    """
    application_service = ApplicationService(db)
    
    # Convert status string to enum if provided
    from app.models.application import ApplicationStatus
    application_status = None
    if status:
        try:
            application_status = ApplicationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid application status"
            )
    
    applications = application_service.get_applications(
        skip=skip, limit=limit, status=application_status
    )
    
    return [ApplicationResponse.from_orm(application) for application in applications]


@router.get("/job/{job_id}", response_model=List[ApplicationResponse])
async def get_applications_by_job(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get applications for a specific job
    """
    # TODO: Add employer authorization check
    # For now, allow any authenticated user
    
    application_service = ApplicationService(db)
    applications = application_service.get_applications_by_job(
        job_id=job_id, skip=skip, limit=limit
    )
    
    return [ApplicationResponse.from_orm(application) for application in applications]


@router.get("/applicant/me", response_model=List[ApplicationResponse])
async def get_my_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get applications submitted by the current user
    """
    application_service = ApplicationService(db)
    applications = application_service.get_applications_by_applicant(
        applicant_id=current_user.id, skip=skip, limit=limit
    )
    
    return [ApplicationResponse.from_orm(application) for application in applications]


@router.get("/employer/me", response_model=List[ApplicationResponse])
async def get_employer_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get applications for jobs posted by the current user
    """
    application_service = ApplicationService(db)
    applications = application_service.get_applications_by_employer(
        employer_id=current_user.id, skip=skip, limit=limit
    )
    
    return [ApplicationResponse.from_orm(application) for application in applications]


@router.get("/search/", response_model=List[ApplicationResponse])
async def search_applications(
    query: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Search applications by query
    """
    application_service = ApplicationService(db)
    applications = application_service.search_applications(
        query=query, skip=skip, limit=limit
    )
    
    return [ApplicationResponse.from_orm(application) for application in applications]


@router.get("/by-status/", response_model=List[ApplicationResponse])
async def get_applications_by_status(
    status: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get applications with a specific status
    """
    application_service = ApplicationService(db)
    
    # Convert status string to enum
    from app.models.application import ApplicationStatus
    try:
        application_status = ApplicationStatus(status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid application status"
        )
    
    applications = application_service.get_applications_by_status(
        status=application_status, skip=skip, limit=limit
    )
    
    return [ApplicationResponse.from_orm(application) for application in applications]


@router.get("/active/", response_model=List[ApplicationResponse])
async def get_active_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get active applications
    """
    application_service = ApplicationService(db)
    applications = application_service.get_active_applications(skip=skip, limit=limit)
    
    return [ApplicationResponse.from_orm(application) for application in applications]


@router.get("/shortlisted/", response_model=List[ApplicationResponse])
async def get_shortlisted_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get shortlisted applications
    """
    application_service = ApplicationService(db)
    applications = application_service.get_shortlisted_applications(skip=skip, limit=limit)
    
    return [ApplicationResponse.from_orm(application) for application in applications]


@router.get("/stats/count")
async def get_applications_count(
    status: str = Query(None),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get application statistics
    """
    application_service = ApplicationService(db)
    
    # Convert status string to enum if provided
    application_status = None
    if status:
        from app.models.application import ApplicationStatus
        try:
            application_status = ApplicationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid application status"
            )
    
    count = application_service.get_applications_count(status=application_status)
    
    return {
        "count": count,
        "status": status or "all"
    }


@router.get("/stats/active")
async def get_active_applications_count(db: Session = Depends(get_db)) -> Any:
    """
    Get count of active applications
    """
    application_service = ApplicationService(db)
    count = application_service.get_active_applications_count()
    
    return {"active_applications_count": count}


@router.get("/stats/shortlisted")
async def get_shortlisted_applications_count(db: Session = Depends(get_db)) -> Any:
    """
    Get count of shortlisted applications
    """
    application_service = ApplicationService(db)
    count = application_service.get_shortlisted_applications_count()
    
    return {"shortlisted_applications_count": count}