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

from automation_stack.social_media.platforms import (
    Instagram,
    Facebook,
    Twitter,
    Tiktok
)
from automation_stack.config import PLATFORMS, SCHEDULE

# Set up logging
logger = logging.getLogger(__name__)

class SocialMediaManager:
    """
    Manages social media posting across multiple platforms.
    Handles scheduling, rate limiting, and post management.
    """
    
    MAX_RETRIES = 3
    RETRY_DELAY_MINUTES = 10

    SCHEDULED_POSTS_FILE = os.path.join(os.path.dirname(__file__), 'scheduled_posts.json')

    def __init__(self):
        """Initialize the social media manager."""
        self.platforms: Dict[str, Any] = {}
        self.scheduled_posts: List[Dict[str, Any]] = []
        self._setup_logging()
        self._initialize_platforms()
        self.load_scheduled_posts()

    def load_scheduled_posts(self):
        """Load scheduled posts from file if it exists."""
        try:
            if os.path.exists(self.SCHEDULED_POSTS_FILE):
                with open(self.SCHEDULED_POSTS_FILE, 'r', encoding='utf-8') as f:
                    self.scheduled_posts = json.load(f)
                self.logger.info(f"Loaded {len(self.scheduled_posts)} scheduled posts from file.")
        except Exception as e:
            self.logger.error(f"Error loading scheduled posts: {e}")

    def save_scheduled_posts(self):
        """Save scheduled posts to file."""
        try:
            with open(self.SCHEDULED_POSTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.scheduled_posts, f, indent=2, default=str)
            self.logger.info(f"Saved {len(self.scheduled_posts)} scheduled posts to file.")
        except Exception as e:
            self.logger.error(f"Error saving scheduled posts: {e}")

    
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
    
    def create_post(
        self,
        platform_name: str,
        content_path: Union[str, Path],
        caption: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Immediately post content to the specified platform.

        Args:
            platform_name: Name of the platform (e.g., 'twitter')
            content_path: Path to the content file
            caption: Post caption text
            **kwargs: Additional platform-specific parameters

        Returns:
            Dictionary with post details and status
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

        try:
            result = self._post_to_platform(
                platform_name=platform_name,
                content_path=str(content_path),
                caption=caption,
                **kwargs
            )
            self.logger.info(f"Posted to {platform_name}: {result}")
            return result
        except Exception as e:
            error_msg = f"Error posting to {platform_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg,
                'platform': platform_name
            }

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
            except Exception as ex:
                self.logger.error(f"Failed to parse post_time: {ex}")
                return {
                    'status': 'error',
                    'message': f'Invalid post_time format: {post_time}',
                    'platform': platform_name,
                    'scheduled_time': post_time
                }
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
            self.save_scheduled_posts()
            self.logger.info(
                f"Scheduled {platform_name} post for {post_time}"
            )
            # Analytics event: scheduling success
            try:
                import requests
                requests.post(
                    "http://localhost:8000/api/analytics/event",
                    json={
                        "event": "post_scheduled",
                        "platform": platform_name,
                        "content_path": str(content_path),
                        "caption": caption,
                        "scheduled_time": post_time.isoformat() if hasattr(post_time, 'isoformat') else str(post_time),
                        "status": "scheduled",
                        "timestamp": datetime.utcnow().isoformat()
                    }, timeout=3
                )
            except Exception:
                pass
            post['status'] = 'scheduled'
            return post
            
        except Exception as e:
            error_msg = f"Error scheduling post: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            post.update({
                'status': 'error',
                'error': str(e)
            })
            # Analytics event: scheduling error
            try:
                import requests, datetime
                requests.post(
                    "http://localhost:8000/api/analytics/event",
                    json={
                        "event": "post_scheduling_failed",
                        "platform": platform_name,
                        "content_path": str(content_path),
                        "caption": caption,
                        "scheduled_time": post_time.isoformat() if hasattr(post_time, 'isoformat') else str(post_time),
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.datetime.utcnow().isoformat()
                    }, timeout=3
                )
            except Exception:
                pass
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
                    # Analytics event: posting error (auth failure)
                    try:
                        import requests, datetime
                        requests.post(
                            "http://localhost:8000/api/analytics/event",
                            json={
                                "event": "post_failed",
                                "platform": platform_name,
                                "content_path": content_path,
                                "caption": caption,
                                "status": "error",
                                "error": error_msg,
                                "timestamp": datetime.datetime.utcnow().isoformat()
                            }, timeout=3
                        )
                    except Exception:
                        pass
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
            # Analytics event: posting success
            try:
                import requests, datetime
                requests.post(
                    "http://localhost:8000/api/analytics/event",
                    json={
                        "event": "post_published",
                        "platform": platform_name,
                        "content_path": content_path,
                        "caption": caption,
                        "status": "success",
                        "result": result,
                        "timestamp": datetime.datetime.utcnow().isoformat()
                    }, timeout=3
                )
            except Exception:
                pass
            return {
                'status': 'success',
                'platform': platform_name,
                'result': result
            }
            
        except Exception as e:
            error_msg = f"Error posting to {platform_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            # Analytics event: posting error
            try:
                import requests, datetime
                requests.post(
                    "http://localhost:8000/api/analytics/event",
                    json={
                        "event": "post_failed",
                        "platform": platform_name,
                        "content_path": content_path,
                        "caption": caption,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.datetime.utcnow().isoformat()
                    }, timeout=3
                )
            except Exception:
                pass
            # Auto-retry logic
            retry_post = None
            for post in self.scheduled_posts:
                if post.get('platform') == platform_name and post.get('content_path') == content_path and post.get('caption') == caption:
                    retry_count = post.get('retry_count', 0) + 1
                    post['retry_count'] = retry_count
                    if retry_count <= self.MAX_RETRIES:
                        import datetime as dt
                        from copy import deepcopy
                        next_time = dt.datetime.now() + dt.timedelta(minutes=self.RETRY_DELAY_MINUTES)
                        post['scheduled_time'] = next_time
                        post['status'] = 'retrying'
                        self.logger.warning(f"Retrying post to {platform_name} (attempt {retry_count}/{self.MAX_RETRIES}) at {next_time}")
                        # Analytics event: retry scheduled
                        try:
                            import requests
                            requests.post(
                                "http://localhost:8000/api/analytics/event",
                                json={
                                    "event": "post_retry_scheduled",
                                    "platform": platform_name,
                                    "content_path": content_path,
                                    "caption": caption,
                                    "retry_count": retry_count,
                                    "next_attempt": next_time.isoformat(),
                                    "timestamp": dt.datetime.utcnow().isoformat()
                                }, timeout=3
                            )
                        except Exception:
                            pass
                        # Schedule retry
                        import schedule
                        schedule.every(self.RETRY_DELAY_MINUTES).minutes.do(
                            self._post_to_platform,
                            platform_name=platform_name,
                            content_path=content_path,
                            caption=caption,
                            **kwargs
                        )
                    else:
                        post['status'] = 'failed'
                        self.logger.error(f"Post to {platform_name} failed after {retry_count} attempts.")
                        # Analytics event: final failure
                        try:
                            import requests
                            requests.post(
                                "http://localhost:8000/api/analytics/event",
                                json={
                                    "event": "post_final_failure",
                                    "platform": platform_name,
                                    "content_path": content_path,
                                    "caption": caption,
                                    "retry_count": retry_count,
                                    "timestamp": dt.datetime.utcnow().isoformat()
                                }, timeout=3
                            )
                        except Exception:
                            pass
                        # Send notification
                        try:
                            from automation_stack.email_utils import send_failure_notification
                            subject = f"[SocialMediaAutomation] Post failed after {retry_count} attempts"
                            message = f"Platform: {platform_name}\nContent: {content_path}\nCaption: {caption}\nAttempts: {retry_count}\nStatus: FAILED"
                            send_failure_notification(subject, message)
                            # Analytics event: notification sent
                            try:
                                requests.post(
                                    "http://localhost:8000/api/analytics/event",
                                    json={
                                        "event": "notification_sent",
                                        "platform": platform_name,
                                        "content_path": content_path,
                                        "caption": caption,
                                        "retry_count": retry_count,
                                        "timestamp": dt.datetime.utcnow().isoformat()
                                    }, timeout=3
                                )
                            except Exception:
                                pass
                        except Exception:
                            pass
                    break
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
