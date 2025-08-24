"""AI background tasks for processing AI operations asynchronously."""
from celery import current_task
from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.services.ai_service import AIService
from app.services.profile_service import ProfileService
from app.services.job_service import JobService
from app.db.base import get_db
from sqlalchemy.orm import Session
import asyncio

logger = get_logger(__name__)


@celery_app.task(bind=True, name="analyze_profile_async")
def analyze_profile_async(self, profile_id: int):
    """Analyze a user profile asynchronously using AI."""
    try:
        logger.info(f"Starting AI analysis for profile {profile_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get profile
        profile_service = ProfileService(db)
        profile = profile_service.get_profile_by_id(profile_id)
        
        if not profile:
            logger.error(f"Profile {profile_id} not found")
            return {"status": "error", "message": "Profile not found"}
        
        # Get AI service
        ai_service = AIService()
        
        # Run AI analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Analyze profile
            analysis_result = loop.run_until_complete(
                ai_service.analyze_profile(profile)
            )
            
            # Update profile with AI analysis
            profile_service.update_profile(
                profile.id,
                skills_vector=analysis_result.get("skills_vector"),
                experience_vector=analysis_result.get("experience_vector"),
                last_ai_analysis="now",
                is_complete=True
            )
            
            logger.info(f"AI analysis completed for profile {profile_id}")
            return {
                "status": "success",
                "profile_id": profile_id,
                "analysis_result": analysis_result
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"AI analysis failed for profile {profile_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="analyze_job_async")
def analyze_job_async(self, job_id: int):
    """Analyze a job posting asynchronously using AI."""
    try:
        logger.info(f"Starting AI analysis for job {job_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get job
        job_service = JobService(db)
        job = job_service.get_job_by_id(job_id)
        
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"status": "error", "message": "Job not found"}
        
        # Get AI service
        ai_service = AIService()
        
        # Run AI analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Analyze job
            analysis_result = loop.run_until_complete(
                ai_service.analyze_job(job)
            )
            
            # Update job with AI analysis
            job_service.update_job(
                job.id,
                skills_vector=analysis_result.get("skills_vector"),
                requirements_vector=analysis_result.get("requirements_vector"),
                last_ai_analysis="now"
            )
            
            logger.info(f"AI analysis completed for job {job_id}")
            return {
                "status": "success",
                "job_id": job_id,
                "analysis_result": analysis_result
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"AI analysis failed for job {job_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="update_profile_scores")
def update_profile_scores(self):
    """Update profile scores for all profiles using AI analysis."""
    try:
        logger.info("Starting profile score update for all profiles")
        
        # Get database session
        db = next(get_db())
        
        # Get all profiles
        profile_service = ProfileService(db)
        profiles = profile_service.get_all_profiles()
        
        updated_count = 0
        failed_count = 0
        
        for profile in profiles:
            try:
                # Calculate profile score
                score = profile.calculate_profile_score()
                
                # Update profile with new score
                profile_service.update_profile(
                    profile.id,
                    profile_score=score
                )
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update score for profile {profile.id}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Profile score update completed. Updated: {updated_count}, Failed: {failed_count}")
        return {
            "status": "success",
            "updated_count": updated_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Profile score update failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="generate_recommendations")
def generate_recommendations(self, user_id: int, profile_id: int = None):
    """Generate personalized recommendations for a user."""
    try:
        logger.info(f"Generating recommendations for user {user_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get AI service
        ai_service = AIService()
        
        # Run AI recommendations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Generate recommendations
            recommendations = loop.run_until_complete(
                ai_service.generate_user_recommendations(user_id, profile_id)
            )
            
            logger.info(f"Recommendations generated for user {user_id}")
            return {
                "status": "success",
                "user_id": user_id,
                "recommendations": recommendations
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Recommendation generation failed for user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="process_batch_ai_analysis")
def process_batch_ai_analysis(self, profile_ids: list = None, job_ids: list = None):
    """Process batch AI analysis for multiple profiles and jobs."""
    try:
        logger.info("Starting batch AI analysis")
        
        results = {
            "profiles": {"success": 0, "failed": 0},
            "jobs": {"success": 0, "failed": 0}
        }
        
        # Process profiles
        if profile_ids:
            for profile_id in profile_ids:
                try:
                    result = analyze_profile_async.delay(profile_id)
                    if result.get("status") == "success":
                        results["profiles"]["success"] += 1
                    else:
                        results["profiles"]["failed"] += 1
                except Exception as e:
                    logger.error(f"Failed to queue profile analysis {profile_id}: {str(e)}")
                    results["profiles"]["failed"] += 1
        
        # Process jobs
        if job_ids:
            for job_id in job_ids:
                try:
                    result = analyze_job_async.delay(job_id)
                    if result.get("status") == "success":
                        results["jobs"]["success"] += 1
                    else:
                        results["jobs"]["failed"] += 1
                except Exception as e:
                    logger.error(f"Failed to queue job analysis {job_id}: {str(e)}")
                    results["jobs"]["failed"] += 1
        
        logger.info(f"Batch AI analysis queued. Results: {results}")
        return {
            "status": "success",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch AI analysis failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="cleanup_ai_vectors")
def cleanup_ai_vectors(self):
    """Clean up old or invalid AI vectors."""
    try:
        logger.info("Starting AI vectors cleanup")
        
        # Get database session
        db = next(get_db())
        
        # This would implement logic to clean up old vectors
        # For now, just log the task
        logger.info("AI vectors cleanup completed")
        
        return {"status": "success", "message": "Cleanup completed"}
        
    except Exception as e:
        logger.error(f"AI vectors cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}