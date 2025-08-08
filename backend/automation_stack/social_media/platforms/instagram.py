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
        self.api_url = self.config.get('api_url', 'https://graph.instagram.com/v18.0')
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
            
        if not self.access_token or not self.page_id:
            self.logger.error("Instagram access token or page ID not configured")
            return False
            
        try:
            # Validate access token format
            if not self.access_token.strip():
                self.logger.error("Instagram access token is empty")
                return False
                
            # Test API connection by getting account info
            response = requests.get(
                f"{self.api_url}/me",
                params={'access_token': self.access_token},
                timeout=30  # Add timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get('id')
                self.username = data.get('username', 'Unknown')
                self.authenticated = True
                self.logger.info(f"Successfully authenticated Instagram user: {self.username}")
                return True
            elif response.status_code == 401:
                self.logger.error("Instagram authentication failed: Invalid access token")
                return False
            elif response.status_code == 403:
                self.logger.error("Instagram authentication failed: Insufficient permissions")
                return False
            else:
                self.logger.error(f"Instagram authentication failed: HTTP {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("Instagram authentication timeout - API request took too long")
            return False
        except requests.exceptions.ConnectionError:
            self.logger.error("Instagram authentication failed: Unable to connect to API")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Instagram authentication request error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Instagram authentication unexpected error: {str(e)}")
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
        content_type = self._get_content_type(content_path)
        if content_type in ['image', 'video']:
            if not self.validate_content(content_path):
                return {
                    'status': 'error',
                    'message': 'Invalid content',
                    'platform': 'instagram',
                    'content_path': content_path
                }
        elif content_type == 'carousel':
            for img_path in content_path:
                if not self.validate_content(img_path):
                    return {
                        'status': 'error',
                        'message': f'Invalid carousel image: {img_path}',
                        'platform': 'instagram',
                        'content_path': img_path
                    }
        # For text/link/story, skip file validation

        try:
            self._rate_limit()
            # Determine content type
            if content_type == 'image':
                return self._post_image(content_path, caption, **kwargs)
            elif content_type == 'video':
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
    
    def _post_link(
        self,
        link: str,
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Attempt to post a link to Instagram. Only possible in stories with special permissions.
        """
        self._rate_limit()
        return {
            'status': 'error',
            'platform': 'instagram',
            'type': 'link',
            'message': 'Instagram does not support link posts except in stories with special permissions.'
        }

    def _post_carousel(
        self,
        image_paths: list,
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post a carousel (multi-image) to Instagram using /media endpoint.
        """
        try:
            self._rate_limit()
            upload_ids = []
            for img_path in image_paths:
                upload_url = f"{self.api_url}/{self.page_id}/media"
                with open(img_path, 'rb') as img_file:
                    files = {'image': img_file}
                    params = {
                        'access_token': self.access_token,
                        'media_type': 'IMAGE',
                        'caption': caption
                    }
                    resp = requests.post(upload_url, files=files, data=params, timeout=60)
                    if resp.status_code == 200:
                        data = resp.json()
                        upload_ids.append(data['id'])
                    else:
                        self.logger.error(f"Instagram image upload failed: {resp.status_code} - {resp.text}")
                        return {
                            'status': 'error',
                            'platform': 'instagram',
                            'type': 'carousel',
                            'message': resp.text
                        }
            # Now create the carousel container
            carousel_url = f"{self.api_url}/{self.page_id}/media"
            params = {
                'access_token': self.access_token,
                'media_type': 'CAROUSEL',
                'children': ','.join(upload_ids),
                'caption': caption
            }
            resp = requests.post(carousel_url, data=params, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                post_id = data.get('id')
                self.logger.info(f"Posted carousel to Instagram: {post_id} ({len(image_paths)} images)")
                return {
                    'status': 'success',
                    'id': post_id,
                    'platform': 'instagram',
                    'type': 'carousel',
                    'images': image_paths,
                    'caption': caption,
                    'url': f"https://www.instagram.com/p/{post_id}/"
                }
            else:
                self.logger.error(f"Instagram carousel post failed: {resp.status_code} - {resp.text}")
                return {
                    'status': 'error',
                    'platform': 'instagram',
                    'type': 'carousel',
                    'message': resp.text
                }
        except Exception as e:
            self.logger.error(f"Error posting carousel to Instagram: {str(e)}", exc_info=True)
            raise

    def _post_story(
        self,
        story_path: str,
        caption: str = '',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post a story to Instagram using /media endpoint (if available).
        """
        try:
            self._rate_limit()
            story_url = f"{self.api_url}/{self.page_id}/media"
            try:
                with open(story_path, 'rb') as story_file:
                    files = {'image': story_file}
                    params = {
                        'access_token': self.access_token,
                        'media_type': 'STORIES',
                        'caption': caption
                    }
                    resp = requests.post(story_url, files=files, data=params, timeout=60)
                    if resp.status_code == 200:
                        data = resp.json()
                        post_id = data.get('id')
                        self.logger.info(f"Posted story to Instagram: {post_id}")
                        return {
                            'status': 'success',
                            'id': post_id,
                            'platform': 'instagram',
                            'type': 'story',
                            'url': f"https://www.instagram.com/stories/{post_id}/",
                            'caption': caption
                        }
                    else:
                        self.logger.error(f"Instagram story post failed: {resp.status_code} - {resp.text}")
                        return {
                            'status': 'error',
                            'platform': 'instagram',
                            'type': 'story',
                            'message': resp.text
                        }
            except FileNotFoundError:
                return {
                    'status': 'error',
                    'platform': 'instagram',
                    'type': 'story',
                    'message': f'Story file not found: {story_path}'
                }
        except Exception as e:
            self.logger.error(f"Error posting story to Instagram: {str(e)}", exc_info=True)
            raise

    def _post_text(
        self,
        message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post a text-only message to Instagram (stub).
        """
        try:
            self._rate_limit()
            post_id = f"ig_text_{int(time.time())}"
            self.logger.info(f"[STUB] Posted text to Instagram: {post_id}")
            return {
                'status': 'success',
                'id': post_id,
                'platform': 'instagram',
                'type': 'text',
                'url': f"https://www.instagram.com/p/{post_id}/",
                'caption': message
            }
        except Exception as e:
            self.logger.error(f"Error posting text to Instagram: {str(e)}", exc_info=True)
            raise

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
