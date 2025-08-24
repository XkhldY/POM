"""
AI endpoints for AI-powered features
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.ai_service import AIService
from app.services.profile_service import ProfileService
from app.services.job_service import JobService
from app.schemas.ai import AIAnalysisRequest, AIAnalysisResponse

router = APIRouter()


@router.post("/analyze-resume", response_model=Dict[str, Any])
async def analyze_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analyze resume using AI to extract structured information
    """
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, DOC, DOCX, and TXT files are allowed."
        )
    
    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 10MB."
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Convert to text (simplified - in production, use proper text extraction)
        if file.filename.lower().endswith('.txt'):
            resume_text = content.decode('utf-8')
        else:
            # For PDF/DOC files, this would use proper text extraction libraries
            # For now, return an error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text extraction for PDF/DOC files not yet implemented. Please upload a TXT file."
            )
        
        # Initialize AI service
        ai_service = AIService()
        
        # Analyze resume
        analysis_result = await ai_service.analyze_resume(resume_text)
        
        # Update user profile with AI analysis results
        profile_service = ProfileService(db)
        profile = profile_service.get_profile_by_user_id(current_user.id)
        
        if profile:
            profile_service.update_ai_analysis(profile.id, analysis_result)
        
        return {
            "message": "Resume analysis completed successfully",
            "analysis": analysis_result,
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume analysis failed: {str(e)}"
        )


@router.post("/analyze-job", response_model=Dict[str, Any])
async def analyze_job_posting(
    job_text: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analyze job posting using AI to extract structured information
    """
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Analyze job posting
        analysis_result = await ai_service.analyze_job_posting(job_text)
        
        return {
            "message": "Job posting analysis completed successfully",
            "analysis": analysis_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job posting analysis failed: {str(e)}"
        )


@router.post("/extract-skills", response_model=Dict[str, Any])
async def extract_skills(
    text_content: str = Form(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Extract skills from text content using AI
    """
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Extract skills
        skills_result = await ai_service.extract_skills(text_content)
        
        return {
            "message": "Skills extraction completed successfully",
            "skills": skills_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Skills extraction failed: {str(e)}"
        )


@router.post("/match-candidate-job", response_model=Dict[str, Any])
async def match_candidate_job(
    candidate_profile: str = Form(...),
    job_requirements: str = Form(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Analyze the match between a candidate and job using AI
    """
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Analyze match
        match_result = await ai_service.analyze_candidate_job_match(
            candidate_profile, job_requirements
        )
        
        return {
            "message": "Candidate-job matching analysis completed successfully",
            "match_analysis": match_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Candidate-job matching analysis failed: {str(e)}"
        )


@router.post("/generate-cover-letter", response_model=Dict[str, Any])
async def generate_cover_letter(
    job_title: str = Form(...),
    company_name: str = Form(...),
    job_description: str = Form(...),
    candidate_profile: str = Form(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate a cover letter using AI
    """
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Generate cover letter
        cover_letter = await ai_service.generate_cover_letter(
            job_title, company_name, job_description, candidate_profile
        )
        
        return {
            "message": "Cover letter generated successfully",
            "cover_letter": cover_letter
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cover letter generation failed: {str(e)}"
        )


@router.post("/generate-interview-prep", response_model=Dict[str, Any])
async def generate_interview_preparation(
    job_title: str = Form(...),
    company_name: str = Form(...),
    job_description: str = Form(...),
    candidate_profile: str = Form(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate interview preparation guidance using AI
    """
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Generate interview preparation
        interview_prep = await ai_service.generate_interview_preparation(
            job_title, company_name, job_description, candidate_profile
        )
        
        return {
            "message": "Interview preparation guidance generated successfully",
            "interview_preparation": interview_prep
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interview preparation generation failed: {str(e)}"
        )


@router.post("/analyze-profile/{profile_id}", response_model=Dict[str, Any])
async def analyze_profile(
    profile_id: int,
    analysis_type: str = Form(..., regex="^(skills|experience|overall)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analyze a specific profile using AI
    """
    try:
        profile_service = ProfileService(db)
        profile = profile_service.get_profile_by_id(profile_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Check if user can analyze this profile
        if profile.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to analyze this profile"
            )
        
        # Initialize AI service
        ai_service = AIService()
        
        # Prepare profile data for analysis
        profile_data = {
            "title": profile.title or "",
            "summary": profile.summary or "",
            "skills": profile.skills or [],
            "experience": profile.experience or [],
            "education": profile.education or []
        }
        
        profile_text = f"""
        Title: {profile_data['title']}
        Summary: {profile_data['summary']}
        Skills: {profile_data['skills']}
        Experience: {profile_data['experience']}
        Education: {profile_data['education']}
        """
        
        # Perform analysis based on type
        if analysis_type == "skills":
            analysis_result = await ai_service.extract_skills(profile_text)
        elif analysis_type == "experience":
            # For experience analysis, we could use a specific prompt
            analysis_result = await ai_service.extract_skills(profile_text)
        else:  # overall
            analysis_result = await ai_service.analyze_resume(profile_text)
        
        # Update profile with AI analysis results
        profile_service.update_ai_analysis(profile.id, analysis_result)
        
        return {
            "message": f"Profile {analysis_type} analysis completed successfully",
            "analysis_type": analysis_type,
            "analysis_result": analysis_result,
            "profile_id": profile_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile analysis failed: {str(e)}"
        )


@router.post("/analyze-job/{job_id}", response_model=Dict[str, Any])
async def analyze_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analyze a specific job posting using AI
    """
    try:
        job_service = JobService(db)
        job = job_service.get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if user can analyze this job
        if job.employer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to analyze this job"
            )
        
        # Initialize AI service
        ai_service = AIService()
        
        # Prepare job data for analysis
        job_text = f"""
        Title: {job.title}
        Description: {job.description}
        Requirements: {job.skills_required or []}
        Preferred Skills: {job.skills_preferred or []}
        Experience Level: {job.experience_level or 'Not specified'}
        """
        
        # Analyze job posting
        analysis_result = await ai_service.analyze_job_posting(job_text)
        
        # Update job with AI analysis results
        job_service.update_ai_analysis(job.id, analysis_result)
        
        return {
            "message": "Job analysis completed successfully",
            "analysis_result": analysis_result,
            "job_id": job_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job analysis failed: {str(e)}"
        )


@router.get("/status")
async def get_ai_service_status() -> Any:
    """
    Get AI service status and configuration
    """
    try:
        ai_service = AIService()
        status_info = ai_service.get_ai_service_status()
        
        return {
            "message": "AI service status retrieved successfully",
            "status": status_info
        }
        
    except Exception as e:
        return {
            "message": "AI service status check failed",
            "error": str(e),
            "status": {
                "service": "Unknown",
                "model": "Unknown",
                "api_key_configured": False,
                "status": "error",
                "timestamp": "Unknown"
            }
        }


@router.get("/recommendations/jobs/{profile_id}")
async def get_ai_job_recommendations(
    profile_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get AI-powered job recommendations for a profile
    """
    try:
        profile_service = ProfileService(db)
        profile = profile_service.get_profile_by_id(profile_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Check if user can access this profile
        if profile.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this profile"
            )
        
        # Get recent jobs for matching
        job_service = JobService(db)
        recent_jobs = job_service.get_recent_jobs(limit=50)
        
        # TODO: Implement proper AI matching algorithm
        # For now, return a simple recommendation based on profile skills
        recommendations = []
        
        if profile.skills:
            profile_skills = [skill.get("name", "").lower() for skill in profile.skills]
            
            for job in recent_jobs:
                if job.skills_required:
                    job_skills = [skill.get("name", "").lower() for skill in job.skills_required]
                    # Calculate simple skill match
                    matching_skills = set(profile_skills) & set(job_skills)
                    match_score = len(matching_skills) / max(len(profile_skills), 1) * 100
                    
                    if match_score > 20:  # Only recommend if there's some skill overlap
                        recommendations.append({
                            "job": job.__dict__,
                            "match_score": round(match_score, 2),
                            "matching_skills": list(matching_skills)
                        })
        
        # Sort by match score and limit results
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        recommendations = recommendations[:limit]
        
        return {
            "message": "Job recommendations generated successfully",
            "profile_id": profile_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate job recommendations: {str(e)}"
        )


@router.get("/recommendations/candidates/{job_id}")
async def get_ai_candidate_recommendations(
    job_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get AI-powered candidate recommendations for a job
    """
    try:
        job_service = JobService(db)
        job = job_service.get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if user can access this job
        if job.employer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this job"
            )
        
        # Get complete profiles for matching
        profile_service = ProfileService(db)
        complete_profiles = profile_service.get_complete_profiles(limit=100)
        
        # TODO: Implement proper AI matching algorithm
        # For now, return a simple recommendation based on job requirements
        recommendations = []
        
        if job.skills_required:
            job_skills = [skill.get("name", "").lower() for skill in job.skills_required]
            
            for profile in complete_profiles:
                if profile.skills:
                    profile_skills = [skill.get("name", "").lower() for skill in profile.skills]
                    # Calculate simple skill match
                    matching_skills = set(profile_skills) & set(job_skills)
                    match_score = len(matching_skills) / max(len(job_skills), 1) * 100
                    
                    if match_score > 20:  # Only recommend if there's some skill overlap
                        recommendations.append({
                            "profile": profile.__dict__,
                            "match_score": round(match_score, 2),
                            "matching_skills": list(matching_skills)
                        })
        
        # Sort by match score and limit results
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        recommendations = recommendations[:limit]
        
        return {
            "message": "Candidate recommendations generated successfully",
            "job_id": job_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate candidate recommendations: {str(e)}"
        )