"""
Job endpoints for job management
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.job_service import JobService
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobSearchRequest

router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new job posting
    """
    job_service = JobService(db)
    
    try:
        job = job_service.create_job(
            employer_id=current_user.id,
            **job_data.dict(exclude_unset=True)
        )
        
        return JobResponse.from_orm(job)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a job by ID
    """
    job_service = JobService(db)
    job = job_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Increment view count
    job_service.increment_job_views(job_id)
    
    return JobResponse.from_orm(job)


@router.get("/slug/{slug}", response_model=JobResponse)
async def get_job_by_slug(
    slug: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a job by slug
    """
    job_service = JobService(db)
    job = job_service.get_job_by_slug(slug)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Increment view count
    job_service.increment_job_views(job.id)
    
    return JobResponse.from_orm(job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a job posting
    """
    job_service = JobService(db)
    job = job_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user owns the job
    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this job"
        )
    
    try:
        updated_job = job_service.update_job(job_id, **job_data.dict(exclude_unset=True))
        return JobResponse.from_orm(updated_job)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a job posting
    """
    job_service = JobService(db)
    job = job_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user owns the job
    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this job"
        )
    
    success = job_service.delete_job(job_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete job"
        )


@router.post("/{job_id}/publish", response_model=JobResponse)
async def publish_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Publish a draft job
    """
    job_service = JobService(db)
    job = job_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user owns the job
    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this job"
        )
    
    try:
        published_job = job_service.publish_job(job_id)
        return JobResponse.from_orm(published_job)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{job_id}/close", response_model=JobResponse)
async def close_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Close a published job
    """
    job_service = JobService(db)
    job = job_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user owns the job
    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this job"
        )
    
    try:
        closed_job = job_service.close_job(job_id)
        return JobResponse.from_orm(closed_job)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get list of jobs with pagination and optional status filter
    """
    job_service = JobService(db)
    
    # Convert status string to enum if provided
    from app.models.job import JobStatus
    job_status = None
    if status:
        try:
            job_status = JobStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid job status"
            )
    
    jobs = job_service.get_jobs(skip=skip, limit=limit, status=job_status)
    
    return [JobResponse.from_orm(job) for job in jobs]


@router.get("/search/", response_model=List[JobResponse])
async def search_jobs(
    query: str = Query(None),
    job_type: str = Query(None),
    experience_level: str = Query(None),
    location: str = Query(None),
    remote_only: bool = Query(None),
    min_salary: int = Query(None, ge=0),
    max_salary: int = Query(None, ge=0),
    industry: str = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Search jobs with multiple filters
    """
    job_service = JobService(db)
    
    # Convert enum strings to actual enums
    from app.models.job import JobType, ExperienceLevel
    job_type_enum = None
    experience_level_enum = None
    
    if job_type:
        try:
            job_type_enum = JobType(job_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid job type"
            )
    
    if experience_level:
        try:
            experience_level_enum = ExperienceLevel(experience_level)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid experience level"
            )
    
    jobs = job_service.search_jobs(
        query=query,
        job_type=job_type_enum,
        experience_level=experience_level_enum,
        location=location,
        remote_only=remote_only,
        min_salary=min_salary,
        max_salary=max_salary,
        industry=industry,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    
    return [JobResponse.from_orm(job) for job in jobs]


@router.get("/employer/me", response_model=List[JobResponse])
async def get_my_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get jobs posted by the current user
    """
    job_service = JobService(db)
    jobs = job_service.get_jobs_by_employer(
        employer_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return [JobResponse.from_orm(job) for job in jobs]


@router.get("/company/{company_id}", response_model=List[JobResponse])
async def get_jobs_by_company(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get jobs by company ID
    """
    job_service = JobService(db)
    jobs = job_service.get_jobs_by_company(
        company_id=company_id,
        skip=skip,
        limit=limit
    )
    
    return [JobResponse.from_orm(job) for job in jobs]


@router.get("/featured/", response_model=List[JobResponse])
async def get_featured_jobs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get featured jobs
    """
    job_service = JobService(db)
    jobs = job_service.get_featured_jobs(limit=limit)
    
    return [JobResponse.from_orm(job) for job in jobs]


@router.get("/recent/", response_model=List[JobResponse])
async def get_recent_jobs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get most recent published jobs
    """
    job_service = JobService(db)
    jobs = job_service.get_recent_jobs(limit=limit)
    
    return [JobResponse.from_orm(job) for job in jobs]


@router.get("/stats/count")
async def get_jobs_count(
    status: str = Query(None),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get job statistics
    """
    job_service = JobService(db)
    
    # Convert status string to enum if provided
    job_status = None
    if status:
        from app.models.job import JobStatus
        try:
            job_status = JobStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid job status"
            )
    
    count = job_service.get_jobs_count(status=job_status)
    
    return {
        "count": count,
        "status": status or "all"
    }


@router.get("/stats/by-status")
async def get_jobs_by_status(db: Session = Depends(get_db)) -> Any:
    """
    Get job counts by status
    """
    job_service = JobService(db)
    
    from app.models.job import JobStatus
    
    stats = {}
    for status in JobStatus:
        count = job_service.get_jobs_count(status=status)
        stats[status.value] = count
    
    return stats