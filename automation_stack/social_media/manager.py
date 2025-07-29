"""
Social media manager for scheduling and posting content to multiple platforms.
"""
import os
import time
import json
import logging
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from .platforms import (
    Instagram,
    Facebook,
    Twitter,
    Tiktok
)
from config import PLATFORMS, SCHEDULE

# Set up logging
logger = logging.getLogger(__name__)

class SocialMediaManager:
    """
    Manages social media posting across multiple platforms.
    Handles scheduling, rate limiting, and post management.
    """
    
    def __init__(self):
        """Initialize the social media manager."""
        self.platforms: Dict[str, Any] = {}
        self.scheduled_posts: List[Dict[str, Any]] = []
        self._initialize_platforms()
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging for the manager."""
        self.logger = logging.getLogger('social_media.manager')
        
    def _initialize_platforms(self) -> None:
        """Initialize all enabled social media platforms."""
        platform_classes = {
            'instagram': Instagram,
            'facebook': Facebook,
            'twitter': Twitter,
            'tiktok': Tiktok
        }
        
        for platform_name, platform_config in PLATFORMS.items():
            if platform_config.get('enabled', False):
                try:
                    platform_class = platform_classes.get(platform_name.lower())
                    if platform_class:
                        self.platforms[platform_name] = platform_class(platform_config)
                        self.logger.info(f"Initialized {platform_name} platform")
                    else:
                        self.logger.warning(f"No class found for platform: {platform_name}")
                except Exception as e:
                    self.logger.error(f"Error initializing {platform_name}: {str(e)}")
    
    def register_platform(self, name: str, platform: Any) -> None:
        """
        Register a social media platform.
        
        Args:
            name: Name of the platform
            platform: Platform instance
        """
        self.platforms[name.lower()] = platform
        self.logger.info(f"Registered platform: {name}")
    
    def schedule_post(
        self,
        platform_name: str,
        content_path: Union[str, Path],
        caption: str,
        post_time: Optional[Union[datetime, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Schedule a post for a specific platform.
        
        Args:
            platform_name: Name of the platform (instagram, facebook, etc.)
            content_path: Path to the content file
            caption: Post caption text
            post_time: When to post (datetime object or ISO format string)
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Dictionary with post details and status
        """
        # Normalize platform name
        platform_name = platform_name.lower()
        
        # Validate platform
        if platform_name not in self.platforms:
            error_msg = f"Platform not registered: {platform_name}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'platform': platform_name,
                'scheduled_time': post_time
            }
        
        # Parse post time
        if post_time is None:
            post_time = datetime.now() + timedelta(minutes=5)
        elif isinstance(post_time, str):
            try:
                post_time = datetime.fromisoformat(post_time)
            except ValueError:
                error_msg = f"Invalid datetime format: {post_time}"
                self.logger.error(error_msg)
                return {
                    'status': 'error',
                    'message': error_msg,
                    'platform': platform_name,
                    'scheduled_time': post_time
                }
        
        # Create post object
        post = {
            'platform': platform_name,
            'content_path': str(content_path),
            'caption': caption,
            'scheduled_time': post_time,
            'status': 'scheduled',
            'created_at': datetime.now(),
            'kwargs': kwargs
        }
        
        # Schedule the post
        try:
            # For real scheduling, you would use a proper job scheduler
            # This is a simplified version
            schedule.every().day.at(
                post_time.strftime('%H:%M')
            ).do(
                self._post_to_platform,
                platform_name=platform_name,
                content_path=str(content_path),
                caption=caption,
                **kwargs
            )
            
            self.scheduled_posts.append(post)
            self.logger.info(
                f"Scheduled {platform_name} post for {post_time}"
            )
            
            post['status'] = 'scheduled'
            return post
            
        except Exception as e:
            error_msg = f"Error scheduling post: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            post.update({
                'status': 'error',
                'error': str(e)
            })
            return post
    
    def _post_to_platform(
        self,
        platform_name: str,
        content_path: str,
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Internal method to handle posting to a platform.
        
        Args:
            platform_name: Name of the platform
            content_path: Path to the content file
            caption: Post caption
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Dictionary with the post result
        """
        platform = self.platforms.get(platform_name.lower())
        if not platform:
            error_msg = f"Platform not found: {platform_name}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'platform': platform_name
            }
        
        try:
            # Authenticate if needed
            if not platform.authenticated:
                if not platform.authenticate():
                    error_msg = f"Authentication failed for {platform_name}"
                    self.logger.error(error_msg)
                    return {
                        'status': 'error',
                        'message': error_msg,
                        'platform': platform_name
                    }
            
            # Post to the platform
            result = platform.post(content_path, caption, **kwargs)
            
            # Log the result
            self.logger.info(
                f"Posted to {platform_name}: {result.get('id', 'No ID')}"
            )
            
            return {
                'status': 'success',
                'platform': platform_name,
                'result': result
            }
            
        except Exception as e:
            error_msg = f"Error posting to {platform_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'platform': platform_name
            }
    
    def get_scheduled_posts(
        self,
        platform: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get a list of scheduled posts.
        
        Args:
            platform: Filter by platform name
            status: Filter by status (scheduled, posted, error)
            
        Returns:
            List of scheduled posts
        """
        posts = self.scheduled_posts
        
        if platform:
            platform = platform.lower()
            posts = [p for p in posts if p['platform'].lower() == platform]
            
        if status:
            status = status.lower()
            posts = [p for p in posts if p['status'].lower() == status]
            
        return posts
    
    def run_scheduler(self) -> None:
        """
        Run the scheduler loop.
        This will block the current thread.
        """
        self.logger.info("Starting social media scheduler...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {str(e)}", exc_info=True)
            raise
    
    def __str__(self) -> str:
        """String representation of the manager."""
        return f"SocialMediaManager(platforms={len(self.platforms)}, scheduled_posts={len(self.scheduled_posts)})"
    
    def __repr__(self) -> str:
        """Official string representation."""
        return f"<SocialMediaManager platforms={len(self.platforms)}>"


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the manager
    manager = SocialMediaManager()
    
    # Example: Schedule a post
    post = manager.schedule_post(
        platform_name="instagram",
        content_path="path/to/image.jpg",
        caption="Test post from SocialMediaManager #test #automation",
        post_time=(datetime.now() + timedelta(minutes=5)).isoformat()
    )
    
    print(f"Scheduled post: {post}")
    
    # Run the scheduler (this will block)
    try:
        manager.run_scheduler()
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
