"""
Social media platform implementations.
"""
from automation_stack.social_media.platforms.base import SocialMediaPlatform
from automation_stack.social_media.platforms.instagram import Instagram
from automation_stack.social_media.platforms.facebook import Facebook
from automation_stack.social_media.platforms.twitter import Twitter
from automation_stack.social_media.platforms.tiktok import Tiktok

__all__ = [
    'SocialMediaPlatform',
    'Instagram',
    'Facebook',
    'Twitter',
    'Tiktok'
]
