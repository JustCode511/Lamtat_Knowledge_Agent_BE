"""
agents.py
The 3 Agents: Chat, Ingestion, Retrieval
"""

import hashlib
import time
from datetime import datetime
from typing import Dict, Any, AsyncGenerator
import asyncio
import json

from models import ChatRequest, ChatResponse, UploadResponse, SearchResponse, SearchResult
from services import (
    StorageService, TextExtractionService, MetadataService, VectorSearchService
)


# # ============================================================================
# # AGENT 1: CHAT AGENT (Orchestrator)
# # ============================================================================

# class ChatAgent:
#     """
#     Main orchestrator - routes requests to appropriate agents
#     """
    
#     def __init__(self, ingestion_agent, retrieval_agent):
#         self.ingestion_agent = ingestion_agent
#         self.retrieval_agent = retrieval_agent
#         self.name = "ChatAgent"
#         print(f"🤖 {self.name} initialized")
    
#     async def classify_intent(self, message: str) -> str:
#         """Classify user intent"""
#         message_lower = message.lower()
        
#         if any(word in message_lower for word in ["upload", "ingest", "add", "index", "store"]):
#             return "ingest"
#         elif any(word in message_lower for word in ["find", "search", "how", "what", "where", "show", "tell", "explain"]):
#             return "retrieve"
#         else:
#             return "chat"
    
#     async def process_message(self, request: ChatRequest, user_context: Dict) -> ChatResponse:
#         """Process message and route to appropriate agent"""
        
#         print(f"\n🤖 [{self.name}] Processing: {request.message}")
        
#         intent = await self.classify_intent(request.message)
#         print(f"   📊 Intent: {intent}")
        
#         if intent == "ingest":
#             response_text = """I can help you upload documents!

# Use the /upload endpoint to upload your files. I'll:
# - Store them securely in S3
# - Extract text from any format
# - Make them searchable

# Ready to upload?"""
#             delegated_to = "IngestionAgent"
#             sources = None
            
#         elif intent == "retrieve":
#             # Delegate to Retrieval Agent
#             result = await self.retrieval_agent.search(
#                 query=request.message,
#                 user_id=user_context['user_id'],
#                 project_id=request.project_id
#             )
#             response_text = result['response']
#             delegated_to = "RetrievalAgent"
#             sources = result.get('sources', [])
            
#         else:
#             response_text = """Hello! I'm your Knowledge Agent. I can help you:

# 1. **Upload & Index** - Store and index your documents
# 2. **Search & Find** - Semantic search across your knowledge base
# 3. **Answer Questions** - Get answers with citations from your docs

# What would you like to do?"""
#             delegated_to = None
#             sources = None
        
#         return ChatResponse(
#             success=True,
#             response=response_text,
#             agent=self.name,
#             delegated_to=delegated_to,
#             sources=sources,
#             timestamp=datetime.utcnow().isoformat()
#         )
    
#     async def stream_response(self, request: ChatRequest, user_context: Dict) -> AsyncGenerator[str, None]:
#         """Stream response with SSE"""
        
#         # Send initial status
#         yield f"data: {json.dumps({'type': 'status', 'content': '🤔 Analyzing your question...'})}\n\n"
#         await asyncio.sleep(0.3)
        
#         # Classify intent
#         intent = await self.classify_intent(request.message)
        
#         yield f"data: {json.dumps({'type': 'status', 'content': f'📊 Intent: {intent}'})}\n\n"
#         await asyncio.sleep(0.3)
        
#         # Get response based on intent
#         if intent == "retrieve":
#             yield f"data: {json.dumps({'type': 'status', 'content': '🔍 Searching knowledge base...'})}\n\n"
#             await asyncio.sleep(0.5)
            
#             result = await self.retrieval_agent.search(
#                 query=request.message,
#                 user_id=user_context['user_id'],
#                 project_id=request.project_id
#             )
#             response_text = result['response']
#         else:
#             response = await self.process_message(request, user_context)
#             response_text = response.response
        
#         # Stream word by word
#         for word in response_text.split():
#             yield f"data: {json.dumps({'type': 'chunk', 'content': word + ' '})}\n\n"
#             await asyncio.sleep(0.05)
        
#         # Send completion
#         yield f"data: {json.dumps({'type': 'complete'})}\n\n"

# ============================================================================
# AGENT 1: CHAT AGENT (Orchestrator) - ENHANCED
# ============================================================================

class ChatAgent:
    """
    Main orchestrator - intelligently routes requests to appropriate agents
    Auto-detects if user wants search or conversational chat
    """
    
    def __init__(self, ingestion_agent, retrieval_agent):
        self.ingestion_agent = ingestion_agent
        self.retrieval_agent = retrieval_agent
        self.name = "ChatAgent"
        print(f"🤖 {self.name} initialized")
    
    async def classify_intent(self, message: str) -> str:
        """Classify user intent - improved logic"""
        message_lower = message.lower()
        
        # Ingestion intent
        if any(word in message_lower for word in ["upload", "ingest", "add", "index", "store"]):
            return "ingest"
        
        # Search/RAG intent - questions that need document lookup
        search_indicators = [
            "what", "how", "why", "when", "where", "who",
            "explain", "tell me", "show me", "find", "search",
            "does", "is", "are", "can", "should", "would",
            "describe", "define", "list"
        ]
        
        # If message starts with question word or has search intent, use retrieval
        first_word = message_lower.split()[0] if message_lower.split() else ""
        if first_word in search_indicators or any(word in message_lower for word in search_indicators):
            return "retrieve"
        
        # Default to chat for greetings and general conversation
        chat_indicators = ["hi", "hello", "hey", "thanks", "thank you", "bye", "ok", "okay"]
        if any(word in message_lower for word in chat_indicators):
            return "chat"
        
        # Default to retrieve (RAG) for everything else
        return "retrieve"
    
    async def process_message(self, request: ChatRequest, user_context: Dict) -> ChatResponse:
        """Process message and route to appropriate agent"""
        
        print(f"\n🤖 [{self.name}] Processing: {request.message}")
        
        intent = await self.classify_intent(request.message)
        print(f"   📊 Intent: {intent}")
        
        if intent == "ingest":
            response_text = """I can help you upload documents!

Use the 📎 paperclip button to upload your files. I'll:
- Store them securely
- Extract text from any format
- Make them searchable

Ready to upload?"""
            delegated_to = "IngestionAgent"
            sources = None
            
        elif intent == "retrieve":
            # Delegate to Retrieval Agent with RAG
            print(f"   🔍 Delegating to RetrievalAgent for RAG search")
            result = await self.retrieval_agent.search(
                query=request.message,
                user_id=user_context['user_id'],
                project_id=request.project_id
            )
            response_text = result['response']
            delegated_to = "RetrievalAgent"
            sources = result.get('sources', [])
            
        else:
            response_text = """Hello! I'm your Knowledge Agent. I can help you:

1. **Upload & Index** - Store and index your documents
2. **Search & Find** - Answer questions from your knowledge base
3. **Provide Context** - Get answers with source citations

Just ask me anything or upload a document to get started!"""
            delegated_to = None
            sources = None
        
        return ChatResponse(
            success=True,
            response=response_text,
            agent=self.name,
            delegated_to=delegated_to,
            sources=sources,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def stream_response(self, request: ChatRequest, user_context: Dict) -> AsyncGenerator[str, None]:
        """Stream response with SSE - intelligently routes to search or chat"""
        
        # Send initial status
        yield f"data: {json.dumps({'type': 'status', 'content': '🤔 Analyzing your question...'})}\n\n"
        await asyncio.sleep(0.3)
        
        # Classify intent
        intent = await self.classify_intent(request.message)
        
        yield f"data: {json.dumps({'type': 'status', 'content': f'🎯 Mode: {intent.upper()}'})}\n\n"
        await asyncio.sleep(0.3)
        
        # Route based on intent
        if intent == "retrieve":
            # Use streaming search from RetrievalAgent
            yield f"data: {json.dumps({'type': 'status', 'content': '🔍 Searching knowledge base...'})}\n\n"
            await asyncio.sleep(0.3)
            
            # Stream search results
            async for chunk in self.retrieval_agent.stream_search(
                query=request.message,
                user_id=user_context['user_id'],
                project_id=request.project_id
            ):
                yield chunk
        else:
            # Regular chat response
            response = await self.process_message(request, user_context)
            response_text = response.response
            
            # Stream word by word
            for word in response_text.split():
                yield f"data: {json.dumps({'type': 'chunk', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.05)
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'sources': []})}\n\n"


# ============================================================================
# AGENT 2: INGESTION AGENT
# ============================================================================

class IngestionAgent:
    """
    Handles document uploads and indexing
    """
    
    def __init__(
        self,
        storage: StorageService,
        text_extraction: TextExtractionService,
        metadata: MetadataService
    ):
        self.storage = storage
        self.text_extraction = text_extraction
        self.metadata = metadata
        self.name = "IngestionAgent"
        print(f"📥 {self.name} initialized")
    
    async def ingest_document(
        self,
        file_content: bytes,
        file_name: str,
        user_id: str,
        project_id: str,
        domain: str,
        tags: list,
        description: str
    ) -> UploadResponse:
        """Complete ingestion pipeline"""
        
        start_time = time.time()
        
        print(f"\n📥 [{self.name}] Starting ingestion: {file_name}")
        print(f"   User: {user_id}")
        print(f"   Project: {project_id}")
        print(f"   Size: {len(file_content)} bytes")
        
        try:
            # Step 1: Generate resource ID
            resource_id = hashlib.sha256(
                f"{user_id}_{file_name}_{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]
            
            print(f"   1️⃣  Resource ID: {resource_id}")
            
            # Step 2: Upload to S3
            print(f"   2️⃣  Uploading to S3...")
            s3_key = await self.storage.upload_file(
                content=file_content,
                filename=file_name,
                metadata={
                    'user_id': user_id,
                    'project_id': project_id,
                    'resource_id': resource_id,
                    'domain': domain
                }
            )
            
            # Step 3: Extract text
            print(f"   3️⃣  Extracting text...")
            extracted_text = await self.text_extraction.extract_text(s3_key, file_name)
            print(f"      Extracted {len(extracted_text)} characters")
            
            # Step 4: Save metadata
            print(f"   4️⃣  Saving metadata...")
            await self.metadata.save_metadata({
                'resource_id': resource_id,
                'user_id': user_id,
                'file_name': file_name,
                'file_type': file_name.split('.')[-1],
                'file_size': len(file_content),
                's3_key': s3_key,
                'project_id': project_id,
                'domain': domain,
                'tags': tags,
                'description': description,
                'uploaded_at': datetime.utcnow().isoformat(),
                'status': 'completed'
            })
            
            processing_time = time.time() - start_time
            
            print(f"   ✅ Ingestion complete ({processing_time:.2f}s)")
            
            return UploadResponse(
                success=True,
                message=f"Successfully ingested {file_name}",
                resource_id=resource_id,
                file_name=file_name,
                file_size=len(file_content),
                s3_key=s3_key,
                processing_time=processing_time
            )
            
        except Exception as e:
            print(f"   ❌ Ingestion failed: {str(e)}")
            raise


# ============================================================================
# AGENT 3: RETRIEVAL AGENT
# ============================================================================

class RetrievalAgent:
    """
    Handles knowledge retrieval and search (RAG)
    """
    
    def __init__(
        self,
        vector_search: VectorSearchService,
        metadata: MetadataService
    ):
        self.vector_search = vector_search
        self.metadata = metadata
        self.name = "RetrievalAgent"
        print(f"🔍 {self.name} initialized")
    
    async def search(
        self,
        query: str,
        user_id: str,
        project_id: str = None,
        top_k: int = 5
    ) -> Dict:
        """Search knowledge base with RAG"""
        
        print(f"\n🔍 [{self.name}] Searching: {query}")
        
        try:
            # Vector search
            results = await self.vector_search.search(
                query=query,
                user_id=user_id,
                filters={'project_id': project_id, 'top_k': top_k}
            )
            
            print(f"   Found {len(results)} results")
            
            # Generate response from results (RAG)
            if results:
                response = "Based on your knowledge base, here's what I found:\n\n"
                
                for idx, r in enumerate(results[:3], 1):
                    response += f"**{idx}. {r['file_name']}** (Relevance: {r['score']:.2f})\n"
                    response += f"{r['text']}\n\n"
                
                response += "\n📚 **Sources:**\n"
                for r in results[:3]:
                    response += f"• {r['file_name']}\n"
            else:
                response = "No relevant documents found. Try different keywords or upload relevant documents first."
            
            return {
                'success': True,
                'query': query,
                'response': response,
                'sources': results,
                'total': len(results)
            }
            
        except Exception as e:
            print(f"   ❌ Search failed: {str(e)}")
            return {
                'success': False,
                'query': query,
                'response': f"Search failed: {str(e)}",
                'sources': [],
                'total': 0
            }

    async def stream_search(
        self,
        query: str,
        user_id: str,
        project_id: str = None,
        top_k: int = 5
    ) -> AsyncGenerator[str, None]:
        """Stream search results with RAG"""
        
        import json
        
        print(f"\n🔍 [{self.name}] Streaming Search: {query}")
        
        try:
            # Vector search
            yield f"data: {json.dumps({'type': 'status', 'content': '🔍 Searching documents...'})}\n\n"
            await asyncio.sleep(0.3)
            
            results = await self.vector_search.search(
                query=query,
                user_id=user_id,
                filters={'project_id': project_id, 'top_k': top_k}
            )
            
            print(f"   Found {len(results)} results")
            
            yield f"data: {json.dumps({'type': 'status', 'content': f'✅ Found {len(results)} documents'})}\n\n"
            await asyncio.sleep(0.3)
            
            # Generate response from results (RAG)
            if results:
                yield f"data: {json.dumps({'type': 'status', 'content': '🤖 Generating answer...'})}\n\n"
                await asyncio.sleep(0.3)
                
                response = "Based on your knowledge base:\n\n"
                
                for idx, r in enumerate(results[:3], 1):
                    response += f"**{idx}. {r['file_name']}** (Relevance: {r['score']:.2f})\n"
                    response += f"{r['text']}\n\n"
                
                response += "\n📚 **Sources:**\n"
                for r in results[:3]:
                    response += f"• {r['file_name']}\n"
                
                # Stream word by word
                for word in response.split():
                    yield f"data: {json.dumps({'type': 'chunk', 'content': word + ' '})}\n\n"
                    await asyncio.sleep(0.05)
            else:
                response = "No relevant documents found. Try different keywords or upload relevant documents first."
                for word in response.split():
                    yield f"data: {json.dumps({'type': 'chunk', 'content': word + ' '})}\n\n"
                    await asyncio.sleep(0.05)
            
            # Send completion with sources
            yield f"data: {json.dumps({'type': 'complete', 'sources': results, 'total': len(results)})}\n\n"
            
        except Exception as e:
            print(f"   ❌ Search failed: {str(e)}")
            error_msg = f"Search failed: {str(e)}"
            for word in error_msg.split():
                yield f"data: {json.dumps({'type': 'chunk', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.05)
            yield f"data: {json.dumps({'type': 'complete', 'sources': [], 'total': 0})}\n\n"