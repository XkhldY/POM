from fastapi import FastAPI

app = FastAPI(
    title="POM API",
    description="API for the POM resume analysis application.",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to the POM API"}

# Placeholder for API routers
# from .api.v1 import some_router
# app.include_router(some_router, prefix="/api/v1")
