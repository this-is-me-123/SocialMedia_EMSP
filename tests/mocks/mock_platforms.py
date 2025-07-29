"""Mock implementations of social media platforms for testing."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from automation_stack.platforms.base_platform import SocialMediaPlatform

class MockSocialMediaPlatform(SocialMediaPlatform):
    """Base class for mock social media platforms."""
    
    def __init__(self):
        self.posts = []
        self.authenticated = False
        self.name = "mock"
    
    def authenticate(self, **kwargs) -> bool:
        """Mock authentication."""
        self.authenticated = True
        return True
    
    def post(self, content: str, **kwargs) -> Dict[str, Any]:
        """Mock post creation."""
        if not self.authenticated:
            raise ValueError("Not authenticated")
            
        post = {
            "id": f"mock_post_{len(self.posts) + 1}",
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": kwargs
        }
        self.posts.append(post)
        return {"status": "success", "post_id": post["id"], "platform": self.name}
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Mock getting a post by ID."""
        for post in self.posts:
            if post["id"] == post_id:
                return post
        return None
    
    def get_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Mock getting recent posts."""
        return self.posts[-limit:]

class MockInstagramPlatform(MockSocialMediaPlatform):
    """Mock Instagram platform implementation."""
    
    def __init__(self):
        super().__init__()
        self.name = "instagram"
    
    def post(self, content: str, **kwargs) -> Dict[str, Any]:
        """Mock Instagram post with media support."""
        if "media_urls" not in kwargs:
            raise ValueError("Instagram posts require media")
        return super().post(content, **kwargs)

class MockFacebookPlatform(MockSocialMediaPlatform):
    """Mock Facebook platform implementation."""
    
    def __init__(self):
        super().__init__()
        self.name = "facebook"
    
    def post(self, content: str, **kwargs) -> Dict[str, Any]:
        """Mock Facebook post with link support."""
        if "link" not in kwargs and "media_urls" not in kwargs:
            raise ValueError("Facebook posts require either a link or media")
        return super().post(content, **kwargs)

class MockTwitterPlatform(MockSocialMediaPlatform):
    """Mock Twitter platform implementation."""
    
    def __init__(self):
        super().__init__()
        self.name = "twitter"
        self.max_length = 280
    
    def post(self, content: str, **kwargs) -> Dict[str, Any]:
        """Mock Twitter post with character limit."""
        if len(content) > self.max_length:
            raise ValueError(f"Tweet exceeds {self.max_length} characters")
        return super().post(content, **kwargs)

class MockTikTokPlatform(MockSocialMediaPlatform):
    """Mock TikTok platform implementation."""
    
    def __init__(self):
        super().__init__()
        self.name = "tiktok"
    
    def post(self, content: str, **kwargs) -> Dict[str, Any]:
        """Mock TikTok post with video requirement."""
        if "video_url" not in kwargs:
            raise ValueError("TikTok posts require a video URL")
        return super().post(content, **kwargs)
