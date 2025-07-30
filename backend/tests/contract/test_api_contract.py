"""API contract tests for the Social Media Automation System."""
import json
import pytest
import requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, HttpUrl, Field, validator
from datetime import datetime
from enum import Enum

# API base URL
BASE_URL = "http://localhost:8080/api"

# --- API Contract Definitions ---

class Platform(str, Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TIKTOK = "tiktok"

class PostStatus(str, Enum):
    """Possible post statuses."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"
    CANCELED = "canceled"

class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)

class UserInDB(UserBase):
    """User model for database storage."""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime

class PostBase(BaseModel):
    """Base post model."""
    platform: Platform
    content: str = Field(..., min_length=1, max_length=2000)
    scheduled_time: datetime
    media_urls: List[HttpUrl] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PostCreate(PostBase):
    """Post creation model."""
    pass

class PostInDB(PostBase):
    """Post model for database storage."""
    id: str
    user_id: int
    status: PostStatus
    posted_time: Optional[datetime] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Analytics(BaseModel):
    """Analytics model."""
    post_id: str
    impressions: int = Field(ge=0)
    engagements: int = Field(ge=0)
    likes: int = Field(ge=0)
    comments: int = Field(ge=0)
    shares: int = Field(ge=0)
    clicks: int = Field(ge=0)
    reach: int = Field(ge=0)
    saved: int = Field(ge=0)
    video_views: Optional[int] = Field(ge=0, default=None)
    engagement_rate: float = Field(ge=0, le=100)
    collected_at: datetime

# API Endpoint Contracts
API_CONTRACT = {
    "/auth/register": {
        "method": "POST",
        "request": UserCreate,
        "response": UserInDB,
        "status_code": 201
    },
    "/auth/login": {
        "method": "POST",
        "request": {
            "username": "string",
            "password": "string"
        },
        "response": {
            "access_token": "string",
            "token_type": "string"
        },
        "status_code": 200
    },
    "/posts/": {
        "method": "GET",
        "query_params": {
            "platform": f"{'|'.join(p.value for p in Platform)}",
            "status": f"{'|'.join(s.value for s in PostStatus)}",
            "limit": "integer",
            "offset": "integer"
        },
        "response": List[PostInDB],
        "status_code": 200
    },
    "/posts/": {
        "method": "POST",
        "request": PostCreate,
        "response": PostInDB,
        "status_code": 201
    },
    "/posts/{post_id}": {
        "method": "GET",
        "response": PostInDB,
        "status_code": 200
    },
    "/posts/{post_id}/cancel": {
        "method": "POST",
        "request": {},
        "response": PostInDB,
        "status_code": 200
    },
    "/analytics/{post_id}": {
        "method": "GET",
        "response": Analytics,
        "status_code": 200
    }
}

# --- Test Fixtures ---

@pytest.fixture
def auth_headers():
    """Get authentication headers."""
    # In a real test, you would get a valid token from the auth endpoint
    return {"Authorization": "Bearer test_token"}

# --- Contract Tests ---

def test_api_contract():
    """Verify that the API contract is valid."""
    # This is a meta-test to ensure our contract definition is valid
    # It doesn't make actual HTTP requests
    
    # Test that all endpoints have required fields
    for endpoint, spec in API_CONTRACT.items():
        assert "method" in spec, f"Endpoint {endpoint} is missing 'method'"
        assert "status_code" in spec, f"Endpoint {endpoint} is missing 'status_code'"
        
        if spec["method"] in ["POST", "PUT", "PATCH"]:
            assert "request" in spec, f"Endpoint {endpoint} is missing 'request' schema"
        
        if "response" not in spec:
            pytest.fail(f"Endpoint {endpoint} is missing 'response' schema")

@pytest.mark.integration
class TestAPIContractCompliance:
    """Test that the API complies with the defined contract."""
    
    def test_auth_register(self, auth_headers):
        """Test the auth/register endpoint contract."""
        endpoint = "/auth/register"
        spec = API_CONTRACT[endpoint]
        
        # Test with valid data
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        # Validate request against the contract
        if "request" in spec and isinstance(spec["request"], type):
            spec["request"](**data)
        
        # Make the request
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check status code
        assert response.status_code == spec["status_code"], \
            f"Expected status {spec['status_code']}, got {response.status_code}"
        
        # Validate response against the contract
        if "response" in spec and isinstance(spec["response"], type):
            response_data = response.json()
            spec["response"](**response_data)
    
    def test_posts_endpoint(self, auth_headers):
        """Test the posts endpoint contract."""
        endpoint = "/posts/"
        spec = API_CONTRACT[endpoint]
        
        # Test GET
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == spec["status_code"], \
            f"Expected status {spec['status_code']}, got {response.status_code}"
        
        # Validate response is a list of posts
        posts = response.json()
        assert isinstance(posts, list)
        if posts:  # If there are posts, validate their structure
            for post in posts:
                PostInDB(**post)
        
        # Test POST
        post_data = {
            "platform": "instagram",
            "content": "Test post content",
            "scheduled_time": "2023-12-31T23:59:59Z",
            "media_urls": ["https://example.com/image.jpg"],
            "metadata": {
                "hashtags": ["test", "api"]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=post_data,
            headers={
                "Authorization": auth_headers["Authorization"],
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 201, \
            f"Expected status 201, got {response.status_code}"
        
        # Validate the created post
        post = response.json()
        PostInDB(**post)
        
        return post["id"]  # Return the post ID for use in other tests
    
    def test_single_post_endpoint(self, auth_headers):
        """Test the single post endpoint contract."""
        # First create a post to test with
        post_id = self.test_posts_endpoint(auth_headers)
        
        endpoint = f"/posts/{post_id}"
        spec = API_CONTRACT["/posts/{post_id}"]
        
        # Test GET
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == spec["status_code"], \
            f"Expected status {spec['status_code']}, got {response.status_code}"
        
        # Validate response
        post = response.json()
        PostInDB(**post)
    
    def test_cancel_post_endpoint(self, auth_headers):
        """Test the cancel post endpoint contract."""
        # First create a post to test with
        post_id = self.test_posts_endpoint(auth_headers)
        
        endpoint = f"/posts/{post_id}/cancel"
        spec = API_CONTRACT["/posts/{post_id}/cancel"]
        
        # Test POST
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == spec["status_code"], \
            f"Expected status {spec['status_code']}, got {response.status_code}"
        
        # Validate response
        post = response.json()
        PostInDB(**post)
        assert post["status"] == "canceled"
    
    def test_analytics_endpoint(self, auth_headers):
        """Test the analytics endpoint contract."""
        # First create a post to test with
        post_id = self.test_posts_endpoint(auth_headers)
        
        endpoint = f"/analytics/{post_id}"
        spec = API_CONTRACT["/analytics/{post_id}"]
        
        # Test GET
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        # Analytics might not exist yet, which is okay
        if response.status_code == 200:
            analytics = response.json()
            Analytics(**analytics)
        else:
            assert response.status_code == 404, \
                f"Expected status 200 or 404, got {response.status_code}"

def test_generate_openapi_spec():
    """Generate an OpenAPI specification from the contract.
    This can be used to document the API and generate client libraries.
    """
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Social Media Automation API",
            "version": "1.0.0",
            "description": "API for scheduling and managing social media posts"
        },
        "paths": {},
        "components": {
            "schemas": {
                "User": UserCreate.schema(),
                "Post": PostCreate.schema(),
                "Analytics": Analytics.schema()
            }
        }
    }
    
    # Add paths from the contract
    for endpoint, spec in API_CONTRACT.items():
        path_item = {}
        method = spec["method"].lower()
        
        # Add parameters
        parameters = []
        if "query_params" in spec:
            for param_name, param_type in spec["query_params"].items():
                parameters.append({
                    "name": param_name,
                    "in": "query",
                    "schema": {"type": param_type}
                })
        
        # Add request body
        request_body = {}
        if "request" in spec:
            if isinstance(spec["request"], type):
                schema = spec["request"].schema()
                request_body = {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{spec['request'].__name__}"}
                        }
                    },
                    "required": True
                }
            else:
                request_body = {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": spec["request"]
                            }
                        }
                    },
                    "required": True
                }
        
        # Add responses
        responses = {
            str(spec["status_code"]): {
                "description": "Success"
            }
        }
        
        if "response" in spec:
            if isinstance(spec["response"], type):
                responses[str(spec["status_code"])]["content"] = {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{spec['response'].__name__}"}
                    }
                }
            else:
                responses[str(spec["status_code"])]["content"] = {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": spec["response"]
                        }
                    }
                }
        
        # Add the path item to the spec
        if endpoint not in openapi_spec["paths"]:
            openapi_spec["paths"][endpoint] = {}
        
        openapi_spec["paths"][endpoint][method] = {
            "parameters": parameters,
            "responses": responses
        }
        
        if request_body:
            openapi_spec["paths"][endpoint][method]["requestBody"] = request_body
    
    # Save the OpenAPI spec to a file
    with open("openapi.json", "w") as f:
        json.dump(openapi_spec, f, indent=2)
    
    print("OpenAPI specification generated: openapi.json")

if __name__ == "__main__":
    # Generate the OpenAPI spec when run directly
    test_generate_openapi_spec()
