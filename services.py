# """
# services.py
# All AWS service implementations - Mock and Real
# Auth, Storage, Text Extraction, Metadata, Vector Search
# """

# from abc import ABC, abstractmethod
# from typing import Dict, Any, List, Optional
# from datetime import datetime, timedelta
# import hashlib
# import time
# import asyncio

# from config import settings


# # ============================================================================
# # AUTHENTICATION SERVICE
# # ============================================================================

# class AuthService(ABC):
#     @abstractmethod
#     async def login(self, username: str, password: str) -> Dict:
#         pass
    
#     @abstractmethod
#     async def verify_token(self, token: str) -> Dict:
#         pass


# class MockAuthService(AuthService):
#     """Mock authentication - no real Cognito"""
    
#     async def login(self, username: str, password: str) -> Dict:
#         await asyncio.sleep(0.3)  # Simulate network
        
#         if username in settings.MOCK_USERS:
#             user = settings.MOCK_USERS[username]
#             if user["password"] == password:
#                 return {
#                     "access_token": f"mock_token_{username}_{int(time.time())}",
#                     "refresh_token": f"mock_refresh_{username}",
#                     "user_id": user["user_id"],
#                     "email": username,
#                     "expires_in": 3600
#                 }
        
#         raise Exception("Invalid credentials")
    
#     async def verify_token(self, token: str) -> Dict:
#         if not token.startswith("mock_token_"):
#             raise Exception("Invalid token")
        
#         parts = token.split("_")
#         email = "_".join(parts[2:-1])
        
#         if email in settings.MOCK_USERS:
#             return {
#                 "user_id": settings.MOCK_USERS[email]["user_id"],
#                 "email": email,
#                 "verified": True
#             }
        
#         raise Exception("Invalid token")


# class RealCognitoService(AuthService):
#     """Real AWS Cognito"""
    
#     def __init__(self):
#         import boto3
#         self.client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)
    
#     async def login(self, username: str, password: str) -> Dict:
#         response = self.client.initiate_auth(
#             ClientId=settings.COGNITO_CLIENT_ID,
#             AuthFlow='USER_PASSWORD_AUTH',
#             AuthParameters={'USERNAME': username, 'PASSWORD': password}
#         )
        
#         auth = response['AuthenticationResult']
#         user_response = self.client.get_user(AccessToken=auth['AccessToken'])
        
#         return {
#             "access_token": auth['AccessToken'],
#             "refresh_token": auth.get('RefreshToken', ''),
#             "user_id": user_response['Username'],
#             "email": next((a['Value'] for a in user_response['UserAttributes'] if a['Name'] == 'email'), ''),
#             "expires_in": auth['ExpiresIn']
#         }
    
#     async def verify_token(self, token: str) -> Dict:
#         response = self.client.get_user(AccessToken=token)
#         return {
#             "user_id": response['Username'],
#             "email": next((a['Value'] for a in response['UserAttributes'] if a['Name'] == 'email'), ''),
#             "verified": True
#         }


# # ============================================================================
# # STORAGE SERVICE (S3)
# # ============================================================================

# class StorageService(ABC):
#     @abstractmethod
#     async def upload_file(self, content: bytes, filename: str, metadata: Dict) -> str:
#         pass
    
#     @abstractmethod
#     async def get_file_url(self, s3_key: str) -> str:
#         pass


# class MockStorageService(StorageService):
#     """Mock S3 storage"""
    
#     def __init__(self):
#         self.storage = {}
    
#     async def upload_file(self, content: bytes, filename: str, metadata: Dict) -> str:
#         s3_key = f"users/{metadata['user_id']}/projects/{metadata['project_id']}/{metadata['resource_id']}/{filename}"
#         self.storage[s3_key] = content
#         print(f"   📦 [MOCK] Uploaded: {s3_key} ({len(content)} bytes)")
#         return s3_key
    
#     async def get_file_url(self, s3_key: str) -> str:
#         return f"mock://s3/{settings.S3_BUCKET_NAME}/{s3_key}"


# class RealS3Service(StorageService):
#     """Real AWS S3"""
    
#     def __init__(self):
#         import boto3
#         self.client = boto3.client('s3', region_name=settings.AWS_REGION)
    
#     async def upload_file(self, content: bytes, filename: str, metadata: Dict) -> str:
#         s3_key = f"users/{metadata['user_id']}/projects/{metadata['project_id']}/{metadata['resource_id']}/{filename}"
        
#         self.client.put_object(
#             Bucket=settings.S3_BUCKET_NAME,
#             Key=s3_key,
#             Body=content,
#             Metadata={k.replace('_', '-'): str(v) for k, v in metadata.items()},
#             ServerSideEncryption='AES256'
#         )
        
#         print(f"   📦 [REAL] Uploaded to S3: {s3_key}")
#         return s3_key
    
#     async def get_file_url(self, s3_key: str) -> str:
#         return self.client.generate_presigned_url(
#             'get_object',
#             Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': s3_key},
#             ExpiresIn=3600
#         )


# # ============================================================================
# # TEXT EXTRACTION SERVICE (Textract)
# # ============================================================================

# class TextExtractionService(ABC):
#     @abstractmethod
#     async def extract_text(self, s3_key: str, filename: str) -> str:
#         pass


# class MockTextExtractionService(TextExtractionService):
#     """Mock text extraction"""
    
#     async def extract_text(self, s3_key: str, filename: str) -> str:
#         await asyncio.sleep(0.5)
#         return f"[MOCK] Extracted text from {filename}: Sample document content about authentication, JWT tokens, and security best practices..."


# class RealTextractService(TextExtractionService):
#     """Real AWS Textract"""
    
#     def __init__(self):
#         import boto3
#         self.client = boto3.client('textract', region_name=settings.AWS_REGION)
    
#     async def extract_text(self, s3_key: str, filename: str) -> str:
#         # Implementation would use Textract
#         return "[Real Textract extraction]"


# # ============================================================================
# # METADATA SERVICE (DynamoDB)
# # ============================================================================

# class MetadataService(ABC):
#     @abstractmethod
#     async def save_metadata(self, metadata: Dict) -> bool:
#         pass
    
#     @abstractmethod
#     async def get_user_documents(self, user_id: str, project_id: Optional[str]) -> List[Dict]:
#         pass


# class MockMetadataService(MetadataService):
#     """Mock DynamoDB"""
    
#     def __init__(self):
#         self.store = {}
    
#     async def save_metadata(self, metadata: Dict) -> bool:
#         self.store[metadata['resource_id']] = metadata
#         print(f"   🗄️  [MOCK] Saved metadata: {metadata['resource_id']}")
#         return True
    
#     async def get_user_documents(self, user_id: str, project_id: Optional[str]) -> List[Dict]:
#         docs = [doc for doc in self.store.values() if doc['user_id'] == user_id]
#         if project_id:
#             docs = [doc for doc in docs if doc['project_id'] == project_id]
#         return docs


# class RealDynamoDBService(MetadataService):
#     """Real AWS DynamoDB"""
    
#     def __init__(self):
#         import boto3
#         dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
#         self.table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
    
#     async def save_metadata(self, metadata: Dict) -> bool:
#         self.table.put_item(Item=metadata)
#         return True
    
#     async def get_user_documents(self, user_id: str, project_id: Optional[str]) -> List[Dict]:
#         # Query with GSI
#         return []


# # ============================================================================
# # VECTOR SEARCH SERVICE (OpenSearch)
# # ============================================================================

# class VectorSearchService(ABC):
#     @abstractmethod
#     async def search(self, query: str, user_id: str, filters: Dict) -> List[Dict]:
#         pass


# class MockVectorSearchService(VectorSearchService):
#     """Mock vector search"""
    
#     def __init__(self):
#         self.mock_docs = [
#             {
#                 "text": "Our authentication system uses JWT tokens with RS256 algorithm. Tokens expire after 24 hours.",
#                 "file_name": "auth.py",
#                 "score": 0.95,
#                 "resource_id": "doc1"
#             },
#             {
#                 "text": "Database configuration uses PostgreSQL with connection pooling for better performance.",
#                 "file_name": "db_config.py",
#                 "score": 0.87,
#                 "resource_id": "doc2"
#             },
#             {
#                 "text": "API routes are defined using FastAPI with automatic OpenAPI documentation generation.",
#                 "file_name": "api_routes.py",
#                 "score": 0.82,
#                 "resource_id": "doc3"
#             }
#         ]
    
#     async def search(self, query: str, user_id: str, filters: Dict) -> List[Dict]:
#         await asyncio.sleep(0.3)
#         # Simple keyword matching
#         query_words = query.lower().split()
#         results = []
        
#         for doc in self.mock_docs:
#             if any(word in doc['text'].lower() for word in query_words):
#                 results.append(doc)
        
#         return results[:filters.get('top_k', 5)]


# class RealOpenSearchService(VectorSearchService):
#     """Real AWS OpenSearch"""
    
#     def __init__(self):
#         # Initialize OpenSearch client
#         pass
    
#     async def search(self, query: str, user_id: str, filters: Dict) -> List[Dict]:
#         # Real vector search implementation
#         return []


# # ============================================================================
# # SERVICE FACTORY - Creates mock or real services
# # ============================================================================

# def get_auth_service() -> AuthService:
#     if settings.USE_MOCK:
#         return MockAuthService()
#     else:
#         return RealCognitoService()


# def get_storage_service() -> StorageService:
#     if settings.USE_MOCK:
#         return MockStorageService()
#     else:
#         return RealS3Service()


# def get_text_extraction_service() -> TextExtractionService:
#     if settings.USE_MOCK:
#         return MockTextExtractionService()
#     else:
#         return RealTextractService()


# def get_metadata_service() -> MetadataService:
#     if settings.USE_MOCK:
#         return MockMetadataService()
#     else:
#         return RealDynamoDBService()


# def get_vector_search_service() -> VectorSearchService:
#     if settings.USE_MOCK:
#         return MockVectorSearchService()
#     else:
#         return RealOpenSearchService()


"""
services.py - ENHANCED FOR HACKATHON
Added: Document deletion, Better mock data, Enhanced search
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib
import time
import asyncio

from config import settings


# ============================================================================
# AUTHENTICATION SERVICE
# ============================================================================

class AuthService(ABC):
    @abstractmethod
    async def login(self, username: str, password: str) -> Dict:
        pass
    
    @abstractmethod
    async def verify_token(self, token: str) -> Dict:
        pass


class MockAuthService(AuthService):
    """Mock authentication - no real Cognito"""
    
    async def login(self, username: str, password: str) -> Dict:
        await asyncio.sleep(0.3)
        
        if username in settings.MOCK_USERS:
            user = settings.MOCK_USERS[username]
            if user["password"] == password:
                return {
                    "access_token": f"mock_token_{username}_{int(time.time())}",
                    "refresh_token": f"mock_refresh_{username}",
                    "user_id": user["user_id"],
                    "email": username,
                    "expires_in": 3600
                }
        
        raise Exception("Invalid credentials")
    
    async def verify_token(self, token: str) -> Dict:
        if not token.startswith("mock_token_"):
            raise Exception("Invalid token")
        
        parts = token.split("_")
        email = "_".join(parts[2:-1])
        
        if email in settings.MOCK_USERS:
            return {
                "user_id": settings.MOCK_USERS[email]["user_id"],
                "email": email,
                "verified": True
            }
        
        raise Exception("Invalid token")


class RealCognitoService(AuthService):
    """Real AWS Cognito"""
    
    def __init__(self):
        import boto3
        self.client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)
    
    async def login(self, username: str, password: str) -> Dict:
        response = self.client.initiate_auth(
            ClientId=settings.COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': username, 'PASSWORD': password}
        )
        
        auth = response['AuthenticationResult']
        user_response = self.client.get_user(AccessToken=auth['AccessToken'])
        
        return {
            "access_token": auth['AccessToken'],
            "refresh_token": auth.get('RefreshToken', ''),
            "user_id": user_response['Username'],
            "email": next((a['Value'] for a in user_response['UserAttributes'] if a['Name'] == 'email'), ''),
            "expires_in": auth['ExpiresIn']
        }
    
    async def verify_token(self, token: str) -> Dict:
        response = self.client.get_user(AccessToken=token)
        return {
            "user_id": response['Username'],
            "email": next((a['Value'] for a in response['UserAttributes'] if a['Name'] == 'email'), ''),
            "verified": True
        }


# ============================================================================
# STORAGE SERVICE (S3)
# ============================================================================

class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, content: bytes, filename: str, metadata: Dict) -> str:
        pass
    
    @abstractmethod
    async def get_file_url(self, s3_key: str) -> str:
        pass
    
    @abstractmethod
    async def delete_file(self, s3_key: str) -> bool:
        pass


class MockStorageService(StorageService):
    """Mock S3 storage"""
    
    def __init__(self):
        self.storage = {}
    
    async def upload_file(self, content: bytes, filename: str, metadata: Dict) -> str:
        s3_key = f"users/{metadata['user_id']}/projects/{metadata['project_id']}/{metadata['resource_id']}/{filename}"
        self.storage[s3_key] = content
        print(f"   📦 [MOCK] Uploaded: {s3_key} ({len(content)} bytes)")
        return s3_key
    
    async def get_file_url(self, s3_key: str) -> str:
        return f"mock://s3/{settings.S3_BUCKET_NAME}/{s3_key}"
    
    async def delete_file(self, s3_key: str) -> bool:
        if s3_key in self.storage:
            del self.storage[s3_key]
            print(f"   🗑️  [MOCK] Deleted: {s3_key}")
            return True
        return False


class RealS3Service(StorageService):
    """Real AWS S3"""
    
    def __init__(self):
        import boto3
        self.client = boto3.client('s3', region_name=settings.AWS_REGION)
    
    async def upload_file(self, content: bytes, filename: str, metadata: Dict) -> str:
        s3_key = f"users/{metadata['user_id']}/projects/{metadata['project_id']}/{metadata['resource_id']}/{filename}"
        
        self.client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=content,
            Metadata={k.replace('_', '-'): str(v) for k, v in metadata.items()},
            ServerSideEncryption='AES256'
        )
        
        print(f"   📦 [REAL] Uploaded to S3: {s3_key}")
        return s3_key
    
    async def get_file_url(self, s3_key: str) -> str:
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )
    
    async def delete_file(self, s3_key: str) -> bool:
        try:
            self.client.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key
            )
            return True
        except:
            return False


# ============================================================================
# TEXT EXTRACTION SERVICE (Textract)
# ============================================================================

class TextExtractionService(ABC):
    @abstractmethod
    async def extract_text(self, s3_key: str, filename: str) -> str:
        pass


class MockTextExtractionService(TextExtractionService):
    """Mock text extraction with realistic content"""
    
    async def extract_text(self, s3_key: str, filename: str) -> str:
        await asyncio.sleep(0.5)
        
        # Return realistic mock content based on filename
        if 'auth' in filename.lower() or 'security' in filename.lower():
            return """
            Authentication System Documentation
            
            Our system uses JWT (JSON Web Tokens) for authentication. The tokens are signed using RS256 algorithm
            and expire after 24 hours. All API endpoints require a valid Bearer token in the Authorization header.
            
            Security Best Practices:
            - Always use HTTPS in production
            - Store tokens securely (never in localStorage)
            - Implement token refresh mechanism
            - Use short expiration times
            - Validate all inputs on the server side
            """
        elif 'database' in filename.lower() or 'db' in filename.lower():
            return """
            Database Configuration Guide
            
            We use PostgreSQL as our primary database with the following configuration:
            - Connection pooling with max 20 connections
            - Automatic failover for high availability
            - Daily backups with 30-day retention
            - Read replicas for improved performance
            
            Schema includes tables for users, documents, metadata, and search indices.
            """
        else:
            return f"""
            Extracted content from {filename}
            
            This is a sample document containing information about various topics including
            system architecture, API design, security practices, and deployment strategies.
            
            The document covers best practices for building scalable applications, implementing
            proper authentication and authorization, and maintaining code quality through testing
            and continuous integration.
            """


class RealTextractService(TextExtractionService):
    """Real AWS Textract"""
    
    def __init__(self):
        import boto3
        self.client = boto3.client('textract', region_name=settings.AWS_REGION)
    
    async def extract_text(self, s3_key: str, filename: str) -> str:
        response = self.client.detect_document_text(
            Document={'S3Object': {'Bucket': settings.S3_BUCKET_NAME, 'Name': s3_key}}
        )
        
        text = []
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                text.append(block['Text'])
        
        return '\n'.join(text)


# ============================================================================
# METADATA SERVICE (DynamoDB) - ENHANCED
# ============================================================================

class MetadataService(ABC):
    @abstractmethod
    async def save_metadata(self, metadata: Dict) -> bool:
        pass
    
    @abstractmethod
    async def get_user_documents(self, user_id: str, project_id: Optional[str]) -> List[Dict]:
        pass
    
    @abstractmethod
    async def delete_document(self, resource_id: str, user_id: str) -> bool:
        pass


class MockMetadataService(MetadataService):
    """Mock DynamoDB with enhanced features"""
    
    def __init__(self):
        self.store = {}
        # Add some sample documents for demo
        self._add_sample_documents()
    
    def _add_sample_documents(self):
        """Add sample documents for demo purposes"""
        sample_docs = [
            {
                'resource_id': 'sample-doc-1',
                'user_id': 'user-123',
                'file_name': 'authentication-guide.pdf',
                'file_type': 'pdf',
                'file_size': 245678,
                's3_key': 'users/user-123/projects/default/sample-doc-1/authentication-guide.pdf',
                'project_id': 'default',
                'domain': 'security',
                'tags': ['auth', 'jwt', 'security'],
                'description': 'Complete guide to authentication',
                'uploaded_at': (datetime.utcnow() - timedelta(days=2)).isoformat(),
                'status': 'completed'
            },
            {
                'resource_id': 'sample-doc-2',
                'user_id': 'user-123',
                'file_name': 'database-config.md',
                'file_type': 'md',
                'file_size': 12345,
                's3_key': 'users/user-123/projects/default/sample-doc-2/database-config.md',
                'project_id': 'default',
                'domain': 'backend',
                'tags': ['database', 'postgresql'],
                'description': 'Database configuration documentation',
                'uploaded_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                'status': 'completed'
            }
        ]
        
        for doc in sample_docs:
            self.store[doc['resource_id']] = doc
    
    async def save_metadata(self, metadata: Dict) -> bool:
        self.store[metadata['resource_id']] = metadata
        print(f"   🗄️  [MOCK] Saved metadata: {metadata['resource_id']}")
        return True
    
    async def get_user_documents(self, user_id: str, project_id: Optional[str]) -> List[Dict]:
        docs = [doc for doc in self.store.values() if doc['user_id'] == user_id]
        if project_id:
            docs = [doc for doc in docs if doc['project_id'] == project_id]
        return docs
    
    async def delete_document(self, resource_id: str, user_id: str) -> bool:
        if resource_id in self.store and self.store[resource_id]['user_id'] == user_id:
            del self.store[resource_id]
            print(f"   🗑️  [MOCK] Deleted metadata: {resource_id}")
            return True
        return False


class RealDynamoDBService(MetadataService):
    """Real AWS DynamoDB"""
    
    def __init__(self):
        import boto3
        dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
    
    async def save_metadata(self, metadata: Dict) -> bool:
        self.table.put_item(Item=metadata)
        return True
    
    async def get_user_documents(self, user_id: str, project_id: Optional[str]) -> List[Dict]:
        response = self.table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        
        docs = response['Items']
        if project_id:
            docs = [doc for doc in docs if doc.get('project_id') == project_id]
        return docs
    
    async def delete_document(self, resource_id: str, user_id: str) -> bool:
        try:
            self.table.delete_item(
                Key={'resource_id': resource_id},
                ConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            return True
        except:
            return False


# ============================================================================
# VECTOR SEARCH SERVICE (OpenSearch) - ENHANCED
# ============================================================================

class VectorSearchService(ABC):
    @abstractmethod
    async def search(self, query: str, user_id: str, filters: Dict) -> List[Dict]:
        pass


class MockVectorSearchService(VectorSearchService):
    """Mock vector search with better relevance"""
    
    def __init__(self):
        self.mock_docs = [
            {
                "text": "Our authentication system uses JWT tokens with RS256 algorithm. Tokens expire after 24 hours. All API endpoints require a valid Bearer token in the Authorization header.",
                "file_name": "authentication-guide.pdf",
                "score": 0.95,
                "resource_id": "sample-doc-1"
            },
            {
                "text": "Database configuration uses PostgreSQL with connection pooling (max 20 connections). We implement automatic failover for high availability and daily backups with 30-day retention.",
                "file_name": "database-config.md",
                "score": 0.89,
                "resource_id": "sample-doc-2"
            },
            {
                "text": "API routes are defined using FastAPI with automatic OpenAPI documentation. All endpoints support JSON request/response format with proper error handling.",
                "file_name": "api-routes.py",
                "score": 0.85,
                "resource_id": "sample-doc-3"
            },
            {
                "text": "Security best practices include HTTPS in production, proper input validation, rate limiting, and never storing sensitive data in localStorage.",
                "file_name": "security-checklist.md",
                "score": 0.82,
                "resource_id": "sample-doc-4"
            },
            {
                "text": "React application structure follows best practices with context-based state management, TypeScript for type safety, and Tailwind CSS for styling.",
                "file_name": "frontend-architecture.md",
                "score": 0.78,
                "resource_id": "sample-doc-5"
            }
        ]
    
    async def search(self, query: str, user_id: str, filters: Dict) -> List[Dict]:
        await asyncio.sleep(0.3)
        
        # Better keyword matching with scoring
        query_words = set(query.lower().split())
        results = []
        
        for doc in self.mock_docs:
            doc_words = set(doc['text'].lower().split())
            
            # Calculate relevance score based on word overlap
            overlap = len(query_words & doc_words)
            if overlap > 0:
                # Adjust score based on overlap
                adjusted_score = doc['score'] * (1 + overlap * 0.1)
                results.append({**doc, 'score': min(adjusted_score, 1.0)})
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:filters.get('top_k', 5)]


class RealOpenSearchService(VectorSearchService):
    """Real AWS OpenSearch with vector embeddings"""
    
    def __init__(self):
        from opensearchpy import OpenSearch, RequestsHttpConnection
        
        self.client = OpenSearch(
            hosts=[{'host': settings.OPENSEARCH_ENDPOINT, 'port': 443}],
            http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
    
    async def search(self, query: str, user_id: str, filters: Dict) -> List[Dict]:
        # Generate embedding for query (would use OpenAI/Cohere/Bedrock)
        # query_embedding = await self.get_embedding(query)
        
        # Search OpenSearch
        response = self.client.search(
            index='knowledge-base',
            body={
                'query': {
                    'bool': {
                        'must': [
                            {'knn': {'embedding': {'vector': [], 'k': filters.get('top_k', 5)}}},
                            {'term': {'user_id': user_id}}
                        ]
                    }
                }
            }
        )
        
        results = []
        for hit in response['hits']['hits']:
            results.append({
                'text': hit['_source']['text'],
                'file_name': hit['_source']['file_name'],
                'score': hit['_score'],
                'resource_id': hit['_source']['resource_id']
            })
        
        return results


# ============================================================================
# SERVICE FACTORY
# ============================================================================

def get_auth_service() -> AuthService:
    if settings.USE_MOCK:
        return MockAuthService()
    else:
        return RealCognitoService()


def get_storage_service() -> StorageService:
    if settings.USE_MOCK:
        return MockStorageService()
    else:
        return RealS3Service()


def get_text_extraction_service() -> TextExtractionService:
    if settings.USE_MOCK:
        return MockTextExtractionService()
    else:
        return RealTextractService()


def get_metadata_service() -> MetadataService:
    if settings.USE_MOCK:
        return MockMetadataService()
    else:
        return RealDynamoDBService()


def get_vector_search_service() -> VectorSearchService:
    if settings.USE_MOCK:
        return MockVectorSearchService()
    else:
        return RealOpenSearchService()