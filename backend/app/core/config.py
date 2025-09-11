import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "POM API"
    DATABASE_URL: str = "postgresql://user:password@localhost/db"
    S3_BUCKET_NAME: str = "pom-resumes"
    # Add other settings here

    class Config:
        env_file = ".env"

settings = Settings()
