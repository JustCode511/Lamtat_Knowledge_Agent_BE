"""
config.py
Central configuration - ONE place to control everything

Toggle mock/real with one variable: USE_MOCK = True/False
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # ============================================================================
    # MAIN TOGGLE - Change this to switch mock/real
    # ============================================================================
    USE_MOCK: bool = True  # True = Mock (no AWS), False = Real AWS
    
    # Application
    APP_NAME: str = "Knowledge Agent"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    # AWS Configuration (used when USE_MOCK = False)
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "knowledge-agent-documents"
    DYNAMODB_TABLE_NAME: str = "knowledge-metadata"
    COGNITO_USER_POOL_ID: str = "us-east-1_XXXXXXXXX"
    COGNITO_CLIENT_ID: str = "your-client-id"
    OPENSEARCH_ENDPOINT: str = "your-opensearch-endpoint"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-use-secrets-manager"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf", ".txt", ".md", ".doc", ".docx",
        ".ppt", ".pptx", ".png", ".jpg", ".jpeg",
        ".py", ".js", ".java", ".cpp", ".go"
    ]
    
    # Text Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Mock Users (for testing when USE_MOCK = True)
    MOCK_USERS: dict = {
        "john@company.com": {
            "password": "SecurePass123!",
            "user_id": "user-123",
            "name": "John Doe"
        },
        "jane@company.com": {
            "password": "SecurePass123!",
            "user_id": "user-456",
            "name": "Jane Smith"
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export for easy import
settings = get_settings()


# Print current mode on import
if settings.USE_MOCK:
    print("🧪 Running in MOCK mode (no AWS required)")
else:
    print("☁️  Running in REAL AWS mode")