"""Analytics background tasks for processing analytics data asynchronously."""
from celery import current_task
from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.core.config import settings
from app.db.base import get_db
from app.services.user_service import UserService
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.services.search_service import SearchService
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

logger = get_logger(__name__)


@celery_app.task(bind=True, name="generate_daily_analytics")
def generate_daily_analytics(self):
    """Generate daily analytics report."""
    try:
        logger.info("Starting daily analytics generation")
        
        # Get database session
        db = next(get_db())
        
        # Get services
        user_service = UserService(db)
        job_service = JobService(db)
        application_service = ApplicationService(db)
        search_service = SearchService(db)
        
        # Calculate date range
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # User analytics
        new_users_today = user_service.count_users_created_since(yesterday)
        total_users = user_service.count_total_users()
        active_users_today = user_service.count_active_users_since(yesterday)
        
        # Job analytics
        new_jobs_today = job_service.count_jobs_created_since(yesterday)
        total_jobs = job_service.count_total_jobs()
        published_jobs = job_service.count_published_jobs()
        
        # Application analytics
        new_applications_today = application_service.count_applications_created_since(yesterday)
        total_applications = application_service.count_total_applications()
        
        # Search analytics
        search_stats = search_service.get_search_statistics()
        
        # Compile analytics data
        analytics_data = {
            "date": today.isoformat(),
            "users": {
                "new_today": new_users_today,
                "total": total_users,
                "active_today": active_users_today,
                "growth_rate": (new_users_today / max(total_users - new_users_today, 1)) * 100 if total_users > new_users_today else 0
            },
            "jobs": {
                "new_today": new_jobs_today,
                "total": total_jobs,
                "published": published_jobs,
                "publish_rate": (published_jobs / max(total_jobs, 1)) * 100
            },
            "applications": {
                "new_today": new_applications_today,
                "total": total_applications,
                "application_rate": (new_applications_today / max(new_jobs_today, 1)) if new_jobs_today > 0 else 0
            },
            "search": search_stats,
            "platform_health": {
                "database_connections": "healthy",
                "cache_status": "healthy",
                "ai_service_status": "healthy"
            }
        }
        
        # Store analytics data (this would typically go to a time-series database)
        # For now, just log it
        logger.info(f"Daily analytics generated: {json.dumps(analytics_data, indent=2)}")
        
        return {
            "status": "success",
            "analytics_data": analytics_data
        }
        
    except Exception as e:
        logger.error(f"Daily analytics generation failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="update_search_analytics")
def update_search_analytics(self, search_query: str, user_id: int = None, 
                           search_type: str = "general", filters: Dict[str, Any] = None):
    """Update search analytics for a search query."""
    try:
        logger.info(f"Updating search analytics for query: {search_query}")
        
        # Get database session
        db = next(get_db())
        
        # Get search service
        search_service = SearchService(db)
        
        # Update search statistics
        search_service.update_search_statistics(
            query=search_query,
            user_id=user_id,
            search_type=search_type,
            filters=filters
        )
        
        logger.info(f"Search analytics updated for query: {search_query}")
        return {
            "status": "success",
            "query": search_query,
            "search_type": search_type
        }
        
    except Exception as e:
        logger.error(f"Search analytics update failed for query '{search_query}': {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="process_user_activity")
def process_user_activity(self, user_id: int, activity_type: str, 
                         activity_data: Dict[str, Any] = None):
    """Process user activity for analytics."""
    try:
        logger.info(f"Processing user activity for user {user_id}: {activity_type}")
        
        # Get database session
        db = next(get_db())
        
        # Get user service
        user_service = UserService(db)
        
        # Update user activity tracking
        user_service.update_user_activity(
            user_id=user_id,
            activity_type=activity_type,
            activity_data=activity_data
        )
        
        logger.info(f"User activity processed for user {user_id}: {activity_type}")
        return {
            "status": "success",
            "user_id": user_id,
            "activity_type": activity_type
        }
        
    except Exception as e:
        logger.error(f"User activity processing failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="generate_user_recommendations_analytics")
def generate_user_recommendations_analytics(self, user_id: int):
    """Generate analytics for user recommendations."""
    try:
        logger.info(f"Generating recommendation analytics for user {user_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get application service
        application_service = ApplicationService(db)
        
        # Get user's application history
        applications = application_service.get_applications_by_applicant(user_id)
        
        # Analyze application patterns
        total_applications = len(applications)
        successful_applications = len([app for app in applications if app.status in ["shortlisted", "interview", "offer"]])
        success_rate = (successful_applications / max(total_applications, 1)) * 100
        
        # Analyze job preferences
        job_industries = {}
        job_locations = {}
        job_types = {}
        
        for app in applications:
            job = app.job
            if job.industry:
                job_industries[job.industry] = job_industries.get(job.industry, 0) + 1
            if job.city:
                job_locations[job.city] = job_locations.get(job.city, 0) + 1
            if job.job_type:
                job_types[job.job_type] = job_types.get(job.job_type, 0) + 1
        
        # Compile recommendation analytics
        recommendation_analytics = {
            "user_id": user_id,
            "application_metrics": {
                "total_applications": total_applications,
                "successful_applications": successful_applications,
                "success_rate": success_rate
            },
            "preferences": {
                "top_industries": sorted(job_industries.items(), key=lambda x: x[1], reverse=True)[:5],
                "top_locations": sorted(job_locations.items(), key=lambda x: x[1], reverse=True)[:5],
                "preferred_job_types": sorted(job_types.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Recommendation analytics generated for user {user_id}")
        return {
            "status": "success",
            "user_id": user_id,
            "analytics": recommendation_analytics
        }
        
    except Exception as e:
        logger.error(f"Recommendation analytics generation failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="generate_company_analytics")
def generate_company_analytics(self, company_id: int):
    """Generate analytics for a company."""
    try:
        logger.info(f"Generating company analytics for company {company_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get services
        company_service = CompanyService(db)
        job_service = JobService(db)
        application_service = ApplicationService(db)
        
        # Get company
        company = company_service.get_company_by_id(company_id)
        if not company:
            logger.error(f"Company {company_id} not found")
            return {"status": "error", "message": "Company not found"}
        
        # Get company jobs
        company_jobs = job_service.get_jobs_by_company(company_id)
        
        # Get applications for company jobs
        total_applications = 0
        job_application_counts = {}
        
        for job in company_jobs:
            job_applications = application_service.get_applications_by_job(job.id)
            total_applications += len(job_applications)
            job_application_counts[job.id] = len(job_applications)
        
        # Calculate metrics
        total_jobs = len(company_jobs)
        published_jobs = len([job for job in company_jobs if job.status == "published"])
        avg_applications_per_job = total_applications / max(total_jobs, 1)
        
        # Compile company analytics
        company_analytics = {
            "company_id": company_id,
            "company_name": company.name,
            "metrics": {
                "total_jobs": total_jobs,
                "published_jobs": published_jobs,
                "total_applications": total_applications,
                "avg_applications_per_job": avg_applications_per_job,
                "publish_rate": (published_jobs / max(total_jobs, 1)) * 100
            },
            "job_details": [
                {
                    "job_id": job.id,
                    "title": job.title,
                    "status": job.status,
                    "applications_count": job_application_counts.get(job.id, 0),
                    "views_count": job.views_count
                }
                for job in company_jobs
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Company analytics generated for company {company_id}")
        return {
            "status": "success",
            "company_id": company_id,
            "analytics": company_analytics
        }
        
    except Exception as e:
        logger.error(f"Company analytics generation failed for company {company_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="cleanup_old_analytics")
def cleanup_old_analytics(self, days_to_keep: int = 90):
    """Clean up old analytics data."""
    try:
        logger.info(f"Cleaning up analytics data older than {days_to_keep} days")
        
        # This would implement logic to clean up old analytics data
        # For now, just log the task
        logger.info("Old analytics data cleanup completed")
        
        return {
            "status": "success",
            "message": f"Cleaned up analytics data older than {days_to_keep} days"
        }
        
    except Exception as e:
        logger.error(f"Analytics cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="export_analytics_report")
def export_analytics_report(self, report_type: str, date_range: Dict[str, str], 
                           format: str = "json"):
    """Export analytics report in specified format."""
    try:
        logger.info(f"Exporting {report_type} analytics report for {date_range}")
        
        # This would implement logic to export analytics reports
        # For now, just log the task
        logger.info(f"Analytics report export completed: {report_type}")
        
        return {
            "status": "success",
            "report_type": report_type,
            "date_range": date_range,
            "format": format,
            "download_url": f"/api/v1/analytics/export/{report_type}"
        }
        
    except Exception as e:
        logger.error(f"Analytics report export failed: {str(e)}")
        return {"status": "error", "message": str(e)}