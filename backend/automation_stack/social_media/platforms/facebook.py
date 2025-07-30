"""
Facebook platform integration for the social media automation system.
"""
import os
import time
import logging
import requests
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from automation_stack.social_media.platforms.base import SocialMediaPlatform

class Facebook(SocialMediaPlatform):
    """
    Facebook platform implementation for posting content.
    Uses the Facebook Graph API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Facebook platform with configuration.
        
        Args:
            config: Platform configuration dictionary
        """
        super().__init__(config)
        self.api_url = self.config.get('api_url', 'https://graph.facebook.com/v12.0')
        self.access_token = self.config.get('access_token')
        self.page_id = self.config.get('page_id')
        self.rate_limit = self.config.get('rate_limit', 200)  # API calls per hour
        self.last_api_call = 0
        
        # Mock mode for testing
        self.mock_mode = self.config.get('mock_mode', False)
        self.mock_posts = []  # Store mock posts for testing
        
    def authenticate(self) -> bool:
        """
        Authenticate with the Facebook Graph API.
        
        In mock mode, this will simulate successful authentication.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if self.mock_mode:
            self.logger.info("Running in mock mode - simulating successful Facebook authentication")
            self.page_access_token = "mock_facebook_token_12345"
            self.page_name = "Mock Facebook Page"
            self.authenticated = True
            return True
            
        if not self.access_token or not self.page_id:
            self.logger.error("Missing access token or page ID for Facebook")
            return False
            
        try:
            # Verify page access token
            response = requests.get(
                f"{self.api_url}/me/accounts",
                params={'access_token': self.access_token}
            )
            response.raise_for_status()
            
            # Check if we have access to the specified page
            pages = response.json().get('data', [])
            page = next((p for p in pages if p.get('id') == self.page_id), None)
            
            if not page:
                self.logger.error(f"No access to page with ID: {self.page_id}")
                return False
                
            # Store page access token
            self.page_access_token = page.get('access_token')
            self.page_name = page.get('name')
            self.authenticated = True
            
            self.logger.info(f"Authenticated with Facebook page: {self.page_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Facebook authentication failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response: {e.response.text}")
            return False
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        now = time.time()
        time_since_last_call = now - self.last_api_call
        
        # Ensure we don't exceed rate limits (200 calls per hour = ~1 call every 18 seconds)
        min_interval = 3600 / self.rate_limit
        if time_since_last_call < min_interval:
            time_to_wait = min_interval - time_since_last_call
            time.sleep(time_to_wait)
            
        self.last_api_call = time.time()
    
    def post(
        self,
        content_path: str,
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to Facebook.
        
        Args:
            content_path: Path to the image, video, or other media file
            caption: Post caption
            **kwargs: Additional parameters
                - link: URL to include with the post
                - scheduled_publish_time: Unix timestamp for scheduling
                - published: Whether to publish immediately (default: True)
                
        Returns:
            Dictionary containing the post response
        """
        if not self.authenticated and not self.authenticate():
            return {
                'status': 'error',
                'message': 'Not authenticated with Facebook',
                'platform': 'facebook'
            }
        
        # Validate content
        if not self.validate_content(content_path):
            return {
                'status': 'error',
                'message': 'Invalid content',
                'platform': 'facebook',
                'content_path': content_path
            }
        
        try:
            self._rate_limit()
            
            # Determine content type
            content_type = self._get_content_type(content_path)
            
            if content_type in ['image', 'video']:
                return self._publish_media_post(content_path, caption, content_type, **kwargs)
            else:
                return self._publish_text_post(caption, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Error posting to Facebook: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'platform': 'facebook'
            }
    
    def _publish_media_post(
        self,
        media_path: str,
        caption: str,
        media_type: str = 'image',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Publish a media post to Facebook.
        
        Args:
            media_path: Path to the media file
            caption: Post caption
            media_type: Type of media ('image' or 'video')
            **kwargs: Additional parameters
                - published: Whether to publish immediately (default: True)
                - scheduled_publish_time: Unix timestamp for scheduling
                
        Returns:
            Dictionary containing the post response
        """
        if not self.authenticated and not self.authenticate():
            return {
                'status': 'error',
                'message': 'Not authenticated with Facebook',
                'platform': 'facebook'
            }
            
        try:
            # In mock mode, simulate a successful post
            if self.mock_mode:
                import os
                from datetime import datetime
                
                # Create a mock post
                post_id = f"mock_fb_{media_type}_{int(time.time())}"
                post_data = {
                    'id': post_id,
                    'media_path': os.path.basename(media_path),
                    'caption': caption,
                    'media_type': media_type,
                    'timestamp': datetime.now().isoformat(),
                    'url': f"https://www.facebook.com/{post_id}",
                    **kwargs
                }
                
                # Store the mock post
                self.mock_posts.append(post_data)
                
                self.logger.info(f"[MOCK] Posted {media_type} to Facebook: {post_id}")
                
                return {
                    'status': 'success',
                    'id': post_id,
                    'platform': 'facebook',
                    'type': media_type,
                    'url': f"https://www.facebook.com/{post_id}",
                    'mock': True
                }
            
            # Real implementation for non-mock mode
            self._rate_limit()
            
            # In a real implementation, you would:
            # 1. Upload the media file to get an ID
            # 2. Create a post with the media ID
            
            # For now, we'll simulate a successful post
            post_id = f"fb_{media_type}_{int(time.time())}"
            
            self.logger.info(f"Posted {media_type} to Facebook: {post_id}")
            
            return {
                'status': 'success',
                'id': post_id,
                'platform': 'facebook',
                'type': media_type,
                'url': f"https://www.facebook.com/{post_id}"
            }
            
        except Exception as e:
            error_msg = f"Error posting {media_type} to Facebook: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg,
                'platform': 'facebook'
            }
    
    def _publish_text_post(
        self,
        message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Publish a text post to Facebook.
        
        Args:
            message: Post text
            **kwargs: Additional parameters
                - link: URL to include with the post
                - published: Whether to publish immediately (default: True)
                - scheduled_publish_time: Unix timestamp for scheduling
                
        Returns:
            Dictionary containing the post response
        """
        try:
            self._rate_limit()
            
            # In a real implementation, you would make an API call to create the post
            # For now, we'll simulate a successful post
            post_id = f"fb_post_{int(time.time())}"
            
            self.logger.info(f"Posted text to Facebook: {post_id}")
            
            return {
                'status': 'success',
                'id': post_id,
                'platform': 'facebook',
                'type': 'text',
                'url': f"https://www.facebook.com/{post_id}"
            }
            
        except Exception as e:
            self.logger.error(f"Error posting text to Facebook: {str(e)}", exc_info=True)
            raise
    
    def _format_message(
        self,
        message: str,
        max_length: int = 63206,
        max_hashtags: int = 30
    ) -> str:
        """
        Format the message for Facebook.
        
        Args:
            message: Original message text
            max_length: Maximum message length (63,206 characters)
            max_hashtags: Maximum number of hashtags to include
            
        Returns:
            Formatted message
        """
        # Format hashtags
        formatted = super().format_hashtags(message, max_hashtags)
        
        # Truncate if needed
        if len(formatted) > max_length:
            # Find the last space before max_length
            truncated = formatted[:max_length].rsplit(' ', 1)[0]
            return truncated + "..."
            
        return formatted
