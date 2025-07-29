"""Configuration settings for the social media automation system."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'social_media_automation.log')

# Platform configurations
PLATFORMS = {
    'instagram': {
        'enabled': os.getenv('INSTAGRAM_ENABLED', 'false').lower() == 'true',
        'username': os.getenv('INSTAGRAM_USERNAME', ''),
        'password': os.getenv('INSTAGRAM_PASSWORD', ''),
        'api_key': os.getenv('INSTAGRAM_API_KEY', ''),
        'api_secret': os.getenv('INSTAGRAM_API_SECRET', ''),
        'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', ''),
        'page_id': os.getenv('INSTAGRAM_PAGE_ID', ''),
        'rate_limit': int(os.getenv('INSTAGRAM_RATE_LIMIT', '200')),  # API calls per hour
    },
    'facebook': {
        'enabled': os.getenv('FACEBOOK_ENABLED', 'false').lower() == 'true',
        'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', ''),
        'page_id': os.getenv('FACEBOOK_PAGE_ID', ''),
    },
    'twitter': {
        'enabled': os.getenv('TWITTER_ENABLED', 'false').lower() == 'true',
        'api_key': os.getenv('TWITTER_API_KEY', ''),
        'api_secret': os.getenv('TWITTER_API_SECRET', ''),
        'access_token': os.getenv('TWITTER_ACCESS_TOKEN', ''),
        'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET', ''),
    },
    'tiktok': {
        'enabled': os.getenv('TIKTOK_ENABLED', 'false').lower() == 'true',
        'username': os.getenv('TIKTOK_USERNAME', ''),
        'password': os.getenv('TIKTOK_PASSWORD', ''),
        'api_key': os.getenv('TIKTOK_API_KEY', ''),
    },
}

# Default schedule for posting
SCHEDULE = {
    'timezone': os.getenv('TIMEZONE', 'UTC'),
    'default_posting_times': [
        '09:00',  # Morning
        '12:00',  # Noon
        '15:00',  # Afternoon
        '18:00',  # Evening
    ],
    'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
}

# Content settings
CONTENT = {
    'base_dir': os.getenv('CONTENT_DIR', str(BASE_DIR / 'content')),
    'image_formats': ['.jpg', '.jpeg', '.png', '.gif'],
    'video_formats': ['.mp4', '.mov'],
    'max_caption_length': 2200,  # Instagram's limit
    'max_hashtags': 30,
}

# Test settings (used in test environment)
TESTING = os.getenv('TESTING', 'false').lower() == 'true'
if TESTING:
    # Override settings for testing
    for platform in PLATFORMS.values():
        platform['enabled'] = True
        platform['dry_run'] = True
    
    CONTENT['base_dir'] = str(BASE_DIR / 'test_output')
    LOG_LEVEL = 'DEBUG'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'standard'
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
}
