"""
Base class for social media platform integrations.
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
from pathlib import Path

class SocialMediaPlatform(ABC):
    """
    Abstract base class for social media platform integrations.
    All platform implementations must inherit from this class.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the platform with configuration.
        
        Args:
            config: Platform-specific configuration dictionary
        """
        self.config = config or {}
        self.name = self.__class__.__name__.lower()
        self.authenticated = False
        self.logger = logging.getLogger(f"social_media.{self.name}")
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform's API.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def post(
        self,
        content_path: Union[str, Path],
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to the platform.
        
        Args:
            content_path: Path to the content file (image or video)
            caption: Caption text for the post
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Dict containing the post response and status
        """
        pass
    
    def validate_content(
        self,
        content_path: Union[str, Path],
        content_type: Optional[str] = None
    ) -> bool:
        """
        Validate content before posting.
        
        Args:
            content_path: Path to the content file
            content_type: Optional content type (image, video, etc.)
            
        Returns:
            bool: True if content is valid, False otherwise
        """
        content_path = Path(content_path)
        
        # Check if file exists
        if not content_path.exists():
            self.logger.error(f"Content file not found: {content_path}")
            return False
            
        # Check file size (max 50MB for most platforms)
        max_size_mb = 50
        file_size_mb = content_path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            self.logger.error(
                f"File too large: {file_size_mb:.2f}MB "
                f"(max {max_size_mb}MB): {content_path}"
            )
            return False
            
        return True
    
    def _get_content_type(self, file_path: Union[str, Path, list]) -> str:
        """
        Determine the content type: image, video, text, link, or carousel.
        Args:
            file_path: Path to the file, string content, URL, or list of files
        Returns:
            Content type (image, video, text, link, carousel, or unknown)
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

        # Carousel: list of image paths
        if isinstance(file_path, list) and all(isinstance(p, (str, Path)) and str(p).lower().endswith(tuple(image_extensions)) for p in file_path):
            return 'carousel'
        # Link: URL string
        if isinstance(file_path, str) and file_path.strip().lower().startswith(('http://', 'https://')):
            return 'link'
        # Text: plain string, not a file path or URL
        if isinstance(file_path, str) and not any(file_path.lower().endswith(ext) for ext in image_extensions | video_extensions) and not file_path.strip().lower().startswith(('http://', 'https://')):
            return 'text'
        # Image/video: file path
        ext = Path(file_path).suffix.lower() if isinstance(file_path, (str, Path)) else ''
        if ext in image_extensions:
            return 'image'
        elif ext in video_extensions:
            return 'video'
        return 'unknown'
    
    def format_hashtags(
        self,
        text: str,
        max_hashtags: int = 30
    ) -> str:
        """
        Format and limit hashtags in the text.
        
        Args:
            text: Text containing hashtags
            max_hashtags: Maximum number of hashtags to allow
            
        Returns:
            Formatted text with limited hashtags
        """
        import re
        
        # Extract all hashtags
        hashtags = re.findall(r'#\w+', text)
        
        # Limit number of hashtags
        if len(hashtags) > max_hashtags:
            hashtags = hashtags[:max_hashtags]
            
        # Remove hashtags from original text
        clean_text = re.sub(r'#\w+', '', text).strip()
        
        # Add hashtags at the end
        if hashtags:
            clean_text += '\n\n' + ' '.join(hashtags)
            
        return clean_text.strip()
    
    def __str__(self) -> str:
        """String representation of the platform."""
        return f"{self.name.capitalize()}Platform(authenticated={self.authenticated})"
    
    def __repr__(self) -> str:
        """Official string representation."""
        return f"<{self.__class__.__name__} authenticated={self.authenticated}>"
