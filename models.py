"""
models.py
All Pydantic models - Requests and Responses
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any


# ============================================================================
# REQUEST MODELS (What clients send)
# ============================================================================

class LoginRequest(BaseModel):
    username: EmailStr = Field(..., example="john@company.com")
    password: str = Field(..., min_length=8, example="SecurePass123!")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, example="How does authentication work?")
    session_id: Optional[str] = Field(default="default")
    project_id: Optional[str] = None


class UploadMetadata(BaseModel):
    project_id: str = Field(default="default")
    domain: str = Field(default="general")
    tags: List[str] = Field(default_factory=list)
    description: str = Field(default="")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    project_id: Optional[str] = None
    domain: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


# ============================================================================
# RESPONSE MODELS (What API sends back)
# ============================================================================

class LoginResponse(BaseModel):
    success: bool
    access_token: str
    refresh_token: str
    user_id: str
    email: str
    expires_in: int


class UserResponse(BaseModel):
    user_id: str
    email: str
    verified: bool = True


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent: str
    delegated_to: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    timestamp: str


class UploadResponse(BaseModel):
    success: bool
    message: str
    resource_id: str
    file_name: str
    file_size: int
    s3_key: Optional[str] = None
    processing_time: float


class SearchResult(BaseModel):
    text: str
    file_name: str
    score: float
    resource_id: str


class SearchResponse(BaseModel):
    success: bool
    query: str
    results: List[SearchResult]
    total_results: int
    response: str
    timestamp: str


class DocumentMetadata(BaseModel):
    resource_id: str
    user_id: str
    file_name: str
    file_type: str
    file_size: int
    s3_key: str
    project_id: str
    domain: str
    tags: List[str]
    uploaded_at: str
    status: str


class DocumentListResponse(BaseModel):
    success: bool
    documents: List[DocumentMetadata]
    total: int


class HealthResponse(BaseModel):
    status: str
    version: str
    mode: str
    agents: Dict[str, str]
    services: Dict[str, str]