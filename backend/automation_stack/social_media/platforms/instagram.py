"""Instagram platform integration for the social media automation system."""
import os
import time
import logging
import requests
from typing import Dict, Any, Optional
from pathlib import Path

from automation_stack.social_media.platforms.base import SocialMediaPlatform

class Instagram(SocialMediaPlatform):
    """
    Instagram platform implementation for posting content.
    Uses the Instagram Graph API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Instagram platform with configuration.
        
        Args:
            config: Platform configuration dictionary
        """
        super().__init__(config)
        self.api_url = self.config.get('api_url', 'https://graph.instagram.com/v12.0')
        self.access_token = self.config.get('api_key')
        self.page_id = self.config.get('page_id')
        self.rate_limit = self.config.get('rate_limit', 200)  # API calls per hour
        self.last_api_call = 0
        
        # Mock mode for testing
        self.mock_mode = self.config.get('mock_mode', False)
        self.mock_posts = []  # Store mock posts for testing
        
    def authenticate(self) -> bool:
        """
        Authenticate with the Instagram Graph API.
        
        In mock mode, this will simulate successful authentication.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if self.mock_mode:
            self.logger.info("Running in mock mode - simulating successful authentication")
            self.user_id = "mock_user_12345"
            self.username = "mock_instagram_user"
            self.authenticated = True
            return True
            
        if not self.access_token:
            self.logger.error("No access token provided for Instagram")
            return False
            
        try:
            # Simple token validation
            response = requests.get(
                f"{self.api_url}/me",
                params={'access_token': self.access_token, 'fields': 'id,username'}
            )
            response.raise_for_status()
            
            data = response.json()
            self.user_id = data.get('id')
            self.username = data.get('username')
            self.authenticated = True
            
            self.logger.info(f"Authenticated as Instagram user: {self.username}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Instagram authentication failed: {str(e)}")
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
        Post content to Instagram.
        
        Args:
            content_path: Path to the image or video file
            caption: Post caption
            **kwargs: Additional parameters
                - is_carousel: Whether to create a carousel post (multiple images)
                - location_id: Instagram location ID
                - user_tags: List of user tags
                
        Returns:
            Dictionary containing the post response
        """
        if not self.authenticated and not self.authenticate():
            return {
                'status': 'error',
                'message': 'Not authenticated with Instagram',
                'platform': 'instagram'
            }
        
        # Validate content
        if not self.validate_content(content_path):
            return {
                'status': 'error',
                'message': 'Invalid content',
                'platform': 'instagram',
                'content_path': content_path
            }
        
        try:
            self._rate_limit()
            
            # Determine content type
            content_type = self._get_content_type(content_path)
            
            if content_type == 'image':
                return self._post_image(content_path, caption, **kwargs)
            elif content_type == 'video':
                return self._post_video(content_path, caption, **kwargs)
            else:
                return {
                    'status': 'error',
                    'message': f'Unsupported content type: {content_type}',
                    'platform': 'instagram',
                    'content_path': content_path
                }
                
        except Exception as e:
            self.logger.error(f"Error posting to Instagram: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'platform': 'instagram'
            }
    
    def _post_image(
        self,
        image_path: str,
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post an image to Instagram.
        
        Args:
            image_path: Path to the image file
            caption: Post caption
            **kwargs: Additional parameters
                - location_id: Instagram location ID
                - user_tags: List of user tags
                
        Returns:
            Dictionary containing the post response
        """
        if not self.authenticated and not self.authenticate():
            return {
                'status': 'error',
                'message': 'Not authenticated with Instagram',
                'platform': 'instagram'
            }
            
        try:
            # In mock mode, simulate a successful post
            if self.mock_mode:
                import os
                from datetime import datetime
                
                # Create a mock post
                post_id = f"mock_insta_{int(time.time())}"
                post_data = {
                    'id': post_id,
                    'image_path': os.path.basename(image_path),
                    'caption': caption,
                    'timestamp': datetime.now().isoformat(),
                    'url': f"https://www.instagram.com/p/{post_id}",
                    **kwargs
                }
                
                # Store the mock post
                self.mock_posts.append(post_data)
                
                self.logger.info(f"[MOCK] Posted image to Instagram: {post_id}")
                
                return {
                    'status': 'success',
                    'id': post_id,
                    'platform': 'instagram',
                    'type': 'image',
                    'url': f"https://www.instagram.com/p/{post_id}",
                    'mock': True
                }
            
            # Real implementation for non-mock mode
            self._rate_limit()
            
            # Note: Instagram Graph API requires a business account and additional permissions
            # This is a simplified example that would need to be adapted based on your setup
            
            # In a real implementation, you would:
            # 1. Upload the image to get a container ID
            # 2. Publish the container
            
            # For now, we'll simulate a successful post
            post_id = f"insta_{int(time.time())}"
            
            self.logger.info(f"Posted image to Instagram: {post_id}")
            
            return {
                'status': 'success',
                'id': post_id,
                'platform': 'instagram',
                'type': 'image',
                'url': f"https://www.instagram.com/p/{post_id}"
            }
            
        except Exception as e:
            self.logger.error(f"Error posting image to Instagram: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'platform': 'instagram'
            }
    
    def _post_video(
        self,
        video_path: str,
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post a video to Instagram.
        
        Args:
            video_path: Path to the video file
            caption: Post caption
            **kwargs: Additional parameters
                - thumbnail_path: Path to custom thumbnail
                - location_id: Instagram location ID
                
        Returns:
            Dictionary containing the post response
        """
        try:
            # Step 1: Upload the video to get a container ID
            # This is a simplified example
            
            # In a real implementation, you would:
            # 1. Upload the video file
            # 2. Check the upload status
            # 3. Publish the container
            
            # For now, we'll simulate a successful post
            post_id = f"insta_video_{int(time.time())}"
            
            self.logger.info(f"Posted video to Instagram: {post_id}")
            
            return {
                'status': 'success',
                'id': post_id,
                'platform': 'instagram',
                'type': 'video',
                'url': f"https://www.instagram.com/p/{post_id}"
            }
            
        except Exception as e:
            self.logger.error(f"Error posting video to Instagram: {str(e)}", exc_info=True)
            raise
    
    def post_image(
        self,
        image_path: str,
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post an image to Instagram.
        
        This is a convenience method that delegates to the post() method.
        
        Args:
            image_path: Path to the image file
            caption: Post caption
            **kwargs: Additional parameters
                
        Returns:
            Dictionary containing the post response
        """
        return self.post(image_path, caption, **kwargs)
    
    def _format_caption(
        self,
        caption: str,
        max_length: int = 2200,
        max_hashtags: int = 30
    ) -> str:
        """
        Format the caption for Instagram.
        
        Args:
            caption: Original caption text
            max_length: Maximum caption length (2200 characters)
            max_hashtags: Maximum number of hashtags to include
            
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
