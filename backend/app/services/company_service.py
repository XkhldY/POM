"""
Company service for company management operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.company import Company
from app.core.exceptions import NotFoundError, ValidationError


class CompanyService:
    """Service class for company operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def get_company_by_slug(self, slug: str) -> Optional[Company]:
        """Get company by slug"""
        return self.db.query(Company).filter(Company.slug == slug).first()
    
    def get_companies(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get list of companies with pagination"""
        return self.db.query(Company).filter(Company.is_active == True).offset(skip).limit(limit).all()
    
    def create_company(self, **kwargs) -> Company:
        """Create a new company"""
        # Generate slug from name
        if "name" in kwargs and not kwargs.get("slug"):
            kwargs["slug"] = self._generate_slug(kwargs["name"])
        
        db_company = Company(**kwargs)
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        
        return db_company
    
    def update_company(self, company_id: int, **kwargs) -> Optional[Company]:
        """Update company information"""
        company = self.get_company_by_id(company_id)
        if not company:
            raise NotFoundError("Company", company_id)
        
        # Update fields
        for field, value in kwargs.items():
            if hasattr(company, field):
                setattr(company, field, value)
        
        # Regenerate slug if name changed
        if "name" in kwargs:
            company.slug = self._generate_slug(company.name)
        
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def delete_company(self, company_id: int) -> bool:
        """Delete a company (soft delete by setting is_active to False)"""
        company = self.get_company_by_id(company_id)
        if not company:
            return False
        
        company.is_active = False
        self.db.commit()
        return True
    
    def verify_company(self, company_id: int) -> Optional[Company]:
        """Verify a company"""
        company = self.get_company_by_id(company_id)
        if not company:
            raise NotFoundError("Company", company_id)
        
        company.is_verified = True
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def search_companies(self, query: str, skip: int = 0, limit: int = 100) -> List[Company]:
        """Search companies by name, industry, or location"""
        search_filter = or_(
            Company.name.ilike(f"%{query}%"),
            Company.industry.ilike(f"%{query}%"),
            Company.city.ilike(f"%{query}%"),
            Company.state.ilike(f"%{query}%"),
            Company.country.ilike(f"%{query}%")
        )
        
        return self.db.query(Company).filter(
            and_(Company.is_active == True, search_filter)
        ).offset(skip).limit(limit).all()
    
    def get_companies_by_industry(self, industry: str, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get companies by industry"""
        return self.db.query(Company).filter(
            and_(Company.is_active == True, Company.industry.ilike(f"%{industry}%"))
        ).offset(skip).limit(limit).all()
    
    def get_companies_by_location(self, city: str = None, state: str = None, country: str = None,
                                remote_friendly: bool = None, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get companies by location criteria"""
        filters = [Company.is_active == True]
        
        if city:
            filters.append(Company.city.ilike(f"%{city}%"))
        if state:
            filters.append(Company.state.ilike(f"%{state}%"))
        if country:
            filters.append(Company.country.ilike(f"%{country}%"))
        if remote_friendly is not None:
            filters.append(Company.is_remote_friendly == remote_friendly)
        
        return self.db.query(Company).filter(and_(*filters)).offset(skip).limit(limit).all()
    
    def get_companies_by_size(self, company_size: str, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get companies by size"""
        return self.db.query(Company).filter(
            and_(Company.is_active == True, Company.company_size == company_size)
        ).offset(skip).limit(limit).all()
    
    def get_verified_companies(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get verified companies"""
        return self.db.query(Company).filter(
            and_(Company.is_active == True, Company.is_verified == True)
        ).offset(skip).limit(limit).all()
    
    def get_companies_count(self) -> int:
        """Get total count of active companies"""
        return self.db.query(Company).filter(Company.is_active == True).count()
    
    def get_verified_companies_count(self) -> int:
        """Get count of verified companies"""
        return self.db.query(Company).filter(
            and_(Company.is_active == True, Company.is_verified == True)
        ).count()
    
    def _generate_slug(self, name: str) -> str:
        """Generate a URL-friendly slug from company name"""
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while self.get_company_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug