"""
Social media automation package for managing posts across multiple platforms.
"""
from automation_stack.social_media.manager import SocialMediaManager
from automation_stack.social_media.platforms import (
    SocialMediaPlatform,
    Instagram,
    Facebook,
    Twitter,
    Tiktok
)

__all__ = [
    'SocialMediaManager',
    'SocialMediaPlatform',
    'Instagram',
    'Facebook',
    'Twitter',
    'Tiktok'
]
