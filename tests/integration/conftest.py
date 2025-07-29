"""Configuration and fixtures for integration tests."""
import os
import pytest
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

# Test database URL (in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create a database engine for testing."""
    return create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope="session")
def tables(engine):
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine, tables):
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    # Clean up
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def manager(db_session):
    """Create a social media manager for testing."""
    # Initialize manager with test database
    manager = SocialMediaManager(database_url=TEST_DATABASE_URL)
    
    # Register mock platforms
    manager.register_platform("instagram", InstagramPlatform())
    manager.register_platform("facebook", FacebookPlatform())
    manager.register_platform("twitter", TwitterPlatform())
    manager.register_platform("tiktok", TikTokPlatform())
    
    return manager

@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    """Mock environment variables for testing."""
    # Mock required environment variables
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ENVIRONMENT", "test")
    
    # Mock social media API keys
    monkeypatch.setenv("INSTAGRAM_API_KEY", "test-instagram-key")
    monkeypatch.setenv("FACEBOOK_API_KEY", "test-facebook-key")
    monkeypatch.setenv("TWITTER_API_KEY", "test-twitter-key")
    monkeypatch.setenv("TIKTOK_API_KEY", "test-tiktok-key")
    
    # Mock storage paths
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("STORAGE_PATH", "/tmp/socialmedia-test")
        yield
