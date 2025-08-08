"""
Configuration module for the social media automation system.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Content settings
CONTENT = {
    'output_dir': str(BASE_DIR / 'generated_content'),
    'image_size': (1080, 1080),  # Instagram square format
    'font_path': str(BASE_DIR / 'assets/fonts/arial.ttf'),
    'brand_colors': ['#003366', '#0066CC', '#0099FF'],  # Dark to light blue
    'audio_dir': str(BASE_DIR / 'assets/audio'),
    'default_font_size': 40,
    'text_margin': 50,
    'text_color': '#FFFFFF',
    'text_max_width': 30  # Characters per line
}

# Platform settings
PLATFORMS = {
    'instagram': {
        'enabled': True,
        'api_key': os.getenv('INSTAGRAM_ACCESS_TOKEN'),
        'page_id': os.getenv('INSTAGRAM_PAGE_ID'),
        'api_url': 'https://graph.instagram.com/v12.0',
        'rate_limit': 200  # API calls per hour
    },
    'facebook': {
        'enabled': True,
        'app_id': os.getenv('FACEBOOK_APP_ID'),
        'app_secret': os.getenv('FACEBOOK_APP_SECRET'),
        'page_id': os.getenv('FACEBOOK_PAGE_ID'),
        'api_url': 'https://graph.facebook.com/v12.0',
        'rate_limit': 200
    },
    'twitter': {
        'enabled': True,
        'api_key': os.getenv('TWITTER_API_KEY'),
        'api_secret': os.getenv('TWITTER_API_SECRET'),
        'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
        'access_secret': lambda: os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
        'api_url': 'https://api.twitter.com/1.1',
        'rate_limit': 300
    },
    'tiktok': {
        'enabled': True,
        'app_id': os.getenv('TIKTOK_APP_ID'),
        'app_secret': os.getenv('TIKTOK_APP_SECRET'),
        'api_url': 'https://open-api.tiktok.com',
        'rate_limit': 100
    }
}

# Posting schedule
SCHEDULE = {
    'default_post_time': '09:00',
    'timezone': 'America/New_York',
    'platforms': {
        'instagram': ['09:00', '12:00', '15:00'],
        'facebook': ['10:00', '14:00', '18:00'],
        'twitter': ['08:00', '12:00', '16:00', '20:00'],
        'tiktok': ['11:00', '15:00', '19:00']
    },
    'max_posts_per_day': 3,
    'content_rotation_days': 30
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'social_media_automation.log'),
            'formatter': 'standard',
            'level': 'DEBUG'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

# Validation
for platform, config in PLATFORMS.items():
    if config.get('enabled') and not all(config.values()):
        print(f"Warning: Missing configuration for {platform}")

# Create output directories
os.makedirs(CONTENT['output_dir'], exist_ok=True)
os.makedirs(CONTENT['audio_dir'], exist_ok=True)

# Provide a get_config() function for compatibility with code expecting it

def get_config():
    """
    Return all major config constants as a dictionary. Used for backward compatibility.
    """
    return {
        "CONTENT": CONTENT,
        "PLATFORMS": PLATFORMS,
        "SCHEDULE": SCHEDULE,
        "LOGGING": LOGGING,
    }
