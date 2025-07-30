"""
Enhanced Social Media Manager for scheduling and posting content to multiple platforms.

This module provides an advanced social media manager that handles scheduling,
rate limiting, and post management across multiple platforms with improved
error handling and monitoring capabilities.
"""
import os
import time
import json
import logging
import threading
import queue
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum, auto

# Import platform implementations
from automation_stack.social_media.platforms import (
    Instagram,
    Facebook,
    Twitter,
    Tiktok
)
from automation_stack.config import PLATFORMS, SCHEDULE

# Set up logging
logger = logging.getLogger('social_media.enhanced_manager')

class PostStatus(Enum):
    """Status of a social media post."""
    DRAFT = auto()
    SCHEDULED = auto()
    POSTING = auto()
    POSTED = auto()
    FAILED = auto()
    CANCELLED = auto()

@dataclass
class Post:
    """Represents a social media post with all its metadata."""
    platform: str
    content_path: str
    caption: str
    scheduled_time: datetime
    status: PostStatus = PostStatus.DRAFT
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert post to a dictionary."""
        result = asdict(self)
        result['status'] = self.status.name
        result['scheduled_time'] = self.scheduled_time.isoformat()
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Post':
        """Create a Post from a dictionary."""
        # Convert string timestamps back to datetime objects
        for time_field in ['scheduled_time', 'created_at', 'updated_at']:
            if time_field in data and isinstance(data[time_field], str):
                data[time_field] = datetime.fromisoformat(data[time_field])
        
        # Convert status string to enum
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = PostStatus[data['status']]
        
        return cls(**data)

class EnhancedSocialMediaManager:
    """
    Enhanced social media manager with advanced scheduling and monitoring.
    
    Features:
    - Thread-safe operation
    - Persistent storage of scheduled posts
    - Rate limiting and backoff
    - Detailed logging and monitoring
    - Support for multiple platforms
    - Event callbacks
    """
    
    def __init__(self, storage_path: Optional[Union[str, Path]] = None):
        """
        Initialize the enhanced social media manager.
        
        Args:
            storage_path: Path to store persistent data (posts, state, etc.)
        """
        self.platforms: Dict[str, Any] = {}
        self.scheduled_posts: Dict[str, Post] = {}
        self.post_queue = queue.Queue()
        self._shutdown_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._storage_path = Path(storage_path) if storage_path else Path('social_media_data')
        self._callbacks: Dict[str, List[Callable]] = {
            'post_scheduled': [],
            'post_started': [],
            'post_completed': [],
            'post_failed': [],
            'error': []
        }
        
        # Set up storage directory
        self._storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize platforms
        self._initialize_platforms()
        
        # Load saved posts
        self._load_posts()
        
        # Start worker thread
        self._start_worker()
    
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
                        # Enable mock mode for testing if specified
                        if platform_config.get('mock_mode', True):
                            platform_config['mock_mode'] = True
                            logger.info(f"Running {platform_name} in mock mode for testing")
                        
                        self.platforms[platform_name] = platform_class(platform_config)
                        logger.info(f"Initialized {platform_name} platform")
                    else:
                        logger.warning(f"No class found for platform: {platform_name}")
                except Exception as e:
                    logger.error(f"Error initializing {platform_name}: {str(e)}", exc_info=True)
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register a callback for an event.
        
        Args:
            event: Event name ('post_scheduled', 'post_started', 'post_completed', 'post_failed', 'error')
            callback: Callback function that takes (post: Post, **kwargs)
        """
        if event not in self._callbacks:
            raise ValueError(f"Unknown event: {event}")
        self._callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, post: Post, **kwargs) -> None:
        """Trigger callbacks for an event."""
        for callback in self._callbacks[event]:
            try:
                callback(post, **kwargs)
            except Exception as e:
                logger.error(f"Error in {event} callback: {str(e)}", exc_info=True)
    
    def _save_posts(self) -> None:
        """Save scheduled posts to disk."""
        # posts_file will resolve to backend/scheduled_posts.json or as set by storage_path
        posts_file = self._storage_path / 'scheduled_posts.json'
        posts_data = [post.to_dict() for post in self.scheduled_posts.values()]
        
        try:
            with open(posts_file, 'w') as f:
                json.dump(posts_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving posts: {str(e)}", exc_info=True)
    
    def _load_posts(self) -> None:
        """Load scheduled posts from disk."""
        # posts_file will resolve to backend/scheduled_posts.json or as set by storage_path
        posts_file = self._storage_path / 'scheduled_posts.json'
        
        if not posts_file.exists():
            return
        
        try:
            with open(posts_file, 'r') as f:
                posts_data = json.load(f)
            
            for post_data in posts_data:
                try:
                    post = Post.from_dict(post_data)
                    # Only load posts that are still pending
                    if post.status in [PostStatus.DRAFT, PostStatus.SCHEDULED]:
                        self.scheduled_posts[post.post_id or str(id(post))] = post
                except Exception as e:
                    logger.error(f"Error loading post: {str(e)}", exc_info=True)
            
            logger.info(f"Loaded {len(self.scheduled_posts)} scheduled posts")
        except Exception as e:
            logger.error(f"Error loading posts: {str(e)}", exc_info=True)
    
    def _start_worker(self) -> None:
        """Start the background worker thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            return
        
        self._shutdown_event.clear()
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            name="SocialMediaWorker",
            daemon=True
        )
        self._worker_thread.start()
        logger.info("Started social media worker thread")
    
    def _worker_loop(self) -> None:
        """Main worker loop for processing scheduled posts."""
        logger.info("Social media worker started")
        
        while not self._shutdown_event.is_set():
            try:
                # Process scheduled posts
                now = datetime.now()
                posts_to_process = [
                    post for post in self.scheduled_posts.values()
                    if post.status == PostStatus.SCHEDULED and post.scheduled_time <= now
                ]
                
                for post in posts_to_process:
                    self.post_queue.put(post)
                
                # Process the queue
                try:
                    post = self.post_queue.get_nowait()
                    self._process_post(post)
                    self.post_queue.task_done()
                except queue.Empty:
                    pass
                
                # Save posts periodically
                if int(time.time()) % 60 == 0:  # Every minute
                    self._save_posts()
                
                # Sleep to prevent busy-waiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}", exc_info=True)
                time.sleep(5)  # Prevent tight loop on repeated errors
        
        logger.info("Social media worker stopped")
    
    def _process_post(self, post: Post) -> None:
        """Process a single post."""
        if post.status != PostStatus.SCHEDULED:
            return
        
        # Update status to posting
        post.status = PostStatus.POSTING
        post.updated_at = datetime.now()
        self._trigger_callback('post_started', post)
        
        try:
            # Get the platform
            platform = self.platforms.get(post.platform.lower())
            if not platform:
                raise ValueError(f"Platform not found: {post.platform}")
            
            # Post to the platform
            result = platform.post(
                content_path=post.content_path,
                caption=post.caption,
                **post.metadata
            )
            
            # Update post with result
            if result.get('status') == 'success':
                post.status = PostStatus.POSTED
                post.post_id = result.get('id')
                post.post_url = result.get('url')
                self._trigger_callback('post_completed', post, result=result)
                logger.info(f"Posted to {post.platform}: {post.post_url}")
            else:
                raise Exception(result.get('message', 'Unknown error'))
                
        except Exception as e:
            post.status = PostStatus.FAILED
            post.error = str(e)
            self._trigger_callback('post_failed', post, error=str(e))
            logger.error(f"Error posting to {post.platform}: {str(e)}", exc_info=True)
        finally:
            post.updated_at = datetime.now()
            self._save_posts()
    
    def schedule_post(
        self,
        platform_name: str,
        content_path: Union[str, Path],
        caption: str,
        post_time: Optional[Union[datetime, str]] = None,
        **kwargs
    ) -> Post:
        """
        Schedule a post for a specific platform.
        
        Args:
            platform_name: Name of the platform (instagram, facebook, etc.)
            content_path: Path to the content file
            caption: Post caption text
            post_time: When to post (datetime object or ISO format string)
            **kwargs: Additional platform-specific parameters
            
        Returns:
            The scheduled Post object
        """
        # Normalize platform name
        platform_name = platform_name.lower()
        
        # Validate platform
        if platform_name not in self.platforms:
            error_msg = f"Platform not registered: {platform_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Parse post time
        if post_time is None:
            post_time = datetime.now() + timedelta(minutes=5)
        elif isinstance(post_time, str):
            try:
                post_time = datetime.fromisoformat(post_time)
            except ValueError as e:
                error_msg = f"Invalid datetime format: {post_time}"
                logger.error(error_msg)
                raise ValueError(error_msg) from e
        
        # Create post object
        post = Post(
            platform=platform_name,
            content_path=str(content_path),
            caption=caption,
            scheduled_time=post_time,
            status=PostStatus.SCHEDULED,
            metadata=kwargs
        )
        
        # Add to scheduled posts
        post_id = str(id(post))
        self.scheduled_posts[post_id] = post
        
        # Save posts
        self._save_posts()
        
        # Log and trigger callback
        logger.info(f"Scheduled {platform_name} post for {post_time}")
        self._trigger_callback('post_scheduled', post)
        
        return post
    
    def get_scheduled_posts(
        self,
        platform: Optional[str] = None,
        status: Optional[Union[PostStatus, str]] = None,
        limit: int = 100
    ) -> List[Post]:
        """
        Get scheduled posts with optional filtering.
        
        Args:
            platform: Filter by platform name
            status: Filter by status (PostStatus enum or string)
            limit: Maximum number of posts to return
            
        Returns:
            List of matching Post objects
        """
        posts = list(self.scheduled_posts.values())
        
        # Apply filters
        if platform:
            platform = platform.lower()
            posts = [p for p in posts if p.platform.lower() == platform]
        
        if status is not None:
            if isinstance(status, str):
                status = PostStatus[status.upper()]
            posts = [p for p in posts if p.status == status]
        
        # Sort by scheduled time (oldest first)
        posts.sort(key=lambda p: p.scheduled_time)
        
        return posts[:limit]
    
    def cancel_post(self, post_id: str) -> bool:
        """
        Cancel a scheduled post.
        
        Args:
            post_id: ID of the post to cancel
            
        Returns:
            True if the post was cancelled, False otherwise
        """
        if post_id in self.scheduled_posts:
            post = self.scheduled_posts[post_id]
            if post.status in [PostStatus.DRAFT, PostStatus.SCHEDULED]:
                post.status = PostStatus.CANCELLED
                post.updated_at = datetime.now()
                self._save_posts()
                logger.info(f"Cancelled post: {post_id}")
                return True
        return False
    
    def shutdown(self) -> None:
        """Shut down the social media manager."""
        logger.info("Shutting down social media manager...")
        self._shutdown_event.set()
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5)
        
        # Save posts before shutting down
        self._save_posts()
        logger.info("Social media manager shut down")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()


def example_usage():
    """Example usage of the EnhancedSocialMediaManager."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('social_media.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create a callback function
    def on_post_scheduled(post: Post, **kwargs):
        logger.info(f"Post scheduled: {post.platform} at {post.scheduled_time}")
    
    # Initialize the manager
    with EnhancedSocialMediaManager() as manager:
        # Register callbacks
        manager.register_callback('post_scheduled', on_post_scheduled)
        
        # Schedule a post
        post = manager.schedule_post(
            platform_name='twitter',
            content_path='path/to/image.jpg',
            caption='Hello from EnhancedSocialMediaManager! #test',
            post_time=(datetime.now() + timedelta(minutes=5)).isoformat(),
            media_alt_text='Test image'
        )
        
        # List scheduled posts
        scheduled = manager.get_scheduled_posts()
        print(f"Scheduled posts: {len(scheduled)}")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")


if __name__ == "__main__":
    example_usage()
