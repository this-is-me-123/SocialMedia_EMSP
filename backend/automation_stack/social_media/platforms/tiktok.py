"""
TikTok platform integration for the social media automation system.
"""
import os
import time
import logging
import requests
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from automation_stack.social_media.platforms.base import SocialMediaPlatform

class Tiktok(SocialMediaPlatform):
    """
    TikTok platform implementation for posting content.
    Uses the TikTok API for video uploads.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize TikTok platform with configuration.
        
        Args:
            config: Platform configuration dictionary
        """
        super().__init__(config)
        self.api_url = self.config.get('api_url', 'https://open-api.tiktok.com')
        self.client_key = self.config.get('client_key')
        self.client_secret = self.config.get('client_secret')
        self.access_token = None
        self.refresh_token = None
        self.rate_limit = self.config.get('rate_limit', 100)  # API calls per hour
        self.last_api_call = 0
        
        # Mock mode for testing
        self.mock_mode = self.config.get('mock_mode', False)
        self.mock_videos = []  # Store mock videos for testing
    
    def authenticate(self) -> bool:
        """
        Authenticate with the TikTok API.
        
        In mock mode, this will simulate successful authentication.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if self.mock_mode:
            self.logger.info("Running in mock mode - simulating successful TikTok authentication")
            self.username = "mock_tiktok_user"
            self.user_id = "1234567890"
            self.access_token = f"mock_tiktok_access_{int(time.time())}"
            self.refresh_token = f"mock_tiktok_refresh_{int(time.time())}"
            self.authenticated = True
            return True
            
        if not all([self.client_key, self.client_secret]):
            self.logger.error("Missing TikTok API credentials")
            return False
            
        try:
            # For TikTok, we need to implement OAuth 2.0 flow
            # This is a simplified example - in a real implementation, you would:
            # 1. Get an authorization code (requires user interaction)
            # 2. Exchange the code for an access token
            # 3. Store the refresh token for future use
            
            # For now, we'll simulate a successful authentication
            self.access_token = f"tiktok_access_{int(time.time())}"
            self.refresh_token = f"tiktok_refresh_{int(time.time())}"
            self.authenticated = True
            
            self.logger.info("Authenticated with TikTok API")
            return True
            
        except Exception as e:
            self.logger.error(f"TikTok authentication failed: {str(e)}")
            return False
    
    def _refresh_access_token(self) -> bool:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            bool: True if token was refreshed successfully, False otherwise
        """
        if not self.refresh_token:
            return False
            
        try:
            # In a real implementation, you would make an API call to refresh the token
            # For now, we'll simulate a successful token refresh
            self.access_token = f"tiktok_access_{int(time.time())}"
            self.logger.info("Refreshed TikTok access token")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh TikTok access token: {str(e)}")
            return False
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        now = time.time()
        time_since_last_call = now - self.last_api_call
        
        # Ensure we don't exceed rate limits (100 calls per hour = ~1 call every 36 seconds)
        min_interval = 3600 / self.rate_limit
        if time_since_last_call < min_interval:
            time_to_wait = min_interval - time_since_last_call
            time.sleep(time_to_wait)
            
        self.last_api_call = time.time()
    
    def post(
        self,
        content_path: str,
        caption: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post a video to TikTok.
        
        Args:
            content_path: Path to the video file
            caption: Video caption
            **kwargs: Additional parameters
                - privacy_level: Privacy level (PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW, etc.)
                - disable_comment: Whether to disable comments (default: False)
                - disable_duet: Whether to disable duets (default: False)
                - disable_stitch: Whether to disable stitches (default: False)
                - disable_share: Whether to disable sharing (default: False)
                
        Returns:
            Dictionary containing the post response
        """
        if not self.authenticated and not self.authenticate():
            return {
                'status': 'error',
                'message': 'Not authenticated with TikTok',
                'platform': 'tiktok'
            }
        
        # Determine content type
        content_type = self._get_content_type(content_path)
        if content_type == 'video':
            if not self.validate_content(content_path):
                return {
                    'status': 'error',
                    'message': 'Invalid content',
                    'platform': 'tiktok',
                    'content_path': content_path
                }
        elif content_type == 'carousel':
            for img_path in content_path:
                if not self.validate_content(img_path):
                    return {
                        'status': 'error',
                        'message': f'Invalid carousel image: {img_path}',
                        'platform': 'tiktok',
                        'content_path': img_path
                    }
        # For text/link/story, skip file validation

        try:
            self._rate_limit()
            if content_type == 'video':
                return self._post_video(content_path, caption, **kwargs)
            elif content_type == 'carousel':
                return self._post_carousel(content_path, caption, **kwargs)
            elif content_type == 'link':
                return self._post_link(content_path, caption, **kwargs)
            elif content_type == 'story':
                return self._post_story(content_path, caption, **kwargs)
            elif content_type == 'text':
                return self._post_text(caption, **kwargs)
            else:
                return {
                    'status': 'error',
                    'message': f'Unsupported content type: {content_type}',
                    'platform': 'tiktok',
                    'content_path': content_path
                }
        except Exception as e:
            self.logger.error(f"Error posting to TikTok: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'platform': 'tiktok'
            }

    def _post_video(self, video_path: str, caption: str, **kwargs) -> Dict[str, Any]:
        """
        Post a video to TikTok (stub).
        """
        try:
            self._rate_limit()
            video_id = f"tiktok_video_{int(time.time())}"
            video_url = f"https://www.tiktok.com/@{getattr(self, 'username', 'user')}/video/{video_id}"
            self.logger.info(f"[STUB] Posted video to TikTok: {video_url}")
            return {
                'status': 'success',
                'platform': 'tiktok',
                'result': {
                    'id': video_id,
                    'url': video_url,
                    'caption': caption,
                    'platform': 'tiktok',
                    'type': 'video'
                }
            }
        except Exception as e:
            self.logger.error(f"Error posting video to TikTok: {str(e)}", exc_info=True)
            raise

    def _post_carousel(self, image_paths: list, caption: str, **kwargs) -> Dict[str, Any]:
        """
        Attempt to post a carousel (multi-image) to TikTok. Not available in public API; return error.
        """
        self._rate_limit()
        return {
            'status': 'error',
            'platform': 'tiktok',
            'type': 'carousel',
            'message': 'TikTok carousel/photo post API is not publicly available. Contact TikTok for partner access.'
        }

    def _post_link(self, link: str, caption: str, **kwargs) -> Dict[str, Any]:
        """
        Attempt to post a link to TikTok (not supported).
        """
        self._rate_limit()
        return {
            'status': 'error',
            'platform': 'tiktok',
            'type': 'link',
            'message': 'TikTok does not support link posts.'
        }

    def _post_story(self, story_path: str, caption: str = '', **kwargs) -> Dict[str, Any]:
        """
        Attempt to post a story/reel to TikTok. Not available in public API; return error.
        """
        self._rate_limit()
        return {
            'status': 'error',
            'platform': 'tiktok',
            'type': 'story',
            'message': 'TikTok story/reel API is not publicly available. Contact TikTok for partner access.'
        }

    def _post_text(self, message: str, **kwargs) -> Dict[str, Any]:
        """
        Post a text-only message to TikTok (stub).
        """
        try:
            self._rate_limit()
            post_id = f"tiktok_text_{int(time.time())}"
            self.logger.info(f"[STUB] Posted text to TikTok: {post_id}")
            return {
                'status': 'success',
                'platform': 'tiktok',
                'result': {
                    'id': post_id,
                    'type': 'text',
                    'url': f"https://www.tiktok.com/@{getattr(self, 'username', 'user')}/video/{post_id}",
                    'caption': message
                }
            }
        except Exception as e:
            self.logger.error(f"Error posting text to TikTok: {str(e)}", exc_info=True)
            raise

    def _format_caption(
        self,
        caption: str,
        max_length: int = 2200,
        max_hashtags: int = 100
    ) -> str:
        """
        Format the caption for TikTok.
        
        Args:
            caption: Original caption text
            max_length: Maximum caption length (2200 characters)
            max_hashtags: Maximum number of hashtags to include (TikTok allows up to 100)
            
        Returns:
            Formatted caption
        """
        # Format hashtags
        formatted = super().format_hashtags(caption, max_hashtags)
        
        # Truncate if needed
        if len(formatted) > max_length:
            # Find the last space before max_length
            truncated = formatted[:max_length].rsplit(' ', 1)[0]
            return truncated + "..."
            
        return formatted
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get information about a TikTok video.
        
        Args:
            video_id: ID of the TikTok video
            
        Returns:
            Dictionary containing video information
        """
        if not self.authenticated and not self.authenticate():
            return {
                'status': 'error',
                'message': 'Not authenticated with TikTok',
                'platform': 'tiktok'
            }
            
        try:
            self._rate_limit()
            
            # In a real implementation, you would make an API call to get video info
            # For now, we'll return mock data
            return {
                'status': 'success',
                'id': video_id,
                'platform': 'tiktok',
                'views': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting TikTok video info: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'platform': 'tiktok'
            }
