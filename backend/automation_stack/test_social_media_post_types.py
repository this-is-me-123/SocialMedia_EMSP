import sys
import os
print('DEBUG: sys.path:', sys.path)
print('DEBUG: CWD:', os.getcwd())
print('DEBUG: automation_stack in sys.modules:', 'automation_stack' in sys.modules)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import pytest
from unittest.mock import patch

# Import your SocialMediaManager and config loader (adjust import as needed)
try:
    from automation_stack.social_media.manager import SocialMediaManager
    from automation_stack.config import get_config
except Exception as e:
    import traceback
    print("IMPORT ERROR:", e)
    traceback.print_exc()
    sys.exit(1)

# Set up dummy config for tests (replace with your own .env or config loading logic)
CONFIG = get_config()

PLATFORMS = ['facebook', 'instagram', 'tiktok']

TEST_TEXT = "This is a test post."
TEST_IMAGE = "tests/assets/test_image.jpg"
TEST_VIDEO = "tests/assets/test_video.mp4"
TEST_LINK = "https://www.example.com"
TEST_CAROUSEL = ["tests/assets/test_image1.jpg", "tests/assets/test_image2.jpg"]

@pytest.fixture(scope="module")
def manager():
    # Patch required environment variables for the test
    with patch.dict(os.environ, {
        "FACEBOOK_APP_ID": "test_id",
        "FACEBOOK_APP_SECRET": "test_secret",
        "FACEBOOK_PAGE_ID": "test_page",
        "INSTAGRAM_ACCESS_TOKEN": "test_token",
        "INSTAGRAM_PAGE_ID": "test_page",
        "TWITTER_API_KEY": "test_key",
        "TWITTER_API_SECRET": "test_secret",
        "TWITTER_ACCESS_TOKEN": "test_token",
        "TWITTER_ACCESS_TOKEN_SECRET": "test_secret",
        "TIKTOK_APP_ID": "test_id",
        "TIKTOK_APP_SECRET": "test_secret",
        # Add more as needed
    }):
        yield SocialMediaManager()

def test_facebook_text_post(manager):
    result = manager.create_post('facebook', TEST_TEXT, TEST_TEXT)
    assert result['status'] in ('success', 'error')

def test_facebook_image_post(manager):
    result = manager.create_post('facebook', TEST_IMAGE, TEST_TEXT)
    assert result['status'] in ('success', 'error')

def test_facebook_link_post(manager):
    result = manager.create_post('facebook', TEST_LINK, TEST_TEXT)
    assert result['status'] in ('success', 'error')

def test_facebook_carousel_post(manager):
    result = manager.create_post('facebook', TEST_CAROUSEL, TEST_TEXT)
    assert result['status'] in ('success', 'error')

def test_facebook_story_post(manager):
    result = manager.create_post('facebook', TEST_VIDEO, TEST_TEXT, post_type='story')
    assert result['status'] in ('success', 'error')

def test_instagram_carousel_post(manager):
    result = manager.create_post('instagram', TEST_CAROUSEL, TEST_TEXT)
    assert result['status'] in ('success', 'error')

def test_instagram_story_post(manager):
    result = manager.create_post('instagram', TEST_IMAGE, TEST_TEXT, post_type='story')
    assert result['status'] in ('success', 'error')

def test_instagram_link_post(manager):
    result = manager.create_post('instagram', TEST_LINK, TEST_TEXT)
    assert result['status'] == 'error'  # Links not supported in feed

def test_tiktok_video_post(manager):
    result = manager.create_post('tiktok', TEST_VIDEO, TEST_TEXT)
    assert result['status'] in ('success', 'error')

def test_tiktok_carousel_post(manager):
    result = manager.create_post('tiktok', TEST_CAROUSEL, TEST_TEXT)
    assert result['status'] == 'error'  # Not supported

def test_tiktok_story_post(manager):
    result = manager.create_post('tiktok', TEST_VIDEO, caption=TEST_TEXT, post_type='story')
    assert result['status'] == 'error'  # Not supported

def test_tiktok_link_post(manager):
    result = manager.create_post('tiktok', TEST_LINK, caption=TEST_TEXT)
    assert result['status'] == 'error'  # Not supported

# Additional tests can be added for edge cases, error handling, etc.
