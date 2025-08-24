"""
Company endpoints for company management
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_current_user, get_current_superuser
from app.services.company_service import CompanyService
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter()


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new company
    """
    company_service = CompanyService(db)
    
    try:
        company = company_service.create_company(**company_data.dict(exclude_unset=True))
        return CompanyResponse.from_orm(company)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a company by ID
    """
    company_service = CompanyService(db)
    company = company_service.get_company_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return CompanyResponse.from_orm(company)


@router.get("/slug/{slug}", response_model=CompanyResponse)
async def get_company_by_slug(
    slug: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a company by slug
    """
    company_service = CompanyService(db)
    company = company_service.get_company_by_slug(slug)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return CompanyResponse.from_orm(company)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a company
    """
    company_service = CompanyService(db)
    company = company_service.get_company_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # TODO: Add authorization check for company updates
    # For now, allow any authenticated user to update
    
    try:
        updated_company = company_service.update_company(company_id, **company_data.dict(exclude_unset=True))
        return CompanyResponse.from_orm(updated_company)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a company (superuser only)
    """
    company_service = CompanyService(db)
    company = company_service.get_company_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    success = company_service.delete_company(company_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete company"
        )


@router.post("/{company_id}/verify", response_model=CompanyResponse)
async def verify_company(
    company_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify a company (superuser only)
    """
    company_service = CompanyService(db)
    company = company_service.get_company_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    try:
        verified_company = company_service.verify_company(company_id)
        return CompanyResponse.from_orm(verified_company)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get list of companies with pagination
    """
    company_service = CompanyService(db)
    companies = company_service.get_companies(skip=skip, limit=limit)
    
    return [CompanyResponse.from_orm(company) for company in companies]


@router.get("/search/", response_model=List[CompanyResponse])
async def search_companies(
    query: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Search companies by query
    """
    company_service = CompanyService(db)
    companies = company_service.search_companies(query=query, skip=skip, limit=limit)
    
    return [CompanyResponse.from_orm(company) for company in companies]


@router.get("/by-industry/", response_model=List[CompanyResponse])
async def get_companies_by_industry(
    industry: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get companies by industry
    """
    company_service = CompanyService(db)
    companies = company_service.get_companies_by_industry(
        industry=industry,
        skip=skip,
        limit=limit
    )
    
    return [CompanyResponse.from_orm(company) for company in companies]


@router.get("/by-location/", response_model=List[CompanyResponse])
async def get_companies_by_location(
    city: str = Query(None),
    state: str = Query(None),
    country: str = Query(None),
    remote_friendly: bool = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get companies by location criteria
    """
    company_service = CompanyService(db)
    companies = company_service.get_companies_by_location(
        city=city,
        state=state,
        country=country,
        remote_friendly=remote_friendly,
        skip=skip,
        limit=limit
    )
    
    return [CompanyResponse.from_orm(company) for company in companies]


@router.get("/by-size/", response_model=List[CompanyResponse])
async def get_companies_by_size(
    company_size: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get companies by size
    """
    company_service = CompanyService(db)
    companies = company_service.get_companies_by_size(
        company_size=company_size,
        skip=skip,
        limit=limit
    )
    
    return [CompanyResponse.from_orm(company) for company in companies]


@router.get("/verified/", response_model=List[CompanyResponse])
async def get_verified_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get verified companies
    """
    company_service = CompanyService(db)
    companies = company_service.get_verified_companies(skip=skip, limit=limit)
    
    return [CompanyResponse.from_orm(company) for company in companies]


@router.get("/stats/count")
async def get_companies_count(db: Session = Depends(get_db)) -> Any:
    """
    Get company statistics
    """
    company_service = CompanyService(db)
    
    return {
        "total_companies": company_service.get_companies_count(),
        "verified_companies": company_service.get_verified_companies_count()
    }


@router.get("/industries/list")
async def get_industries_list(db: Session = Depends(get_db)) -> Any:
    """
    Get list of all industries
    """
    # TODO: Implement this endpoint to return unique industries
    # For now, return a static list
    return [
        "Technology",
        "Healthcare",
        "Finance",
        "Education",
        "Manufacturing",
        "Retail",
        "Consulting",
        "Media",
        "Transportation",
        "Energy",
        "Real Estate",
        "Non-profit",
        "Government",
        "Other"
    ]


@router.get("/sizes/list")
async def get_company_sizes_list() -> Any:
    """
    Get list of company size options
    """
    return [
        "1-10",
        "11-50",
        "51-200",
        "201-500",
        "501-1000",
        "1001-5000",
        "5001-10000",
        "10000+"
    ]