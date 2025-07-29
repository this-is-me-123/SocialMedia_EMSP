"""
Social media automation package for managing posts across multiple platforms.
"""
from .manager import SocialMediaManager
from .platforms import (
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
