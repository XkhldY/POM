"""
Search endpoints for implementing search functionality
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.services.search_service import SearchService
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter()


@router.get("/jobs/", response_model=Dict[str, Any])
async def search_jobs(
    query: str = Query(None),
    job_type: str = Query(None),
    experience_level: str = Query(None),
    location: str = Query(None),
    remote_only: bool = Query(None),
    min_salary: int = Query(None, ge=0),
    max_salary: int = Query(None, ge=0),
    industry: str = Query(None),
    sort_by: str = Query("relevance"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Search jobs with multiple filters
    """
    search_service = SearchService(db)
    
    # Build filters dictionary
    filters = {}
    if job_type:
        filters["job_type"] = job_type
    if experience_level:
        filters["experience_level"] = experience_level
    if location:
        filters["location"] = location
    if remote_only is not None:
        filters["remote_only"] = remote_only
    if min_salary:
        filters["min_salary"] = min_salary
    if max_salary:
        filters["max_salary"] = max_salary
    if industry:
        filters["industry"] = industry
    
    try:
        jobs, total_count, metadata = search_service.search_jobs(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        return {
            "jobs": [job.__dict__ for job in jobs],
            "total_count": total_count,
            "metadata": metadata
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/profiles/", response_model=Dict[str, Any])
async def search_profiles(
    query: str = Query(None),
    min_experience: int = Query(None, ge=0),
    max_experience: int = Query(None, ge=0),
    location: str = Query(None),
    remote_available: bool = Query(None),
    min_salary: int = Query(None, ge=0),
    max_salary: int = Query(None, ge=0),
    sort_by: str = Query("relevance"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Search profiles with multiple filters
    """
    search_service = SearchService(db)
    
    # Build filters dictionary
    filters = {}
    if min_experience:
        filters["min_experience"] = min_experience
    if max_experience:
        filters["max_experience"] = max_experience
    if location:
        filters["location"] = location
    if remote_available is not None:
        filters["remote_available"] = remote_available
    if min_salary:
        filters["min_salary"] = min_salary
    if max_salary:
        filters["max_salary"] = max_salary
    
    try:
        profiles, total_count, metadata = search_service.search_profiles(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        return {
            "profiles": [profile.__dict__ for profile in profiles],
            "total_count": total_count,
            "metadata": metadata
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/companies/", response_model=Dict[str, Any])
async def search_companies(
    query: str = Query(None),
    industry: str = Query(None),
    company_size: str = Query(None),
    location: str = Query(None),
    remote_friendly: bool = Query(None),
    verified_only: bool = Query(False),
    sort_by: str = Query("relevance"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Search companies with multiple filters
    """
    search_service = SearchService(db)
    
    # Build filters dictionary
    filters = {}
    if industry:
        filters["industry"] = industry
    if company_size:
        filters["company_size"] = company_size
    if location:
        filters["location"] = location
    if remote_friendly is not None:
        filters["remote_friendly"] = remote_friendly
    if verified_only:
        filters["verified_only"] = verified_only
    
    try:
        companies, total_count, metadata = search_service.search_companies(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        return {
            "companies": [company.__dict__ for company in companies],
            "total_count": total_count,
            "metadata": metadata
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/global/", response_model=Dict[str, Any])
async def global_search(
    query: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Perform global search across all entities
    """
    search_service = SearchService(db)
    
    try:
        results = search_service.global_search(
            query=query,
            page=page,
            page_size=page_size
        )
        
        # Convert ORM objects to dictionaries
        for entity_type in ["jobs", "profiles", "companies"]:
            if entity_type in results and "items" in results[entity_type]:
                results[entity_type]["items"] = [
                    item.__dict__ for item in results[entity_type]["items"]
                ]
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Global search failed: {str(e)}"
        )


@router.get("/suggestions/", response_model=Dict[str, Any])
async def get_search_suggestions(
    query: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get search suggestions for autocomplete
    """
    search_service = SearchService(db)
    
    try:
        suggestions = search_service.get_search_suggestions(
            query=query,
            limit=limit
        )
        
        return suggestions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search suggestions: {str(e)}"
        )


@router.get("/jobs/featured/", response_model=Dict[str, Any])
async def get_featured_jobs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get featured jobs
    """
    from app.services.job_service import JobService
    
    job_service = JobService(db)
    
    try:
        jobs = job_service.get_featured_jobs(limit=limit)
        
        return {
            "jobs": [job.__dict__ for job in jobs],
            "count": len(jobs)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get featured jobs: {str(e)}"
        )


@router.get("/jobs/recent/", response_model=Dict[str, Any])
async def get_recent_jobs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get most recent published jobs
    """
    from app.services.job_service import JobService
    
    job_service = JobService(db)
    
    try:
        jobs = job_service.get_recent_jobs(limit=limit)
        
        return {
            "jobs": [job.__dict__ for job in jobs],
            "count": len(jobs)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent jobs: {str(e)}"
        )


@router.get("/profiles/complete/", response_model=Dict[str, Any])
async def get_complete_profiles(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get profiles that are marked as complete
    """
    from app.services.profile_service import ProfileService
    
    profile_service = ProfileService(db)
    
    try:
        profiles = profile_service.get_complete_profiles(limit=limit)
        
        return {
            "profiles": [profile.__dict__ for profile in profiles],
            "count": len(profiles)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get complete profiles: {str(e)}"
        )


@router.get("/companies/verified/", response_model=Dict[str, Any])
async def get_verified_companies(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get verified companies
    """
    from app.services.company_service import CompanyService
    
    company_service = CompanyService(db)
    
    try:
        companies = company_service.get_verified_companies(limit=limit)
        
        return {
            "companies": [company.__dict__ for company in companies],
            "count": len(companies)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get verified companies: {str(e)}"
        )


@router.get("/stats/overview")
async def get_search_overview(db: Session = Depends(get_db)) -> Any:
    """
    Get search overview statistics
    """
    try:
        from app.services.job_service import JobService
        from app.services.profile_service import ProfileService
        from app.services.company_service import CompanyService
        
        job_service = JobService(db)
        profile_service = ProfileService(db)
        company_service = CompanyService(db)
        
        stats = {
            "jobs": {
                "total": job_service.get_jobs_count(),
                "published": job_service.get_jobs_count(status="published"),
                "featured": len(job_service.get_featured_jobs(limit=1000))
            },
            "profiles": {
                "total": profile_service.get_profiles_count(),
                "complete": profile_service.get_complete_profiles_count()
            },
            "companies": {
                "total": company_service.get_companies_count(),
                "verified": company_service.get_verified_companies_count()
            }
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search overview: {str(e)}"
        )