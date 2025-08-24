"""
AI service for integrating Google Gemini AI API
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

import google.generativeai as genai
from app.core.config import settings
from app.core.exceptions import AIProcessingError, ExternalServiceError

logger = logging.getLogger(__name__)


class AIService:
    """Service class for AI operations using Google Gemini"""
    
    def __init__(self):
        """Initialize AI service with Gemini configuration"""
        if not settings.GEMINI_API_KEY:
            raise AIProcessingError("Gemini API key not configured")
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Initialize collections for different types of content
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup AI prompts for different tasks"""
        self.prompts = {
            "resume_analysis": """
            Analyze the following resume and extract key information in JSON format:
            
            Please provide:
            1. Skills (list with proficiency levels: beginner, intermediate, advanced, expert)
            2. Work experience (list with company, role, duration, key achievements)
            3. Education (list with degree, institution, year, GPA if available)
            4. Summary (professional summary in 2-3 sentences)
            5. Years of experience (total years)
            6. Key achievements (list of notable accomplishments)
            7. Languages (list with proficiency levels)
            
            Resume content:
            {resume_text}
            
            Return only valid JSON without markdown formatting.
            """,
            
            "job_analysis": """
            Analyze the following job posting and extract key information in JSON format:
            
            Please provide:
            1. Required skills (list with importance levels: required, preferred, nice-to-have)
            2. Experience requirements (minimum and maximum years)
            3. Job level (entry, junior, mid, senior, lead, executive)
            4. Key responsibilities (list of main duties)
            5. Required qualifications (list of must-have qualifications)
            6. Preferred qualifications (list of nice-to-have qualifications)
            7. Industry classification
            8. Job complexity score (1-10)
            
            Job posting:
            {job_text}
            
            Return only valid JSON without markdown formatting.
            """,
            
            "skills_extraction": """
            Extract technical and soft skills from the following text:
            
            Please identify:
            1. Technical skills (programming languages, tools, technologies)
            2. Soft skills (communication, leadership, problem-solving)
            3. Domain expertise (industry-specific knowledge)
            4. Certifications (if mentioned)
            
            Text content:
            {text_content}
            
            Return only valid JSON without markdown formatting.
            """,
            
            "matching_analysis": """
            Analyze the match between a candidate profile and job requirements:
            
            Candidate Profile:
            {candidate_profile}
            
            Job Requirements:
            {job_requirements}
            
            Please provide:
            1. Overall match score (0-100)
            2. Skills match percentage
            3. Experience match percentage
            4. Key strengths (what makes this a good match)
            5. Areas for improvement (what could be better)
            6. Specific skill gaps
            7. Recommendations for the candidate
            8. Risk factors (if any)
            
            Return only valid JSON without markdown formatting.
            """,
            
            "cover_letter_generation": """
            Generate a professional cover letter based on:
            
            Job Title: {job_title}
            Company: {company_name}
            Job Description: {job_description}
            
            Candidate Profile:
            {candidate_profile}
            
            Please create:
            1. A compelling opening paragraph
            2. 2-3 body paragraphs highlighting relevant experience
            3. A strong closing paragraph
            4. Professional tone and formatting
            
            Return only the cover letter text without markdown formatting.
            """,
            
            "interview_preparation": """
            Generate interview preparation guidance for:
            
            Job Title: {job_title}
            Company: {company_name}
            Job Description: {job_description}
            
            Candidate Profile:
            {candidate_profile}
            
            Please provide:
            1. Key talking points for the candidate
            2. Potential interview questions
            3. Questions the candidate should ask
            4. Areas to emphasize
            5. Potential challenges and how to address them
            6. Company research suggestions
            
            Return only valid JSON without markdown formatting.
            """
        }
    
    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyze resume using AI to extract structured information
        
        Args:
            resume_text: Raw resume text content
            
        Returns:
            Dictionary with extracted resume information
        """
        try:
            prompt = self.prompts["resume_analysis"].format(resume_text=resume_text)
            
            response = await self._generate_ai_response(prompt)
            result = self._parse_ai_response(response)
            
            # Validate and structure the result
            structured_result = self._structure_resume_analysis(result)
            
            logger.info("Resume analysis completed successfully")
            return structured_result
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {str(e)}")
            raise AIProcessingError(f"Failed to analyze resume: {str(e)}")
    
    async def analyze_job_posting(self, job_text: str) -> Dict[str, Any]:
        """
        Analyze job posting using AI to extract structured information
        
        Args:
            job_text: Raw job posting text content
            
        Returns:
            Dictionary with extracted job information
        """
        try:
            prompt = self.prompts["job_analysis"].format(job_text=job_text)
            
            response = await self._generate_ai_response(prompt)
            result = self._parse_ai_response(response)
            
            # Validate and structure the result
            structured_result = self._structure_job_analysis(result)
            
            logger.info("Job posting analysis completed successfully")
            return structured_result
            
        except Exception as e:
            logger.error(f"Job posting analysis failed: {str(e)}")
            raise AIProcessingError(f"Failed to analyze job posting: {str(e)}")
    
    async def extract_skills(self, text_content: str) -> Dict[str, Any]:
        """
        Extract skills from text content using AI
        
        Args:
            text_content: Text content to analyze
            
        Returns:
            Dictionary with extracted skills
        """
        try:
            prompt = self.prompts["skills_extraction"].format(text_content=text_content)
            
            response = await self._generate_ai_response(prompt)
            result = self._parse_ai_response(response)
            
            logger.info("Skills extraction completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Skills extraction failed: {str(e)}")
            raise AIProcessingError(f"Failed to extract skills: {str(e)}")
    
    async def analyze_candidate_job_match(self, candidate_profile: str, job_requirements: str) -> Dict[str, Any]:
        """
        Analyze the match between a candidate and job using AI
        
        Args:
            candidate_profile: Candidate profile information
            job_requirements: Job requirements information
            
        Returns:
            Dictionary with matching analysis results
        """
        try:
            prompt = self.prompts["matching_analysis"].format(
                candidate_profile=candidate_profile,
                job_requirements=job_requirements
            )
            
            response = await self._generate_ai_response(prompt)
            result = self._parse_ai_response(response)
            
            # Validate and structure the result
            structured_result = self._structure_matching_analysis(result)
            
            logger.info("Candidate-job matching analysis completed successfully")
            return structured_result
            
        except Exception as e:
            logger.error(f"Candidate-job matching analysis failed: {str(e)}")
            raise AIProcessingError(f"Failed to analyze candidate-job match: {str(e)}")
    
    async def generate_cover_letter(self, job_title: str, company_name: str, 
                                  job_description: str, candidate_profile: str) -> str:
        """
        Generate a cover letter using AI
        
        Args:
            job_title: Job title
            company_name: Company name
            job_description: Job description
            candidate_profile: Candidate profile information
            
        Returns:
            Generated cover letter text
        """
        try:
            prompt = self.prompts["cover_letter_generation"].format(
                job_title=job_title,
                company_name=company_name,
                job_description=job_description,
                candidate_profile=candidate_profile
            )
            
            response = await self._generate_ai_response(prompt)
            
            logger.info("Cover letter generation completed successfully")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Cover letter generation failed: {str(e)}")
            raise AIProcessingError(f"Failed to generate cover letter: {str(e)}")
    
    async def generate_interview_preparation(self, job_title: str, company_name: str,
                                          job_description: str, candidate_profile: str) -> Dict[str, Any]:
        """
        Generate interview preparation guidance using AI
        
        Args:
            job_title: Job title
            company_name: Company name
            job_description: Job description
            candidate_profile: Candidate profile information
            
        Returns:
            Dictionary with interview preparation guidance
        """
        try:
            prompt = self.prompts["interview_preparation"].format(
                job_title=job_title,
                company_name=company_name,
                job_description=job_description,
                candidate_profile=candidate_profile
            )
            
            response = await self._generate_ai_response(prompt)
            result = self._parse_ai_response(response)
            
            logger.info("Interview preparation guidance generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Interview preparation generation failed: {str(e)}")
            raise AIProcessingError(f"Failed to generate interview preparation: {str(e)}")
    
    async def _generate_ai_response(self, prompt: str) -> str:
        """Generate AI response using Gemini"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            raise ExternalServiceError("Gemini AI", f"API call failed: {str(e)}")
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON content"""
        try:
            # Clean the response and extract JSON
            cleaned_response = response.strip()
            
            # Try to find JSON content
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3]  # Remove ```json and ```
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3]  # Remove ``` and ```
            
            # Parse JSON
            result = json.loads(cleaned_response)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.error(f"Raw response: {response}")
            raise AIProcessingError("Failed to parse AI response as JSON")
    
    def _structure_resume_analysis(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Structure and validate resume analysis results"""
        structured = {
            "skills": raw_result.get("skills", []),
            "work_experience": raw_result.get("work_experience", []),
            "education": raw_result.get("education", []),
            "summary": raw_result.get("summary", ""),
            "years_of_experience": raw_result.get("years_of_experience", 0),
            "key_achievements": raw_result.get("key_achievements", []),
            "languages": raw_result.get("languages", []),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence_score": raw_result.get("confidence_score", 0.8)
        }
        
        return structured
    
    def _structure_job_analysis(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Structure and validate job analysis results"""
        structured = {
            "required_skills": raw_result.get("required_skills", []),
            "experience_requirements": raw_result.get("experience_requirements", {}),
            "job_level": raw_result.get("job_level", "mid"),
            "key_responsibilities": raw_result.get("key_responsibilities", []),
            "required_qualifications": raw_result.get("required_qualifications", []),
            "preferred_qualifications": raw_result.get("preferred_qualifications", []),
            "industry_classification": raw_result.get("industry_classification", ""),
            "job_complexity_score": raw_result.get("job_complexity_score", 5),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence_score": raw_result.get("confidence_score", 0.8)
        }
        
        return structured
    
    def _structure_matching_analysis(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Structure and validate matching analysis results"""
        structured = {
            "overall_match_score": raw_result.get("overall_match_score", 0),
            "skills_match_percentage": raw_result.get("skills_match_percentage", 0),
            "experience_match_percentage": raw_result.get("experience_match_percentage", 0),
            "key_strengths": raw_result.get("key_strengths", []),
            "areas_for_improvement": raw_result.get("areas_for_improvement", []),
            "specific_skill_gaps": raw_result.get("specific_skill_gaps", []),
            "recommendations": raw_result.get("recommendations", []),
            "risk_factors": raw_result.get("risk_factors", []),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence_score": raw_result.get("confidence_score", 0.8)
        }
        
        return structured
    
    def get_ai_service_status(self) -> Dict[str, Any]:
        """Get AI service status and configuration"""
        return {
            "service": "Gemini AI",
            "model": settings.GEMINI_MODEL,
            "api_key_configured": bool(settings.GEMINI_API_KEY),
            "status": "operational" if settings.GEMINI_API_KEY else "not_configured",
            "timestamp": datetime.utcnow().isoformat()
        }