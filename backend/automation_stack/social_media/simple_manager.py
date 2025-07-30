"""
A simplified version of the SocialMediaManager for testing.
"""
import logging
from typing import Dict, Any, Optional

class SimpleSocialMediaManager:
    """A simplified social media manager for testing purposes."""
    
    def __init__(self):
        """Initialize the simple manager."""
        self.platforms = {}
        self.logger = logging.getLogger('simple_manager')
    
    def register_platform(self, name: str, platform: Any) -> None:
        """
        Register a platform with the manager.
        
        Args:
            name: Name of the platform
            platform: Platform instance
        """
        self.platforms[name.lower()] = platform
        self.logger.info(f"Registered platform: {name}")
    
    def post_to_platform(
        self,
        platform_name: str,
        content_path: str,
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to a specific platform.
        
        Args:
            platform_name: Name of the platform to post to
            content_path: Path to the content file
            caption: Caption for the post
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Dictionary with the result of the post operation
        """
        platform_name = platform_name.lower()
        
        if platform_name not in self.platforms:
            error_msg = f"Platform not registered: {platform_name}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'platform': platform_name
            }
        
        platform = self.platforms[platform_name]
        
        try:
            # Authenticate if not already authenticated
            if not getattr(platform, 'authenticated', False):
                if not platform.authenticate():
                    return {
                        'status': 'error',
                        'message': 'Authentication failed',
                        'platform': platform_name
                    }
            
            # Post the content
            result = platform.post_image(
                image_path=content_path,
                caption=caption,
                **kwargs
            )
            
            return {
                'status': 'success',
                'message': 'Post successful',
                'platform': platform_name,
                'result': result
            }
            
        except Exception as e:
            self.logger.error(f"Error posting to {platform_name}: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'platform': platform_name
            }
