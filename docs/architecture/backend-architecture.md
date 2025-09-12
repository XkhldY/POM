# Backend Architecture Stories

## Backend Service Architecture

### FastAPI Application Structure

**Story:** Set up FastAPI application with modular architecture

**Structure:**
```
apps/api/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Environment configuration
│   │   └── database.py         # Database connection setup
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py           # File upload endpoints
│   │   ├── analysis.py         # Analysis endpoints
│   │   └── consultation.py     # Consultation endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_service.py     # File processing logic
│   │   ├── analysis_service.py # AI analysis orchestration
│   │   └── email_service.py    # Email handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # User SQLAlchemy model
│   │   ├── analysis.py        # Analysis SQLAlchemy model
│   │   └── consultation.py    # Consultation SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── analysis.py        # Pydantic schemas for analysis
│   │   └── consultation.py    # Pydantic schemas for consultation
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── cors.py            # CORS configuration
│   │   ├── auth.py            # Authentication middleware
│   │   └── error_handling.py  # Global error handling
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── bedrock_client.py  # AWS Bedrock integration
│   │   ├── langchain_workflows.py # LangChain orchestration
│   │   └── strand_agents.py   # Strand Agents implementation
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py      # File processing utilities
│       ├── validation.py      # Input validation helpers
│       └── logging.py         # Logging configuration
├── tests/                     # Backend tests
├── requirements.txt           # Python dependencies
└── Dockerfile                # Container configuration
```

### FastAPI Controller Template

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..services.analysis_service import AnalysisService
from ..schemas.analysis import AnalysisResponse, AnalysisCreate
from ..middleware.auth import get_current_user_optional

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/upload", response_model=dict)
async def upload_resume(
    file: UploadFile = File(...),
    session_id: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Upload resume file for analysis"""
    try:
        # Validate file type and size
        if not file.content_type in ["application/pdf", "application/msword", "text/plain"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Process upload
        result = await AnalysisService.process_upload(
            file=file,
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            db=db
        )
        
        return {"upload_id": result.id, "status": "uploaded"}
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_results(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get analysis results by ID"""
    analysis = await AnalysisService.get_analysis(analysis_id, db)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return AnalysisResponse.from_orm(analysis)
```

## Database Architecture

### SQLAlchemy Models

**Story:** Implement database models with proper relationships

```python
from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class AnalysisStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analysis = Column(DateTime)
    analysis_count = Column(Integer, default=0)
    
    # Relationships
    analyses = relationship("ResumeAnalysis", back_populates="user")
    consultation_requests = relationship("ConsultationRequest", back_populates="user")

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    s3_key = Column(String(512), nullable=False)
    extracted_text = Column(Text)
    analysis_results = Column(JSON)
    overall_score = Column(Integer)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PROCESSING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    consultation_requests = relationship("ConsultationRequest", back_populates="analysis")

class ConsultationRequest(Base):
    __tablename__ = "consultation_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False)
    help_category = Column(String(50), nullable=False)
    details = Column(Text, nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("resume_analyses.id"))
    status = Column(String(20), default="pending")
    priority = Column(String(10), default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    contacted_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    analysis = relationship("ResumeAnalysis", back_populates="consultation_requests")
```

### Repository Pattern Implementation

**Story:** Implement repository pattern for data access

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.analysis import ResumeAnalysis, AnalysisStatus

class AnalysisRepository(ABC):
    @abstractmethod
    async def create(self, analysis_data: dict) -> ResumeAnalysis:
        pass
    
    @abstractmethod
    async def get_by_id(self, analysis_id: str) -> Optional[ResumeAnalysis]:
        pass
    
    @abstractmethod
    async def update_status(self, analysis_id: str, status: AnalysisStatus) -> bool:
        pass

class SQLAnalysisRepository(AnalysisRepository):
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, analysis_data: dict) -> ResumeAnalysis:
        analysis = ResumeAnalysis(**analysis_data)
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    async def get_by_id(self, analysis_id: str) -> Optional[ResumeAnalysis]:
        return self.db.query(ResumeAnalysis).filter(
            ResumeAnalysis.id == analysis_id
        ).first()
    
    async def update_status(self, analysis_id: str, status: AnalysisStatus) -> bool:
        result = self.db.query(ResumeAnalysis).filter(
            ResumeAnalysis.id == analysis_id
        ).update({"status": status, "updated_at": datetime.utcnow()})
        
        self.db.commit()
        return result > 0
    
    async def get_recent_analyses(self, limit: int = 10) -> List[ResumeAnalysis]:
        return self.db.query(ResumeAnalysis).order_by(
            desc(ResumeAnalysis.created_at)
        ).limit(limit).all()
```

## AI Service Integration

### AWS Bedrock Integration

**Story:** Implement AWS Bedrock client for AI analysis

```python
import boto3
import json
from typing import Dict, Any
from botocore.exceptions import ClientError

from ..config.settings import get_settings

settings = get_settings()

class BedrockClient:
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume using AWS Bedrock"""
        
        prompt = self._build_analysis_prompt(resume_text)
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            result = json.loads(response['body'].read())
            return self._parse_analysis_response(result['content'][0]['text'])
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Bedrock analysis: {str(e)}")
            raise
    
    def _build_analysis_prompt(self, resume_text: str) -> str:
        return f"""
        Analyze the following resume for a tech professional and provide detailed feedback:

        RESUME TEXT:
        {resume_text}

        Please provide analysis in the following JSON format:
        {{
            "overall_score": <score 0-100>,
            "ats_compatibility": {{
                "score": <score 0-100>,
                "issues": ["issue1", "issue2"],
                "recommendations": ["rec1", "rec2"]
            }},
            "keyword_optimization": {{
                "score": <score 0-100>,
                "missing_keywords": ["keyword1", "keyword2"],
                "suggestions": ["suggestion1", "suggestion2"]
            }},
            "structure_analysis": {{
                "score": <score 0-100>,
                "strengths": ["strength1", "strength2"],
                "improvements": ["improvement1", "improvement2"]
            }},
            "suggestions": [
                {{
                    "category": "formatting|content|keywords|structure",
                    "priority": "high|medium|low",
                    "description": "specific suggestion",
                    "example": "concrete example"
                }}
            ]
        }}
        
        Focus on:
        1. ATS (Applicant Tracking System) compatibility
        2. Tech industry keyword optimization
        3. Structure and formatting for tech roles
        4. Specific, actionable improvements
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate the AI response"""
        try:
            # Extract JSON from response text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            # Return default structure if parsing fails
            return {
                "overall_score": 0,
                "error": "Failed to parse AI response",
                "suggestions": []
            }
```

### LangChain Workflow Integration

**Story:** Implement LangChain for AI workflow orchestration

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import Bedrock
from langchain.schema import BaseOutputParser
from typing import Dict, Any

class ResumeAnalysisChain:
    def __init__(self):
        self.bedrock_llm = Bedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name=settings.AWS_REGION
        )
        
        self.analysis_prompt = PromptTemplate(
            input_variables=["resume_text", "job_type"],
            template="""
            You are an expert resume analyst specializing in {job_type} positions.
            
            Analyze this resume and provide specific, actionable feedback:
            
            RESUME:
            {resume_text}
            
            Provide analysis covering:
            1. ATS compatibility issues and fixes
            2. Missing keywords for {job_type} roles
            3. Structure and formatting improvements
            4. Content enhancement suggestions
            
            Format your response as structured JSON with scores and specific recommendations.
            """
        )
        
        self.analysis_chain = LLMChain(
            llm=self.bedrock_llm,
            prompt=self.analysis_prompt,
            output_parser=ResumeAnalysisOutputParser()
        )
    
    async def analyze(self, resume_text: str, job_type: str = "technology") -> Dict[str, Any]:
        """Run the analysis chain"""
        try:
            result = await self.analysis_chain.arun(
                resume_text=resume_text,
                job_type=job_type
            )
            return result
        except Exception as e:
            logger.error(f"LangChain analysis failed: {str(e)}")
            raise

class ResumeAnalysisOutputParser(BaseOutputParser):
    """Custom parser for resume analysis results"""
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse the LLM output into structured format"""
        try:
            # Extract and parse JSON from the response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                
                # Validate required fields
                required_fields = ['overall_score', 'suggestions']
                for field in required_fields:
                    if field not in parsed:
                        parsed[field] = self._get_default_value(field)
                
                return parsed
            else:
                return self._get_default_response()
                
        except Exception as e:
            logger.error(f"Failed to parse analysis output: {str(e)}")
            return self._get_default_response()
    
    def _get_default_value(self, field: str) -> Any:
        defaults = {
            'overall_score': 0,
            'suggestions': [],
            'ats_compatibility': {'score': 0, 'issues': [], 'recommendations': []},
            'keyword_optimization': {'score': 0, 'missing_keywords': [], 'suggestions': []},
            'structure_analysis': {'score': 0, 'strengths': [], 'improvements': []}
        }
        return defaults.get(field, None)
    
    def _get_default_response(self) -> Dict[str, Any]:
        return {
            'overall_score': 0,
            'error': 'Analysis parsing failed',
            'suggestions': [],
            'ats_compatibility': {'score': 0, 'issues': [], 'recommendations': []},
            'keyword_optimization': {'score': 0, 'missing_keywords': [], 'suggestions': []},
            'structure_analysis': {'score': 0, 'strengths': [], 'improvements': []}
        }
```

### Strand Agents Implementation

**Story:** Implement Strand Agents for autonomous AI decisions

```python
from strand import Agent, Task, Workflow
from typing import Dict, Any, List
import asyncio

class ResumeAnalysisAgent(Agent):
    """Autonomous agent for resume analysis decisions"""
    
    def __init__(self, bedrock_client: BedrockClient):
        super().__init__(name="resume_analyzer")
        self.bedrock_client = bedrock_client
        
    async def analyze_resume_autonomously(self, resume_text: str) -> Dict[str, Any]:
        """Make autonomous decisions about resume analysis"""
        
        # Create analysis workflow
        workflow = Workflow("resume_analysis")
        
        # Task 1: Initial analysis
        initial_analysis_task = Task(
            name="initial_analysis",
            action=self._perform_initial_analysis,
            inputs={"resume_text": resume_text}
        )
        
        # Task 2: Autonomous decision making
        decision_task = Task(
            name="autonomous_decisions",
            action=self._make_autonomous_decisions,
            depends_on=[initial_analysis_task]
        )
        
        # Task 3: Generate final recommendations
        recommendations_task = Task(
            name="generate_recommendations",
            action=self._generate_final_recommendations,
            depends_on=[decision_task]
        )
        
        # Add tasks to workflow
        workflow.add_tasks([initial_analysis_task, decision_task, recommendations_task])
        
        # Execute workflow
        result = await workflow.execute()
        
        return result.get_output("generate_recommendations")
    
    async def _perform_initial_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Perform initial AI analysis"""
        return await self.bedrock_client.analyze_resume(resume_text)
    
    async def _make_autonomous_decisions(self, initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Make autonomous decisions based on initial analysis"""
        
        decisions = {
            "priority_focus": self._determine_priority_focus(initial_analysis),
            "improvement_strategy": self._determine_improvement_strategy(initial_analysis),
            "template_recommendations": self._recommend_templates(initial_analysis),
            "follow_up_actions": self._determine_follow_up_actions(initial_analysis)
        }
        
        return {**initial_analysis, "autonomous_decisions": decisions}
    
    async def _generate_final_recommendations(self, analysis_with_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final recommendations based on autonomous decisions"""
        
        decisions = analysis_with_decisions["autonomous_decisions"]
        base_analysis = {k: v for k, v in analysis_with_decisions.items() if k != "autonomous_decisions"}
        
        # Enhance suggestions based on autonomous decisions
        enhanced_suggestions = self._enhance_suggestions(
            base_analysis.get("suggestions", []),
            decisions
        )
        
        return {
            **base_analysis,
            "suggestions": enhanced_suggestions,
            "autonomous_insights": decisions,
            "confidence_score": self._calculate_confidence_score(base_analysis, decisions)
        }
    
    def _determine_priority_focus(self, analysis: Dict[str, Any]) -> str:
        """Autonomously determine what aspect needs most attention"""
        scores = {
            "ats_compatibility": analysis.get("ats_compatibility", {}).get("score", 0),
            "keyword_optimization": analysis.get("keyword_optimization", {}).get("score", 0),
            "structure_analysis": analysis.get("structure_analysis", {}).get("score", 0)
        }
        
        return min(scores, key=scores.get)  # Focus on lowest scoring area
    
    def _determine_improvement_strategy(self, analysis: Dict[str, Any]) -> str:
        """Determine the best improvement strategy"""
        overall_score = analysis.get("overall_score", 0)
        
        if overall_score < 40:
            return "comprehensive_rewrite"
        elif overall_score < 70:
            return "targeted_improvements"
        else:
            return "fine_tuning"
    
    def _recommend_templates(self, analysis: Dict[str, Any]) -> List[str]:
        """Autonomously recommend resume templates"""
        ats_score = analysis.get("ats_compatibility", {}).get("score", 0)
        
        if ats_score < 50:
            return ["ats_optimized_simple", "ats_optimized_modern"]
        else:
            return ["professional_modern", "creative_tech"]
    
    def _determine_follow_up_actions(self, analysis: Dict[str, Any]) -> List[str]:
        """Determine what follow-up actions to suggest"""
        actions = []
        
        overall_score = analysis.get("overall_score", 0)
        
        if overall_score < 60:
            actions.append("schedule_consultation")
        
        if len(analysis.get("suggestions", [])) > 5:
            actions.append("prioritize_top_3_changes")
        
        actions.append("download_improved_template")
        
        return actions
    
    def _enhance_suggestions(self, base_suggestions: List[Dict], decisions: Dict) -> List[Dict]:
        """Enhance suggestions based on autonomous decisions"""
        enhanced = []
        
        priority_focus = decisions.get("priority_focus", "")
        strategy = decisions.get("improvement_strategy", "")
        
        for suggestion in base_suggestions:
            enhanced_suggestion = suggestion.copy()
            
            # Adjust priority based on autonomous decisions
            if suggestion.get("category") == priority_focus:
                enhanced_suggestion["priority"] = "high"
                enhanced_suggestion["autonomous_reasoning"] = f"Identified as priority focus area"
            
            # Add strategy-specific guidance
            if strategy == "comprehensive_rewrite":
                enhanced_suggestion["implementation_note"] = "Consider as part of comprehensive rewrite"
            elif strategy == "targeted_improvements":
                enhanced_suggestion["implementation_note"] = "Focus on this specific improvement"
            
            enhanced.append(enhanced_suggestion)
        
        return enhanced
    
    def _calculate_confidence_score(self, analysis: Dict, decisions: Dict) -> float:
        """Calculate confidence in the autonomous analysis"""
        base_score = analysis.get("overall_score", 0)
        
        # Higher confidence for more extreme scores (very good or very bad)
        if base_score < 30 or base_score > 80:
            return 0.9
        else:
            return 0.7  # Medium confidence for middle-range scores
```

## Authentication and Authorization

### Authentication Middleware

**Story:** Implement authentication middleware for Phase 2

```python
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from typing import Optional

from ..config.settings import get_settings
from ..database import get_db
from ..models.user import User

settings = get_settings()
security = HTTPBearer(auto_error=False)

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for Phase 1)"""
    
    if not credentials:
        return None
    
    try:
        # Verify JWT token (Clerk integration)
        payload = jwt.decode(
            credentials.credentials,
            settings.CLERK_JWT_SECRET,
            algorithms=["RS256"]
        )
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Get or create user
        user = db.query(User).filter(User.clerk_id == user_id).first()
        if not user:
            # Create user from Clerk data
            user = User(
                clerk_id=user_id,
                email=payload.get("email"),
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
        
        return user
        
    except jwt.InvalidTokenError:
        return None
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        return None

async def get_current_user_required(
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Require authenticated user (for Phase 2 features)"""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user
```

## Error Handling

### Global Error Handler

**Story:** Implement comprehensive error handling

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from typing import Union
import traceback
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        super().__init__(self.message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(message, 400, "VALIDATION_ERROR")

class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404, "NOT_FOUND")

class RateLimitError(APIError):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429, "RATE_LIMIT_EXCEEDED")

def setup_error_handlers(app: FastAPI):
    """Setup global error handlers"""
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        request_id = str(uuid.uuid4())
        
        logger.error(
            f"API Error [{request_id}]: {exc.error_code} - {exc.message}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "error_code": exc.error_code,
                "status_code": exc.status_code
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        request_id = str(uuid.uuid4())
        
        logger.warning(
            f"Validation Error [{request_id}]: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "validation_errors": exc.errors()
            }
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = str(uuid.uuid4())
        
        logger.warning(
            f"HTTP Exception [{request_id}]: {exc.status_code} - {exc.detail}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = str(uuid.uuid4())
        
        logger.error(
            f"Unhandled Exception [{request_id}]: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )
```

## Service Layer Implementation

### Analysis Service

**Story:** Implement comprehensive analysis service

```python
import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from celery import Celery

from ..models.analysis import ResumeAnalysis, AnalysisStatus
from ..ai.bedrock_client import BedrockClient
from ..ai.langchain_workflows import ResumeAnalysisChain
from ..ai.strand_agents import ResumeAnalysisAgent
from ..utils.file_utils import extract_text_from_file
from ..config.settings import get_settings

settings = get_settings()

# Celery for background tasks
celery_app = Celery('resume_analysis', broker=settings.CELERY_BROKER_URL)

class AnalysisService:
    """Service for handling resume analysis workflow"""
    
    def __init__(self):
        self.bedrock_client = BedrockClient()
        self.langchain_workflow = ResumeAnalysisChain()
        self.strand_agent = ResumeAnalysisAgent(self.bedrock_client)
    
    async def process_upload(
        self,
        file,
        session_id: str,
        user_id: Optional[str],
        db: Session
    ) -> ResumeAnalysis:
        """Process file upload and initiate analysis"""
        
        # Create analysis record
        analysis = ResumeAnalysis(
            user_id=user_id,
            session_id=session_id,
            original_filename=file.filename,
            status=AnalysisStatus.PROCESSING
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Store file in S3
        s3_key = f"resumes/{analysis.id}/{file.filename}"
        await self._upload_to_s3(file, s3_key)
        
        analysis.s3_key = s3_key
        db.commit()
        
        # Start background analysis
        analyze_resume_task.delay(str(analysis.id))
        
        return analysis
    
    async def get_analysis(self, analysis_id: str, db: Session) -> Optional[ResumeAnalysis]:
        """Get analysis by ID"""
        return db.query(ResumeAnalysis).filter(
            ResumeAnalysis.id == analysis_id
        ).first()
    
    async def _upload_to_s3(self, file, s3_key: str):
        """Upload file to S3"""
        import boto3
        
        s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        file_content = await file.read()
        
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=file.content_type,
            ServerSideEncryption='AES256'
        )

@celery_app.task
def analyze_resume_task(analysis_id: str):
    """Background task for resume analysis"""
    from ..database import SessionLocal
    
    db = SessionLocal()
    
    try:
        analysis = db.query(ResumeAnalysis).filter(
            ResumeAnalysis.id == analysis_id
        ).first()
        
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found")
            return
        
        # Download file from S3 and extract text
        file_content = download_from_s3(analysis.s3_key)
        extracted_text = extract_text_from_file(file_content, analysis.original_filename)
        
        analysis.extracted_text = extracted_text
        db.commit()
        
        # Perform AI analysis using Strand Agents
        service = AnalysisService()
        analysis_results = asyncio.run(
            service.strand_agent.analyze_resume_autonomously(extracted_text)
        )
        
        # Update analysis record
        analysis.analysis_results = analysis_results
        analysis.overall_score = analysis_results.get('overall_score', 0)
        analysis.status = AnalysisStatus.COMPLETED
        
        db.commit()
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {str(e)}")
        
        # Update status to failed
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            db.commit()
    
    finally:
        db.close()

def download_from_s3(s3_key: str) -> bytes:
    """Download file from S3"""
    import boto3
    
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    response = s3_client.get_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=s3_key
    )
    
    return response['Body'].read()
```

This covers the comprehensive backend architecture stories. The backend is designed with:

1. **Modular FastAPI structure** with clear separation of concerns
2. **Repository pattern** for data access abstraction
3. **Comprehensive AI integration** with Bedrock, LangChain, and Strand Agents
4. **Robust error handling** with structured error responses
5. **Background task processing** with Celery
6. **Authentication ready** for Phase 2 with Clerk integration
7. **Comprehensive logging and monitoring**

The architecture supports the freemium model with no authentication required in Phase 1, while being ready to scale for Phase 2 premium features.
