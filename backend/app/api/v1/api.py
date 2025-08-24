"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, profiles, jobs, companies, applications, search, ai

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])