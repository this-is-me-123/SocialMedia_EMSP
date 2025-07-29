"""Test configuration and constants."""
import os
from pathlib import Path

# Test directories
TEST_DIR = Path(__file__).parent
FIXTURES_DIR = TEST_DIR / "fixtures"
TEST_DATA_DIR = TEST_DIR / "test_data"

# Ensure test directories exist
for directory in [FIXTURES_DIR, TEST_DATA_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# Test database
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

# Mock API responses
MOCK_RESPONSES = {
    "instagram": {
        "success": {
            "status": "success",
            "post_id": "insta_12345",
            "url": "https://instagram.com/p/insta_12345"
        },
        "error": {
            "error": {
                "message": "Invalid media URL",
                "type": "OAuthException",
                "code": 100,
                "error_subcode": 2207008,
                "fbtrace_id": "A123456789"
            }
        }
    },
    "facebook": {
        "success": {
            "id": "12345_67890",
            "post_id": "12345_67890"
        },
        "error": {
            "error": {
                "message": "Invalid parameter",
                "type": "OAuthException",
                "code": 100,
                "error_subcode": 1234567,
                "fbtrace_id": "ABC123"
            }
        }
    },
    "twitter": {
        "success": {
            "data": {
                "id": "1234567890123456789",
                "text": "Test tweet"
            }
        },
        "error": {
            "errors": [
                {
                    "code": 187,
                    "message": "Status is a duplicate."
                }
            ]
        }
    },
    "tiktok": {
        "success": {
            "code": 0,
            "data": {
                "publish_id": "1234567890123456789",
                "status": "success"
            }
        },
        "error": {
            "code": 40001,
            "message": "Invalid access token"
        }
    }
}

# Test media files
TEST_IMAGE_PATH = FIXTURES_DIR / "test_image.jpg"
TEST_VIDEO_PATH = FIXTURES_DIR / "test_video.mp4"

# Create placeholder test files if they don't exist
if not TEST_IMAGE_PATH.exists():
    with open(TEST_IMAGE_PATH, "wb") as f:
        f.write(b"FAKE_IMAGE_DATA")

if not TEST_VIDEO_PATH.exists():
    with open(TEST_VIDEO_PATH, "wb") as f:
        f.write(b"FAKE_VIDEO_DATA")

# Test user credentials
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

# Test post data
TEST_POST = {
    "platform": "instagram",
    "content": "Test post content",
    "scheduled_time": "2023-01-01T12:00:00Z",
    "media_urls": ["https://example.com/image.jpg"],
    "metadata": {
        "hashtags": ["test", "integration"],
        "location": "Test Location"
    }
}

# Test configuration
TEST_CONFIG = {
    "database": {
        "url": TEST_DATABASE_URL,
        "echo": False,
        "pool_pre_ping": True
    },
    "storage": {
        "path": str(TEST_DATA_DIR),
        "max_size_mb": 100
    },
    "api": {
        "port": 8000,
        "debug": True,
        "reload": False
    },
    "logging": {
        "level": "INFO",
        "file": "test.log"
    }
}
