"""
Job service for job management operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from datetime import datetime

from app.models.job import Job, JobStatus, JobType, ExperienceLevel
from app.core.exceptions import NotFoundError, ValidationError


class JobService:
    """Service class for job operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        """Get job by ID"""
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def get_job_by_slug(self, slug: str) -> Optional[Job]:
        """Get job by slug"""
        return self.db.query(Job).filter(Job.slug == slug).first()
    
    def get_jobs(self, skip: int = 0, limit: int = 100, status: JobStatus = None) -> List[Job]:
        """Get list of jobs with pagination and optional status filter"""
        query = self.db.query(Job)
        
        if status:
            query = query.filter(Job.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_jobs_by_employer(self, employer_id: int, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by employer ID"""
        return self.db.query(Job).filter(Job.employer_id == employer_id).offset(skip).limit(limit).all()
    
    def get_jobs_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by company ID"""
        return self.db.query(Job).filter(Job.company_id == company_id).offset(skip).limit(limit).all()
    
    def create_job(self, **kwargs) -> Job:
        """Create a new job"""
        # Generate slug from title
        if "title" in kwargs and not kwargs.get("slug"):
            kwargs["slug"] = self._generate_slug(kwargs["title"])
        
        db_job = Job(**kwargs)
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        
        return db_job
    
    def update_job(self, job_id: int, **kwargs) -> Optional[Job]:
        """Update job information"""
        job = self.get_job_by_id(job_id)
        if not job:
            raise NotFoundError("Job", job_id)
        
        # Update fields
        for field, value in kwargs.items():
            if hasattr(job, field):
                setattr(job, field, value)
        
        # Regenerate slug if title changed
        if "title" in kwargs:
            job.slug = self._generate_slug(job.title)
        
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def delete_job(self, job_id: int) -> bool:
        """Delete a job (soft delete by setting status to archived)"""
        job = self.get_job_by_id(job_id)
        if not job:
            return False
        
        job.status = JobStatus.ARCHIVED
        self.db.commit()
        return True
    
    def publish_job(self, job_id: int) -> Optional[Job]:
        """Publish a job (change status to published)"""
        job = self.get_job_by_id(job_id)
        if not job:
            raise NotFoundError("Job", job_id)
        
        if job.status != JobStatus.DRAFT:
            raise ValidationError("Only draft jobs can be published")
        
        job.status = JobStatus.PUBLISHED
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def close_job(self, job_id: int) -> Optional[Job]:
        """Close a job (change status to closed)"""
        job = self.get_job_by_id(job_id)
        if not job:
            raise NotFoundError("Job", job_id)
        
        job.status = JobStatus.CLOSED
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def search_jobs(self, query: str = None, job_type: JobType = None, 
                   experience_level: ExperienceLevel = None, location: str = None,
                   remote_only: bool = None, min_salary: int = None, max_salary: int = None,
                   skills: List[str] = None, industry: str = None,
                   skip: int = 0, limit: int = 100, sort_by: str = "created_at", 
                   sort_order: str = "desc") -> List[Job]:
        """Search jobs with multiple filters"""
        query_builder = self.db.query(Job).filter(Job.status == JobStatus.PUBLISHED)
        
        # Text search
        if query:
            search_filter = or_(
                Job.title.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%"),
                Job.city.ilike(f"%{query}%"),
                Job.state.ilike(f"%{query}%"),
                Job.country.ilike(f"%{query}%")
            )
            query_builder = query_builder.filter(search_filter)
        
        # Job type filter
        if job_type:
            query_builder = query_builder.filter(Job.job_type == job_type)
        
        # Experience level filter
        if experience_level:
            query_builder = query_builder.filter(Job.experience_level == experience_level)
        
        # Location filter
        if location:
            location_filter = or_(
                Job.city.ilike(f"%{location}%"),
                Job.state.ilike(f"%{location}%"),
                Job.country.ilike(f"%{location}%")
            )
            query_builder = query_builder.filter(location_filter)
        
        # Remote filter
        if remote_only is not None:
            query_builder = query_builder.filter(Job.is_remote == remote_only)
        
        # Salary filters
        if min_salary:
            query_builder = query_builder.filter(Job.salary_max >= min_salary)
        if max_salary:
            query_builder = query_builder.filter(Job.salary_min <= max_salary)
        
        # Industry filter
        if industry:
            query_builder = query_builder.filter(Job.industry.ilike(f"%{industry}%"))
        
        # Skills filter (simplified - in production use vector similarity)
        if skills:
            # This is a basic implementation - would be enhanced with vector search
            pass
        
        # Sorting
        if hasattr(Job, sort_by):
            sort_column = getattr(Job, sort_by)
            if sort_order.lower() == "desc":
                query_builder = query_builder.order_by(desc(sort_column))
            else:
                query_builder = query_builder.order_by(asc(sort_column))
        else:
            # Default sorting by creation date
            query_builder = query_builder.order_by(desc(Job.created_at))
        
        return query_builder.offset(skip).limit(limit).all()
    
    def get_featured_jobs(self, limit: int = 10) -> List[Job]:
        """Get featured jobs (high view count, recent, etc.)"""
        return self.db.query(Job).filter(
            Job.status == JobStatus.PUBLISHED
        ).order_by(
            desc(Job.views_count),
            desc(Job.created_at)
        ).limit(limit).all()
    
    def get_recent_jobs(self, limit: int = 20) -> List[Job]:
        """Get most recent published jobs"""
        return self.db.query(Job).filter(
            Job.status == JobStatus.PUBLISHED
        ).order_by(desc(Job.created_at)).limit(limit).all()
    
    def increment_job_views(self, job_id: int) -> bool:
        """Increment job view count"""
        job = self.get_job_by_id(job_id)
        if not job:
            return False
        
        job.increment_views()
        self.db.commit()
        return True
    
    def increment_job_applications(self, job_id: int) -> bool:
        """Increment job application count"""
        job = self.get_job_by_id(job_id)
        if not job:
            return False
        
        job.increment_applications()
        self.db.commit()
        return True
    
    def update_ai_analysis(self, job_id: int, ai_data: Dict[str, Any]) -> Optional[Job]:
        """Update job with AI analysis results"""
        job = self.get_job_by_id(job_id)
        if not job:
            raise NotFoundError("Job", job_id)
        
        # Update AI-generated fields
        if "skills_vector" in ai_data:
            job.skills_vector = ai_data["skills_vector"]
        if "requirements_vector" in ai_data:
            job.requirements_vector = ai_data["requirements_vector"]
        
        job.last_ai_analysis = "now"  # Should be actual timestamp
        
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def get_jobs_count(self, status: JobStatus = None) -> int:
        """Get total count of jobs with optional status filter"""
        query = self.db.query(Job)
        if status:
            query = query.filter(Job.status == status)
        return query.count()
    
    def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get all jobs with a specific status"""
        return self.db.query(Job).filter(Job.status == status).all()
    
    def _generate_slug(self, title: str) -> str:
        """Generate a URL-friendly slug from job title"""
        import re
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while self.get_job_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug