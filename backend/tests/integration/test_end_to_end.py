"""End-to-end tests for the Social Media Automation System."""
import os
import time
import json
import tempfile
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the FastAPI app and database models
from automation_stack.main import app
from automation_stack.database import Base, get_db
from automation_stack.manager import SocialMediaManager
from automation_stack.platforms import (
    InstagramPlatform,
    FacebookPlatform,
    TwitterPlatform,
    TikTokPlatform
)

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture for the test database
@pytest.fixture(scope="module")
def test_db():
    """Create a fresh database for each test module."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Set up test data
    db = TestingSessionLocal()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield db
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    db.close()

# Fixture for the test client
@pytest.fixture(scope="module")
def client(test_db):
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

# Fixture for the social media manager
@pytest.fixture(scope="module")
def manager(test_db):
    """Create a social media manager for testing."""
    # Create a temporary directory for test data
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize manager with test database
        manager = SocialMediaManager(database_url=TEST_DATABASE_URL)
        
        # Register mock platforms
        manager.register_platform("instagram", InstagramPlatform())
        manager.register_platform("facebook", FacebookPlatform())
        manager.register_platform("twitter", TwitterPlatform())
        manager.register_platform("tiktok", TikTokPlatform())
        
        yield manager

class TestEndToEnd:
    """End-to-end tests for the Social Media Automation System."""
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_schedule_and_post(self, manager):
        """Test scheduling and posting content to all platforms."""
        # Test data
        test_content = "Test post from integration test"
        scheduled_time = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        
        # Schedule posts for all platforms
        platform_ids = {}
        for platform in ["instagram", "facebook", "twitter", "tiktok"]:
            post_id = manager.schedule_post(
                platform=platform,
                content=test_content,
                scheduled_time=scheduled_time
            )
            platform_ids[platform] = post_id
            
            # Verify post was scheduled
            post = manager.get_post(post_id)
            assert post is not None
            assert post["content"] == test_content
            assert post["status"] == "scheduled"
        
        # Process scheduled posts (shouldn't post yet)
        processed = manager.process_scheduled_posts()
        assert processed == 0
        
        # Update scheduled time to the past and process again
        for post_id in platform_ids.values():
            post = manager.get_post(post_id)
            post["scheduled_time"] = (datetime.utcnow() - timedelta(minutes=1)).isoformat()
            manager.db.commit()
        
        # Process posts (should post now)
        processed = manager.process_scheduled_posts()
        assert processed == len(platform_ids)
        
        # Verify posts were marked as posted
        for platform, post_id in platform_ids.items():
            post = manager.get_post(post_id)
            assert post["status"] == "posted"
            assert post["posted_time"] is not None
    
    def test_api_endpoints(self, client, manager):
        """Test the REST API endpoints."""
        # Test creating a post
        post_data = {
            "platform": "instagram",
            "content": "Test post from API",
            "scheduled_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "media_urls": ["https://example.com/image.jpg"]
        }
        
        # Create post
        response = client.post("/api/posts/", json=post_data)
        assert response.status_code == 201
        post_id = response.json()["id"]
        
        # Get post
        response = client.get(f"/api/posts/{post_id}")
        assert response.status_code == 200
        assert response.json()["content"] == post_data["content"]
        
        # List posts
        response = client.get("/api/posts/")
        assert response.status_code == 200
        assert len(response.json()) > 0
        
        # Cancel post
        response = client.post(f"/api/posts/{post_id}/cancel")
        assert response.status_code == 200
        
        # Verify post was canceled
        response = client.get(f"/api/posts/{post_id}")
        assert response.json()["status"] == "canceled"
    
    def test_error_handling(self, manager):
        """Test error handling in the system."""
        # Test scheduling with invalid platform
        with pytest.raises(ValueError):
            manager.schedule_post(
                platform="invalid_platform",
                content="This should fail",
                scheduled_time=(datetime.utcnow() + timedelta(hours=1)).isoformat()
            )
        
        # Test getting non-existent post
        assert manager.get_post("non-existent-id") is None
        
        # Test canceling non-existent post
        assert not manager.cancel_post("non-existent-id")

# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
