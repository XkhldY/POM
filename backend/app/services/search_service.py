"""
Search service for implementing text-based search, filtering, and ranking
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc, func
from sqlalchemy.sql import text

from app.models.job import Job, JobStatus
from app.models.profile import Profile
from app.models.company import Company
from app.models.user import User
from app.core.config import settings


class SearchService:
    """Service class for search operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_jobs(self, query: str = None, filters: Dict[str, Any] = None, 
                   sort_by: str = "relevance", sort_order: str = "desc",
                   page: int = 1, page_size: int = None) -> Tuple[List[Job], int, Dict[str, Any]]:
        """
        Search jobs with advanced filtering and ranking
        
        Returns:
            Tuple of (jobs, total_count, metadata)
        """
        if page_size is None:
            page_size = settings.DEFAULT_PAGE_SIZE
        
        # Build base query
        base_query = self.db.query(Job).filter(Job.status == JobStatus.PUBLISHED)
        
        # Apply text search
        if query:
            search_filter = or_(
                Job.title.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%"),
                Job.city.ilike(f"%{query}%"),
                Job.state.ilike(f"%{query}%"),
                Job.country.ilike(f"%{query}%"),
                Job.industry.ilike(f"%{query}%"),
                Job.department.ilike(f"%{query}%")
            )
            base_query = base_query.filter(search_filter)
        
        # Apply filters
        if filters:
            base_query = self._apply_job_filters(base_query, filters)
        
        # Get total count before pagination
        total_count = base_query.count()
        
        # Apply sorting
        base_query = self._apply_job_sorting(base_query, sort_by, sort_order, query)
        
        # Apply pagination
        offset = (page - 1) * page_size
        jobs = base_query.offset(offset).limit(page_size).all()
        
        # Calculate metadata
        metadata = {
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
            "total_count": total_count,
            "has_next": page * page_size < total_count,
            "has_previous": page > 1
        }
        
        return jobs, total_count, metadata
    
    def search_profiles(self, query: str = None, filters: Dict[str, Any] = None,
                       sort_by: str = "relevance", sort_order: str = "desc",
                       page: int = 1, page_size: int = None) -> Tuple[List[Profile], int, Dict[str, Any]]:
        """
        Search profiles with advanced filtering and ranking
        
        Returns:
            Tuple of (profiles, total_count, metadata)
        """
        if page_size is None:
            page_size = settings.DEFAULT_PAGE_SIZE
        
        # Build base query
        base_query = self.db.query(Profile)
        
        # Apply text search
        if query:
            search_filter = or_(
                Profile.title.ilike(f"%{query}%"),
                Profile.summary.ilike(f"%{query}%"),
                Profile.city.ilike(f"%{query}%"),
                Profile.state.ilike(f"%{query}%"),
                Profile.country.ilike(f"%{query}%")
            )
            base_query = base_query.filter(search_filter)
        
        # Apply filters
        if filters:
            base_query = self._apply_profile_filters(base_query, filters)
        
        # Get total count before pagination
        total_count = base_query.count()
        
        # Apply sorting
        base_query = self._apply_profile_sorting(base_query, sort_by, sort_order, query)
        
        # Apply pagination
        offset = (page - 1) * page_size
        profiles = base_query.offset(offset).limit(page_size).all()
        
        # Calculate metadata
        metadata = {
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
            "total_count": total_count,
            "has_next": page * page_size < total_count,
            "has_previous": page > 1
        }
        
        return profiles, total_count, metadata
    
    def search_companies(self, query: str = None, filters: Dict[str, Any] = None,
                        sort_by: str = "relevance", sort_order: str = "desc",
                        page: int = 1, page_size: int = None) -> Tuple[List[Company], int, Dict[str, Any]]:
        """
        Search companies with advanced filtering and ranking
        
        Returns:
            Tuple of (companies, total_count, metadata)
        """
        if page_size is None:
            page_size = settings.DEFAULT_PAGE_SIZE
        
        # Build base query
        base_query = self.db.query(Company).filter(Company.is_active == True)
        
        # Apply text search
        if query:
            search_filter = or_(
                Company.name.ilike(f"%{query}%"),
                Company.description.ilike(f"%{query}%"),
                Company.industry.ilike(f"%{query}%"),
                Company.city.ilike(f"%{query}%"),
                Company.state.ilike(f"%{query}%"),
                Company.country.ilike(f"%{query}%")
            )
            base_query = base_query.filter(search_filter)
        
        # Apply filters
        if filters:
            base_query = self._apply_company_filters(base_query, filters)
        
        # Get total count before pagination
        total_count = base_query.count()
        
        # Apply sorting
        base_query = self._apply_company_sorting(base_query, sort_by, sort_order, query)
        
        # Apply pagination
        offset = (page - 1) * page_size
        companies = base_query.offset(offset).limit(page_size).all()
        
        # Calculate metadata
        metadata = {
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
            "total_count": total_count,
            "has_next": page * page_size < total_count,
            "has_previous": page > 1
        }
        
        return companies, total_count, metadata
    
    def global_search(self, query: str, page: int = 1, page_size: int = None) -> Dict[str, Any]:
        """
        Perform global search across all entities
        
        Returns:
            Dictionary with search results for each entity type
        """
        if page_size is None:
            page_size = settings.DEFAULT_PAGE_SIZE
        
        results = {}
        
        # Search jobs
        jobs, jobs_count, jobs_metadata = self.search_jobs(
            query=query, page=page, page_size=page_size
        )
        results["jobs"] = {
            "items": jobs,
            "count": jobs_count,
            "metadata": jobs_metadata
        }
        
        # Search profiles
        profiles, profiles_count, profiles_metadata = self.search_profiles(
            query=query, page=page, page_size=page_size
        )
        results["profiles"] = {
            "items": profiles,
            "count": profiles_count,
            "metadata": profiles_metadata
        }
        
        # Search companies
        companies, companies_count, companies_metadata = self.search_companies(
            query=query, page=page, page_size=page_size
        )
        results["companies"] = {
            "items": companies,
            "count": companies_count,
            "metadata": companies_metadata
        }
        
        # Calculate total results
        total_count = jobs_count + profiles_count + companies_count
        results["total_count"] = total_count
        results["query"] = query
        
        return results
    
    def get_search_suggestions(self, query: str, limit: int = 10) -> Dict[str, List[str]]:
        """
        Get search suggestions for autocomplete
        
        Returns:
            Dictionary with suggestions for each entity type
        """
        suggestions = {}
        
        # Job title suggestions
        job_titles = self.db.query(Job.title).filter(
            and_(
                Job.status == JobStatus.PUBLISHED,
                Job.title.ilike(f"%{query}%")
            )
        ).distinct().limit(limit).all()
        suggestions["job_titles"] = [title[0] for title in job_titles]
        
        # Company name suggestions
        company_names = self.db.query(Company.name).filter(
            and_(
                Company.is_active == True,
                Company.name.ilike(f"%{query}%")
            )
        ).distinct().limit(limit).all()
        suggestions["company_names"] = [name[0] for name in company_names]
        
        # Location suggestions
        locations = self.db.query(Job.city, Job.state, Job.country).filter(
            and_(
                Job.status == JobStatus.PUBLISHED,
                or_(
                    Job.city.ilike(f"%{query}%"),
                    Job.state.ilike(f"%{query}%"),
                    Job.country.ilike(f"%{query}%")
                )
            )
        ).distinct().limit(limit).all()
        suggestions["locations"] = [f"{city}, {state}, {country}" for city, state, country in locations if city]
        
        # Skill suggestions
        # This would be enhanced with vector search in production
        suggestions["skills"] = []
        
        return suggestions
    
    def _apply_job_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to job search query"""
        if "job_type" in filters:
            query = query.filter(Job.job_type == filters["job_type"])
        
        if "experience_level" in filters:
            query = query.filter(Job.experience_level == filters["experience_level"])
        
        if "location" in filters:
            location_filter = or_(
                Job.city.ilike(f"%{filters['location']}%"),
                Job.state.ilike(f"%{filters['location']}%"),
                Job.country.ilike(f"%{filters['location']}%")
            )
            query = query.filter(location_filter)
        
        if "remote_only" in filters:
            query = query.filter(Job.is_remote == filters["remote_only"])
        
        if "min_salary" in filters:
            query = query.filter(Job.salary_max >= filters["min_salary"])
        
        if "max_salary" in filters:
            query = query.filter(Job.salary_min <= filters["max_salary"])
        
        if "industry" in filters:
            query = query.filter(Job.industry.ilike(f"%{filters['industry']}%"))
        
        return query
    
    def _apply_profile_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to profile search query"""
        if "min_experience" in filters:
            query = query.filter(Profile.years_of_experience >= filters["min_experience"])
        
        if "max_experience" in filters:
            query = query.filter(Profile.years_of_experience <= filters["max_experience"])
        
        if "location" in filters:
            location_filter = or_(
                Profile.city.ilike(f"%{filters['location']}%"),
                Profile.state.ilike(f"%{filters['location']}%"),
                Profile.country.ilike(f"%{filters['location']}%")
            )
            query = query.filter(location_filter)
        
        if "remote_available" in filters:
            query = query.filter(Profile.is_remote_available == filters["remote_available"])
        
        if "min_salary" in filters:
            query = query.filter(Profile.salary_expectation_min >= filters["min_salary"])
        
        if "max_salary" in filters:
            query = query.filter(Profile.salary_expectation_max <= filters["max_salary"])
        
        return query
    
    def _apply_company_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to company search query"""
        if "industry" in filters:
            query = query.filter(Company.industry.ilike(f"%{filters['industry']}%"))
        
        if "company_size" in filters:
            query = query.filter(Company.company_size == filters["company_size"])
        
        if "location" in filters:
            location_filter = or_(
                Company.city.ilike(f"%{filters['location']}%"),
                Company.state.ilike(f"%{filters['location']}%"),
                Company.country.ilike(f"%{filters['location']}%")
            )
            query = query.filter(location_filter)
        
        if "remote_friendly" in filters:
            query = query.filter(Company.is_remote_friendly == filters["remote_friendly"])
        
        if "verified_only" in filters and filters["verified_only"]:
            query = query.filter(Company.is_verified == True)
        
        return query
    
    def _apply_job_sorting(self, query, sort_by: str, sort_order: str, search_query: str = None):
        """Apply sorting to job search query"""
        if sort_by == "relevance" and search_query:
            # Simple relevance scoring based on title match
            query = query.add_columns(
                func.case(
                    (Job.title.ilike(f"%{search_query}%"), 3),
                    (Job.title.ilike(f"{search_query}%"), 2),
                    (Job.title.ilike(f"%{search_query}"), 2),
                    else_=1
                ).label("relevance_score")
            ).order_by(desc("relevance_score"), desc(Job.created_at))
        elif sort_by == "date":
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Job.created_at))
            else:
                query = query.order_by(asc(Job.created_at))
        elif sort_by == "salary":
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Job.salary_max))
            else:
                query = query.order_by(asc(Job.salary_min))
        elif sort_by == "views":
            query = query.order_by(desc(Job.views_count))
        else:
            # Default sorting
            query = query.order_by(desc(Job.created_at))
        
        return query
    
    def _apply_profile_sorting(self, query, sort_by: str, sort_order: str, search_query: str = None):
        """Apply sorting to profile search query"""
        if sort_by == "relevance" and search_query:
            # Simple relevance scoring
            query = query.add_columns(
                func.case(
                    (Profile.title.ilike(f"%{search_query}%"), 3),
                    (Profile.title.ilike(f"{search_query}%"), 2),
                    (Profile.title.ilike(f"%{search_query}"), 2),
                    else_=1
                ).label("relevance_score")
            ).order_by(desc("relevance_score"), desc(Profile.created_at))
        elif sort_by == "date":
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Profile.created_at))
            else:
                query = query.order_by(asc(Profile.created_at))
        elif sort_by == "experience":
            query = query.order_by(desc(Profile.years_of_experience))
        elif sort_by == "score":
            query = query.order_by(desc(Profile.profile_score))
        else:
            # Default sorting
            query = query.order_by(desc(Profile.created_at))
        
        return query
    
    def _apply_company_sorting(self, query, sort_by: str, sort_order: str, search_query: str = None):
        """Apply sorting to company search query"""
        if sort_by == "relevance" and search_query:
            # Simple relevance scoring
            query = query.add_columns(
                func.case(
                    (Company.name.ilike(f"%{search_query}%"), 3),
                    (Company.name.ilike(f"{search_query}%"), 2),
                    (Company.name.ilike(f"%{search_query}"), 2),
                    else_=1
                ).label("relevance_score")
            ).order_by(desc("relevance_score"), desc(Company.created_at))
        elif sort_by == "date":
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Company.created_at))
            else:
                query = query.order_by(asc(Company.created_at))
        elif sort_by == "name":
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Company.name))
            else:
                query = query.order_by(asc(Company.name))
        else:
            # Default sorting
            query = query.order_by(desc(Company.created_at))
        
        return query