"""
Simplified base platform implementation for testing.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

class SimpleSocialMediaPlatform(ABC):
    """Simplified base class for social media platform integrations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.authenticated = False
        self.dry_run = config.get('dry_run', False)
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform's API."""
        pass
    
    @abstractmethod
    def post_image(self, image_path: str, caption: str, **kwargs) -> Dict[str, Any]:
        """Post an image to the platform."""
        pass
    
    def format_caption(self, caption: str, max_hashtags: int = 5) -> str:
        """Format the caption with proper hashtag handling."""
        if not caption:
            return ""
            
        # Split into lines and process each line
        lines = caption.split('\n')
        processed_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # If line contains hashtags, process them
            if '#' in line:
                # Split into text and hashtags
                parts = line.split('#')
                text_part = parts[0].strip()
                
                # Extract and process hashtags
                hashtags = []
                for part in parts[1:]:
                    if not part:
                        continue
                    # Get the first word as the hashtag
                    tag = part.split()[0] if ' ' in part else part
                    hashtags.append(f"#{tag}")
                
                # Limit number of hashtags
                if max_hashtags and len(hashtags) > max_hashtags:
                    hashtags = hashtags[:max_hashtags]
                
                # Rebuild the line
                line = text_part
                if hashtags:
                    line += " " + " ".join(hashtags)
            
            processed_lines.append(line)
        
        return "\n".join(processed_lines)

class TestSimplePlatform(SimpleSocialMediaPlatform):
    """Test implementation of the simple platform."""
    
    def authenticate(self) -> bool:
        """Test authentication."""
        self.logger.info("Authenticating with test platform")
        self.authenticated = True
        return True
    
    def post_image(self, image_path: str, caption: str, **kwargs) -> Dict[str, Any]:
        """Test image posting."""
        if not self.authenticated:
            return {
                'status': 'error',
                'message': 'Not authenticated',
                'platform': 'test'
            }
        
        self.logger.info(f"Posting image: {image_path}")
        self.logger.info(f"Caption: {caption}")
        
        if self.dry_run:
            return {
                'status': 'success',
                'message': 'Dry run - no post made',
                'platform': 'test',
                'dry_run': True
            }
        
        # In a real implementation, this would post to the actual platform
        return {
            'status': 'success',
            'message': 'Post successful',
            'platform': 'test',
            'image_path': image_path,
            'caption': caption
        }
