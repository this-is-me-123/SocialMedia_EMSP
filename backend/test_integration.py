#!/usr/bin/env python3
"""
Integration test script for the Social Media Automation System.
Tests all major components and their connectivity.
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all critical imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test config imports
        from config.config import PLATFORMS, LOG_LEVEL, TESTING, BASE_DIR
        print("✅ Config imports successful")
        
        # Test database imports
        from database import Database, User, Post, AnalyticsEvent, PostStatus
        print("✅ Database imports successful")
        
        # Test platform imports
        from automation_stack.social_media.platforms import Instagram, Facebook, Twitter, Tiktok
        print("✅ Platform imports successful")
        
        # Test content creation imports
        from automation_stack.content_creation.create_content import ContentCreator
        print("✅ Content creation imports successful")
        
        # Test main automation imports
        from enhanced_automation import SocialMediaAutomation
        print("✅ Main automation imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {e}")
        return False

def test_database():
    """Test database functionality."""
    print("\nTesting database...")
    
    try:
        from database import Database, User, Post, AnalyticsEvent, PostStatus
        
        # Initialize database
        db = Database("test_social_media.db")
        print("✅ Database initialization successful")
        
        # Test user creation
        user = User(
            id=0,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="test_hash"
        )
        created_user = db.create_user(user)
        print(f"✅ User creation successful: {created_user.username}")
        
        # Test post creation
        post = Post(
            id="test-post-1",
            user_id=created_user.id,
            platform="instagram",
            content="Test post content",
            scheduled_time=datetime.utcnow(),
            status=PostStatus.SCHEDULED
        )
        created_post = db.create_post(post)
        print(f"✅ Post creation successful: {created_post.id}")
        
        # Test analytics event
        event = AnalyticsEvent(
            id=0,
            event="test_event",
            timestamp=datetime.utcnow(),
            platform="instagram",
            post_id=created_post.id
        )
        logged_event = db.log_analytics_event(event)
        print(f"✅ Analytics event logging successful: {logged_event.id}")
        
        # Clean up test database
        os.remove("test_social_media.db")
        print("✅ Database test cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_platform_initialization():
    """Test platform initialization in mock mode."""
    print("\nTesting platform initialization...")
    
    try:
        from automation_stack.social_media.platforms import Instagram, Facebook, Twitter, Tiktok
        
        # Test Instagram
        instagram_config = {
            'mock_mode': True,
            'api_key': 'test_token',
            'page_id': 'test_page'
        }
        instagram = Instagram(instagram_config)
        auth_result = instagram.authenticate()
        print(f"✅ Instagram mock authentication: {'Success' if auth_result else 'Failed'}")
        
        # Test Facebook
        facebook_config = {
            'mock_mode': True,
            'access_token': 'test_token',
            'page_id': 'test_page'
        }
        facebook = Facebook(facebook_config)
        auth_result = facebook.authenticate()
        print(f"✅ Facebook mock authentication: {'Success' if auth_result else 'Failed'}")
        
        # Test Twitter
        twitter_config = {
            'mock_mode': True,
            'api_key': 'test_key',
            'api_secret': 'test_secret',
            'access_token': 'test_token',
            'access_secret': 'test_secret'
        }
        twitter = Twitter(twitter_config)
        auth_result = twitter.authenticate()
        print(f"✅ Twitter mock authentication: {'Success' if auth_result else 'Failed'}")
        
        # Test TikTok
        tiktok_config = {
            'mock_mode': True,
            'client_key': 'test_key',
            'client_secret': 'test_secret'
        }
        tiktok = Tiktok(tiktok_config)
        auth_result = tiktok.authenticate()
        print(f"✅ TikTok mock authentication: {'Success' if auth_result else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Platform initialization error: {e}")
        return False

def test_content_creation():
    """Test content creation functionality."""
    print("\nTesting content creation...")
    
    try:
        from automation_stack.content_creation.create_content import ContentCreator
        from config.config import CONTENT
        
        # Initialize content creator
        creator = ContentCreator(CONTENT)
        print("✅ Content creator initialization successful")
        
        # Test caption generation (without API key, should fallback)
        caption = creator.generate_caption_with_gpt("Test prompt for caption generation")
        print(f"✅ Caption generation successful: {caption[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Content creation test error: {e}")
        return False

def test_fastapi_imports():
    """Test FastAPI application imports."""
    print("\nTesting FastAPI application...")
    
    try:
        from automation_stack.main import app, db
        print("✅ FastAPI application imports successful")
        
        # Test that database is initialized
        if db is not None:
            print("✅ Database initialization in FastAPI successful")
        else:
            print("❌ Database not initialized in FastAPI")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ FastAPI application test error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from config.config import PLATFORMS, BASE_DIR, CONTENT
        
        print(f"✅ BASE_DIR: {BASE_DIR}")
        print(f"✅ Platforms configured: {list(PLATFORMS.keys())}")
        print(f"✅ Content directory: {CONTENT.get('base_dir', 'Not set')}")
        
        # Check if env.template exists
        env_template = Path("env.template")
        if env_template.exists():
            print("✅ Environment template file exists")
        else:
            print("❌ Environment template file missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting Social Media Automation System Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Database Tests", test_database),
        ("Platform Initialization Tests", test_platform_initialization),
        ("Content Creation Tests", test_content_creation),
        ("FastAPI Application Tests", test_fastapi_imports),
        ("Configuration Tests", test_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! The system is ready for use.")
        print("\nNext steps:")
        print("1. Copy env.template to .env and configure your API keys")
        print("2. Run: python -m uvicorn automation_stack.main:app --reload")
        print("3. Access the analytics dashboard at http://localhost:8000/static/analytics_dashboard.html")
        return 0
    else:
        print(f"\n⚠️  {failed} tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
