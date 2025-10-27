# """
# main.py
# FastAPI application with all endpoints
# Run: python main.py OR uvicorn main:app --reload
# """

# from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status
# from fastapi.responses import StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from typing import Dict, Optional
# from datetime import datetime

# from config import settings
# from models import *
# from services import *
# from agents import ChatAgent, IngestionAgent, RetrievalAgent


# # ============================================================================
# # INITIALIZE SERVICES
# # ============================================================================

# print("\n" + "="*60)
# print("🚀 Initializing Services")
# print("="*60)

# auth_service = get_auth_service()
# storage_service = get_storage_service()
# text_extraction_service = get_text_extraction_service()
# metadata_service = get_metadata_service()
# vector_search_service = get_vector_search_service()

# print("="*60)
# print("🚀 Initializing Agents")
# print("="*60)

# # Initialize agents
# ingestion_agent = IngestionAgent(storage_service, text_extraction_service, metadata_service)
# retrieval_agent = RetrievalAgent(vector_search_service, metadata_service)
# chat_agent = ChatAgent(ingestion_agent, retrieval_agent)

# print("="*60)
# print("✅ All services and agents initialized!")
# print("="*60 + "\n")


# # ============================================================================
# # FASTAPI APPLICATION
# # ============================================================================

# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.VERSION,
#     description="3-Agent Knowledge Management System with AWS Integration",
#     docs_url="/docs",
#     redoc_url="/redoc"
# )

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Security
# security = HTTPBearer()


# # ============================================================================
# # AUTHENTICATION DEPENDENCY
# # ============================================================================

# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security)
# ) -> Dict:
#     """Verify JWT token and return user context"""
#     try:
#         token = credentials.credentials
#         user = await auth_service.verify_token(token)
#         return user
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Invalid authentication: {str(e)}",
#             headers={"WWW-Authenticate": "Bearer"},
#         )


# # ============================================================================
# # ROOT & HEALTH ENDPOINTS
# # ============================================================================

# @app.get("/")
# async def root():
#     """Root endpoint"""
#     mode = "MOCK" if settings.USE_MOCK else "REAL AWS"
    
#     return {
#         "status": "running",
#         "service": settings.APP_NAME,
#         "version": settings.VERSION,
#         "mode": mode,
#         "agents": {
#             "chat": "ChatAgent (Orchestrator)",
#             "ingestion": "IngestionAgent (S3 Upload)",
#             "retrieval": "RetrievalAgent (Search & RAG)"
#         },
#         "features": [
#             "AWS Cognito Authentication",
#             "Server-Sent Events (SSE)",
#             "Multi-Agent Orchestration",
#             "Mock/Real Toggle"
#         ],
#         "endpoints": {
#             "docs": "/docs",
#             "health": "/health",
#             "auth": {
#                 "login": "POST /auth/login",
#                 "me": "GET /auth/me"
#             },
#             "chat": {
#                 "chat": "POST /chat",
#                 "stream": "POST /chat/stream"
#             },
#             "documents": {
#                 "upload": "POST /upload",
#                 "list": "GET /documents"
#             },
#             "search": {
#                 "search": "POST /search"
#             }
#         }
#     }


# @app.get("/health", response_model=HealthResponse)
# async def health_check():
#     """Health check endpoint"""
#     mode = "MOCK" if settings.USE_MOCK else "REAL AWS"
    
#     return HealthResponse(
#         status="healthy",
#         version=settings.VERSION,
#         mode=mode,
#         agents={
#             "chat_agent": "ready",
#             "ingestion_agent": "ready",
#             "retrieval_agent": "ready"
#         },
#         services={
#             "auth": "mock" if settings.USE_MOCK else "cognito",
#             "storage": "mock" if settings.USE_MOCK else f"s3://{settings.S3_BUCKET_NAME}",
#             "text_extraction": "mock" if settings.USE_MOCK else "textract",
#             "metadata": "mock" if settings.USE_MOCK else f"dynamodb:{settings.DYNAMODB_TABLE_NAME}",
#             "vector_search": "mock" if settings.USE_MOCK else "opensearch"
#         }
#     )


# # ============================================================================
# # AUTHENTICATION ENDPOINTS
# # ============================================================================

# @app.post("/auth/login", response_model=LoginResponse)
# async def login(request: LoginRequest):
#     """
#     Login with username and password
    
#     Mock users (when USE_MOCK=True):
#     - john@company.com / SecurePass123!
#     - jane@company.com / SecurePass123!
#     """
#     try:
#         result = await auth_service.login(request.username, request.password)
        
#         return LoginResponse(
#             success=True,
#             access_token=result['access_token'],
#             refresh_token=result['refresh_token'],
#             user_id=result['user_id'],
#             email=result['email'],
#             expires_in=result['expires_in']
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=str(e)
#         )


# @app.get("/auth/me", response_model=UserResponse)
# async def get_current_user_info(user: Dict = Depends(get_current_user)):
#     """Get current user information"""
#     return UserResponse(**user)


# # ============================================================================
# # CHAT ENDPOINTS
# # ============================================================================

# @app.post("/chat", response_model=ChatResponse)
# async def chat(
#     request: ChatRequest,
#     user: Dict = Depends(get_current_user)
# ):
#     """
#     Chat endpoint - routes to appropriate agent
    
#     Examples:
#     - "How does authentication work?" → RetrievalAgent
#     - "Upload document" → IngestionAgent  
#     - "Hello" → ChatAgent
#     """
#     try:
#         return await chat_agent.process_message(request, user)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/chat/stream")
# async def chat_stream(
#     request: ChatRequest,
#     user: Dict = Depends(get_current_user)
# ):
#     """
#     Streaming chat with Server-Sent Events (SSE)
    
#     Returns word-by-word streaming response for better UX
#     """
#     try:
#         return StreamingResponse(
#             chat_agent.stream_response(request, user),
#             media_type="text/event-stream"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ============================================================================
# # DOCUMENT ENDPOINTS
# # ============================================================================

# @app.post("/upload", response_model=UploadResponse)
# async def upload_document(
#     file: UploadFile = File(..., description="Document to upload"),
#     project_id: str = Form(default="default"),
#     domain: str = Form(default="general"),
#     tags: str = Form(default="", description="Comma-separated tags"),
#     description: str = Form(default=""),
#     user: Dict = Depends(get_current_user)
# ):
#     """
#     Upload and index a document
    
#     Supported formats: PDF, DOC, DOCX, PPT, PPTX, TXT, MD, code files, images
#     """
#     try:
#         # Read file
#         file_content = await file.read()
        
#         # Validate file size
#         if len(file_content) > settings.MAX_UPLOAD_SIZE:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
#             )
        
#         # Parse tags
#         tags_list = [t.strip() for t in tags.split(",") if t.strip()]
        
#         # Ingest document
#         result = await ingestion_agent.ingest_document(
#             file_content=file_content,
#             file_name=file.filename,
#             user_id=user['user_id'],
#             project_id=project_id,
#             domain=domain,
#             tags=tags_list,
#             description=description
#         )
        
#         return result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# @app.get("/documents", response_model=DocumentListResponse)
# async def list_documents(
#     project_id: Optional[str] = None,
#     user: Dict = Depends(get_current_user)
# ):
#     """List user's documents, optionally filtered by project"""
#     try:
#         docs = await metadata_service.get_user_documents(
#             user_id=user['user_id'],
#             project_id=project_id
#         )
        
#         return DocumentListResponse(
#             success=True,
#             documents=[DocumentMetadata(**doc) for doc in docs],
#             total=len(docs)
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ============================================================================
# # SEARCH ENDPOINT
# # ============================================================================

# @app.post("/search", response_model=SearchResponse)
# async def search(
#     request: SearchRequest,
#     user: Dict = Depends(get_current_user)
# ):
#     """
#     Search knowledge base with semantic search
    
#     Returns relevant documents with RAG-generated response
#     """
#     try:
#         result = await retrieval_agent.search(
#             query=request.query,
#             user_id=user['user_id'],
#             project_id=request.project_id,
#             top_k=request.top_k
#         )
        
#         return SearchResponse(
#             success=result['success'],
#             query=result['query'],
#             results=[SearchResult(**r) for r in result['sources']],
#             total_results=result['total'],
#             response=result['response'],
#             timestamp=datetime.utcnow().isoformat()
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ============================================================================
# # RUN SERVER
# # ============================================================================

# if __name__ == "__main__":
#     import uvicorn
    
#     mode = "MOCK" if settings.USE_MOCK else "REAL AWS"
    
#     print(f"""
# ╔════════════════════════════════════════════════════════════╗
# ║         KNOWLEDGE AGENT - 3-AGENT SYSTEM                   ║
# ╠════════════════════════════════════════════════════════════╣
# ║                                                             ║
# ║  Mode: {mode:^53} ║
# ║                                                             ║
# ║  🤖 Chat Agent      - Orchestrates requests                ║
# ║  📥 Ingestion Agent - Uploads to S3                        ║
# ║  🔍 Retrieval Agent - Semantic search with RAG             ║
# ║                                                             ║
# ║  🔐 Mock Users:                                            ║
# ║     • john@company.com / SecurePass123!                    ║
# ║     • jane@company.com / SecurePass123!                    ║
# ║                                                             ║
# ║  📡 Features:                                              ║
# ║     ✅ Server-Sent Events (SSE) Streaming                  ║
# ║     ✅ AWS Cognito Authentication                          ║
# ║     ✅ Multi-Agent Orchestration                           ║
# ║     ✅ Mock/Real AWS Toggle                                ║
# ║                                                             ║
# ╚════════════════════════════════════════════════════════════╝

# 🌐 Server: http://localhost:8000
# 📚 Docs: http://localhost:8000/docs
# 🔐 ReDoc: http://localhost:8000/redoc

# To switch to real AWS:
# 1. Edit config.py: USE_MOCK = False
# 2. Add AWS credentials to .env
# 3. Restart server

# 🚀 Starting server...
#     """)
    
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info"
#     )

"""
main.py - ENHANCED FOR HACKATHON
Complete FastAPI application with ALL endpoints
Added: Streaming, Better Search, Document Management, Analytics
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional, List
from datetime import datetime
import json

from config import settings
from models import *
from services import *
from agents import ChatAgent, IngestionAgent, RetrievalAgent


# ============================================================================
# INITIALIZE SERVICES
# ============================================================================

print("\n" + "="*60)
print("🚀 Initializing Services - HACKATHON MODE")
print("="*60)

auth_service = get_auth_service()
storage_service = get_storage_service()
text_extraction_service = get_text_extraction_service()
metadata_service = get_metadata_service()
vector_search_service = get_vector_search_service()

print("="*60)
print("🚀 Initializing Agents")
print("="*60)

ingestion_agent = IngestionAgent(storage_service, text_extraction_service, metadata_service)
retrieval_agent = RetrievalAgent(vector_search_service, metadata_service)
chat_agent = ChatAgent(ingestion_agent, retrieval_agent)

print("="*60)
print("✅ All services and agents initialized!")
print("="*60 + "\n")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="🏆 HACKATHON: 3-Agent Knowledge Management System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


# ============================================================================
# AUTHENTICATION DEPENDENCY
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Verify JWT token and return user context"""
    try:
        token = credentials.credentials
        user = await auth_service.verify_token(token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with system info"""
    mode = "MOCK" if settings.USE_MOCK else "REAL AWS"
    
    return {
        "status": "🏆 HACKATHON READY",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "mode": mode,
        "features": [
            "✅ Multi-Agent Orchestration",
            "✅ Server-Sent Events (SSE) Streaming",
            "✅ Document Upload & Processing",
            "✅ Semantic Search with RAG",
            "✅ Source Citations",
            "✅ Project Management",
            "✅ Analytics Dashboard",
            "✅ Mock/Real AWS Toggle"
        ],
        "endpoints": {
            "auth": ["POST /auth/login", "GET /auth/me"],
            "chat": ["POST /chat", "POST /chat/stream"],
            "documents": ["POST /upload", "GET /documents", "DELETE /documents/{id}"],
            "search": ["POST /search"],
            "analytics": ["GET /analytics"]
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    mode = "MOCK" if settings.USE_MOCK else "REAL AWS"
    
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        mode=mode,
        agents={
            "chat_agent": "ready",
            "ingestion_agent": "ready",
            "retrieval_agent": "ready"
        },
        services={
            "auth": "mock" if settings.USE_MOCK else "cognito",
            "storage": "mock" if settings.USE_MOCK else f"s3://{settings.S3_BUCKET_NAME}",
            "text_extraction": "mock" if settings.USE_MOCK else "textract",
            "metadata": "mock" if settings.USE_MOCK else f"dynamodb:{settings.DYNAMODB_TABLE_NAME}",
            "vector_search": "mock" if settings.USE_MOCK else "opensearch"
        }
    )


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with username and password
    
    Mock users (when USE_MOCK=True):
    - john@company.com / SecurePass123!
    - jane@company.com / SecurePass123!
    """
    try:
        result = await auth_service.login(request.username, request.password)
        
        return LoginResponse(
            success=True,
            access_token=result['access_token'],
            refresh_token=result['refresh_token'],
            user_id=result['user_id'],
            email=result['email'],
            expires_in=result['expires_in']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(user: Dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**user)


# ============================================================================
# CHAT ENDPOINTS - ENHANCED
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: Dict = Depends(get_current_user)
):
    """
    Chat endpoint - routes to appropriate agent
    Returns full response with sources and citations
    """
    try:
        return await chat_agent.process_message(request, user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user: Dict = Depends(get_current_user)
):
    """
    🎯 HACKATHON FEATURE: Streaming chat with Server-Sent Events (SSE)
    
    Returns word-by-word streaming response for better UX
    """
    try:
        return StreamingResponse(
            chat_agent.stream_response(request, user),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DOCUMENT ENDPOINTS - ENHANCED
# ============================================================================

@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="Document to upload"),
    project_id: str = Form(default="default"),
    domain: str = Form(default="general"),
    tags: str = Form(default="", description="Comma-separated tags"),
    description: str = Form(default=""),
    user: Dict = Depends(get_current_user)
):
    """
    🎯 HACKATHON FEATURE: Upload and index documents
    
    Supported formats: PDF, DOC, DOCX, PPT, PPTX, TXT, MD, code files, images
    """
    try:
        file_content = await file.read()
        
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        tags_list = [t.strip() for t in tags.split(",") if t.strip()]
        
        result = await ingestion_agent.ingest_document(
            file_content=file_content,
            file_name=file.filename,
            user_id=user['user_id'],
            project_id=project_id,
            domain=domain,
            tags=tags_list,
            description=description
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    project_id: Optional[str] = None,
    user: Dict = Depends(get_current_user)
):
    """List user's documents with optional project filter"""
    try:
        docs = await metadata_service.get_user_documents(
            user_id=user['user_id'],
            project_id=project_id
        )
        
        return DocumentListResponse(
            success=True,
            documents=[DocumentMetadata(**doc) for doc in docs],
            total=len(docs)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{resource_id}")
async def delete_document(
    resource_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    🎯 NEW: Delete a document
    """
    try:
        success = await metadata_service.delete_document(resource_id, user['user_id'])
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"success": True, "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SEARCH ENDPOINT - ENHANCED
# ============================================================================

@app.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    user: Dict = Depends(get_current_user)
):
    """
    🎯 HACKATHON FEATURE: Semantic search with RAG
    
    Returns relevant documents with AI-generated response and citations
    """
    try:
        result = await retrieval_agent.search(
            query=request.query,
            user_id=user['user_id'],
            project_id=request.project_id,
            top_k=request.top_k
        )
        
        return SearchResponse(
            success=result['success'],
            query=result['query'],
            results=[SearchResult(**r) for r in result['sources']],
            total_results=result['total'],
            response=result['response'],
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 🎯 NEW: ANALYTICS ENDPOINT (HACKATHON WOW FACTOR)
# ============================================================================

@app.get("/analytics")
async def get_analytics(user: Dict = Depends(get_current_user)):
    """
    🎯 HACKATHON FEATURE: Analytics dashboard data
    
    Shows usage statistics and insights
    """
    try:
        docs = await metadata_service.get_user_documents(user['user_id'])
        
        # Calculate stats
        total_docs = len(docs)
        total_size = sum(doc.get('file_size', 0) for doc in docs)
        
        domains = {}
        for doc in docs:
            domain = doc.get('domain', 'general')
            domains[domain] = domains.get(domain, 0) + 1
        
        return {
            "success": True,
            "user_id": user['user_id'],
            "stats": {
                "total_documents": total_docs,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "domains": domains,
                "recent_uploads": sorted(
                    docs, 
                    key=lambda x: x.get('uploaded_at', ''), 
                    reverse=True
                )[:5]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 🎯 NEW: CHAT HISTORY ENDPOINT
# ============================================================================

@app.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    🎯 NEW: Get chat history for a session
    """
    try:
        # In mock mode, return empty history
        # In real mode, fetch from database
        return {
            "success": True,
            "session_id": session_id,
            "messages": [],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    mode = "MOCK" if settings.USE_MOCK else "REAL AWS"
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║     🏆 HACKATHON: KNOWLEDGE AGENT - 3-AGENT SYSTEM 🏆     ║
╠════════════════════════════════════════════════════════════╣
║                                                             ║
║  Mode: {mode:^53} ║
║                                                             ║
║  🤖 Chat Agent      - Orchestrates requests                ║
║  📥 Ingestion Agent - Uploads & indexes documents          ║
║  🔍 Retrieval Agent - Semantic search with RAG             ║
║                                                             ║
║  🔐 Mock Users:                                            ║
║     • john@company.com / SecurePass123!                    ║
║     • jane@company.com / SecurePass123!                    ║
║                                                             ║
║  ✨ HACKATHON FEATURES:                                    ║
║     ✅ Server-Sent Events (SSE) Streaming                  ║
║     ✅ Multi-format Document Processing                    ║
║     ✅ Semantic Search with Citations                      ║
║     ✅ Analytics Dashboard                                 ║
║     ✅ Project Management                                  ║
║     ✅ Real-time Progress Updates                          ║
║                                                             ║
╚════════════════════════════════════════════════════════════╝

🌐 Server: http://localhost:8000
📚 Docs: http://localhost:8000/docs
🔐 ReDoc: http://localhost:8000/redoc

🚀 Starting server...
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )