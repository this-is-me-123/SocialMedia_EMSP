"""
Base class for all social media platform integrations.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path

class SocialMediaPlatform(ABC):
    """Abstract base class for social media platform integrations."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the platform with configuration.
        
        Args:
            config: Platform-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.authenticated = False
        self.dry_run = config.get('dry_run', False)
        
        # Set up rate limiting
        self.rate_limit = config.get('rate_limit', 10)  # Default: 10 requests per minute
        self.last_request_time = 0
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform's API.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def post_image(
        self,
        image_path: str,
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post an image to the platform.
        
        Args:
            image_path: Path to the image file
            caption: Caption text for the post
            **kwargs: Platform-specific parameters
            
        Returns:
            Dictionary containing the post response
        """
        pass
    
    def validate_image(self, image_path: str) -> bool:
        """
        Validate that an image file exists and is in a supported format.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            bool: True if the image is valid, False otherwise
        """
        if not Path(image_path).exists():
            self.logger.error(f"Image file not found: {image_path}")
            return False
            
        # Check file extension
        valid_extensions = {'.jpg', '.jpeg', '.png'}
        if Path(image_path).suffix.lower() not in valid_extensions:
            self.logger.error(f"Unsupported image format. Must be one of: {', '.join(valid_extensions)}")
            return False
            
        return True
    
    def format_caption(
        self,
        caption: str,
        max_length: int = 2200,
        max_hashtags: int = 30
    ) -> str:
        """
        Format a caption for the platform.
        
        Args:
            caption: Original caption text
            max_length: Maximum length of the caption
            max_hashtags: Maximum number of hashtags to include
            
        Returns:
            Formatted caption
        """
        # Extract hashtags
        words = caption.split()
        hashtags = [word for word in words if word.startswith('#')]
        
        # Limit number of hashtags
        if len(hashtags) > max_hashtags:
            hashtags = hashtags[:max_hashtags]
            self.logger.warning(f"Reduced number of hashtags to {max_hashtags}")
        
        # Remove hashtags from the main text
        text = ' '.join(word for word in words if not word.startswith('#'))
        
        # Add hashtags at the end
        if hashtags:
            text = f"{text}\n\n{' '.join(hashtags)}"
        
        # Truncate if necessary
        if len(text) > max_length:
            text = text[:max_length-3] + '...'
            self.logger.warning(f"Caption truncated to {max_length} characters")
            
        return text.strip()
    
    def _rate_limit(self):
        """Enforce rate limiting between API calls."""
        import time
        from datetime import datetime, timedelta
        
        now = datetime.now()
        time_since_last = (now - self.last_request_time).total_seconds()
        
        # Calculate minimum time between requests (in seconds)
        min_interval = 60 / self.rate_limit
        
        # Sleep if necessary
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = datetime.now()
    
    def __str__(self):
        return self.__class__.__name__
