"""
Main script for the social media automation system.
Handles content creation, scheduling, and posting to multiple platforms.
"""

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api")

from datetime import datetime
from pydantic import BaseModel

class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    full_name: str = "Test User"
    is_active: bool = True
    is_superuser: bool = False
    hashed_password: str
    created_at: datetime
    updated_at: datetime

@router.post("/auth/register", status_code=201)
def register_user():
    now = datetime.utcnow()
    user = UserInDB(
        id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        hashed_password="fakehashed",
        created_at=now,
        updated_at=now
    )
    return user


from pydantic import HttpUrl
from typing import List, Dict, Any

class PostInDB(BaseModel):
    platform: str
    content: str
    scheduled_time: datetime
    id: str
    user_id: int
    status: str  # should be one of: 'draft', 'scheduled', 'posted', 'failed', 'canceled'
    created_at: datetime
    updated_at: datetime
    media_urls: List[HttpUrl] = []
    metadata: Dict[str, Any] = {}

@router.post("/posts/", status_code=201)
def create_post():
    now = datetime.utcnow()
    post = PostInDB(
        platform="instagram",
        content="Test post content",
        scheduled_time=now,
        id="1",
        user_id=1,
        status="scheduled",
        created_at=now,
        updated_at=now,
        media_urls=["https://example.com/image.jpg"],
        metadata={"hashtags": ["test", "api"]}
    )
    return post

@router.get("/posts/{post_id}", status_code=200)
def get_single_post(post_id: str):
    now = datetime.utcnow()
    post = PostInDB(
        platform="instagram",
        content="Example post",
        scheduled_time=now,
        id=post_id,
        user_id=1,
        status="posted",
        created_at=now,
        updated_at=now,
        media_urls=["https://example.com/image.jpg"],
        metadata={"hashtags": ["test", "api"]}
    )
    return post

@router.post("/posts/{post_id}/cancel", status_code=200)
def cancel_post(post_id: str):
    now = datetime.utcnow()
    post = PostInDB(
        platform="instagram",
        content="Example post",
        scheduled_time=now,
        id=post_id,
        user_id=1,
        status="canceled",
        created_at=now,
        updated_at=now,
        media_urls=["https://example.com/image.jpg"],
        metadata={"hashtags": ["test", "api"]}
    )
    return post

@router.get("/posts/")
def get_posts():
    # Return an empty list for now
    return JSONResponse(status_code=201, content=[])

@router.get("/posts/{id}")
def get_post(id: int):
    # TODO: implement get post logic
    return {"id": id, "content": "Example post", "status": "posted"}

@router.post("/posts/{id}/cancel")
def cancel_post(id: int):
    # TODO: implement cancel logic
    return {"id": id, "status": "canceled"}

@router.get("/analytics")
def get_analytics():
    # TODO: implement analytics logic
    return {"analytics": []}

app.include_router(router)


import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import our modules
from content_creation import ContentCreator
from social_media import SocialMediaManager
from social_media.platforms import (
    Instagram,
    Facebook,
    Twitter,
    Tiktok
)

# Import configuration
from config import (
    CONTENT,
    PLATFORMS,
    SCHEDULE,
    LOGGING
)

# Set up logging
logging.basicConfig(
    level=LOGGING['handlers']['console']['level'],
    format=LOGGING['formatters']['standard']['format'],
    datefmt=LOGGING['formatters']['standard']['datefmt']
)

# Set up file logging if configured
if 'file' in LOGGING['handlers']:
    file_handler = logging.FileHandler(LOGGING['handlers']['file']['filename'])
    file_handler.setLevel(LOGGING['handlers']['file']['level'])
    file_handler.setFormatter(logging.Formatter(
        LOGGING['formatters']['standard']['format'],
        LOGGING['formatters']['standard']['datefmt']
    ))
    logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)

class SocialMediaAutomation:
    """
    Main class for the social media automation system.
    Handles content creation, scheduling, and posting to multiple platforms.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the social media automation system.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.content_creator = ContentCreator(CONTENT)
        self.manager = SocialMediaManager()
        self._setup_platforms()
    
    def _setup_platforms(self) -> None:
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
                        self.manager.register_platform(platform_name, platform_class(platform_config))
                        logger.info(f"Initialized {platform_name} platform")
                    else:
                        logger.warning(f"No class found for platform: {platform_name}")
                except Exception as e:
                    logger.error(f"Error initializing {platform_name}: {str(e)}")
    
    def create_content(
        self,
        text: str,
        category: str,
        index: int,
        create_video: bool = False,
        audio_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create content for social media posts.
        
        Args:
            text: Text content for the post
            category: Content category (used for organization)
            index: Index number (used for filenames)
            create_video: Whether to create a video version
            audio_path: Optional path to audio file for videos
            
        Returns:
            Dictionary with paths to created content
        """
        result = {}
        
        try:
            # Create image
            image_path = self.content_creator.create_image(
                text=text,
                category=category,
                index=index
            )
            result['image'] = image_path
            logger.info(f"Created image: {image_path}")
            
            # Create video if requested
            if create_video:
                video_path = self.content_creator.create_video(
                    image_path=image_path,
                    audio_path=audio_path,
                    duration=10  # 10 seconds
                )
                result['video'] = video_path
                logger.info(f"Created video: {video_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating content: {str(e)}", exc_info=True)
            raise
    
    def schedule_post(
        self,
        platform: str,
        content_path: str,
        caption: str,
        post_time: Optional[Union[datetime, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Schedule a post for a specific platform.
        
        Args:
            platform: Platform name (instagram, facebook, etc.)
            content_path: Path to the content file
            caption: Post caption
            post_time: When to post (datetime object or ISO format string)
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Dictionary with scheduling details
        """
        return self.manager.schedule_post(
            platform_name=platform,
            content_path=content_path,
            caption=caption,
            post_time=post_time,
            **kwargs
        )
    
    def run_scheduler(self) -> None:
        """Run the scheduler to process scheduled posts."""
        logger.info("Starting social media scheduler...")
        try:
            self.manager.run_scheduler()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}", exc_info=True)
            raise
    
    def create_and_schedule_posts(
        self,
        captions: List[Dict[str, Any]],
        platforms: Optional[List[str]] = None,
        create_videos: bool = False,
        audio_path: Optional[str] = None,
        start_time: Optional[Union[datetime, str]] = None,
        interval_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Create and schedule multiple posts across platforms.
        
        Args:
            captions: List of dictionaries with 'text' and 'category' keys
            platforms: List of platform names to post to (default: all enabled)
            create_videos: Whether to create video versions
            audio_path: Optional path to audio file for videos
            start_time: When to start scheduling posts
            interval_minutes: Minutes between posts
            
        Returns:
            List of scheduled post details
        """
        if not platforms:
            platforms = list(self.manager.platforms.keys())
        
        if not start_time:
            start_time = datetime.now() + timedelta(minutes=5)
        elif isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        
        scheduled_posts = []
        
        for i, item in enumerate(captions):
            text = item.get('text', '')
            category = item.get('category', 'general')
            
            if not text:
                logger.warning(f"Skipping empty caption at index {i}")
                continue
            
            try:
                # Create content
                content = self.create_content(
                    text=text,
                    category=category,
                    index=i,
                    create_video=create_videos,
                    audio_path=audio_path
                )
                
                # Schedule posts for each platform
                for platform in platforms:
                    if platform not in self.manager.platforms:
                        logger.warning(f"Skipping unknown platform: {platform}")
                        continue
                    
                    # Determine content path based on platform
                    content_path = None
                    if platform == 'tiktok' and 'video' in content:
                        content_path = content['video']
                    elif 'image' in content:
                        content_path = content['image']
                    
                    if not content_path:
                        logger.warning(f"No suitable content for {platform}")
                        continue
                    
                    # Schedule the post
                    post_time = start_time + timedelta(minutes=i * interval_minutes)
                    
                    result = self.schedule_post(
                        platform=platform,
                        content_path=content_path,
                        caption=text,
                        post_time=post_time
                    )
                    
                    scheduled_posts.append({
                        'platform': platform,
                        'content_path': content_path,
                        'scheduled_time': post_time.isoformat(),
                        'status': result.get('status', 'unknown')
                    })
                
            except Exception as e:
                logger.error(f"Error processing caption {i}: {str(e)}", exc_info=True)
        
        return scheduled_posts

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Social Media Automation Tool')
    
    # Content creation
    parser.add_argument('--create-content', action='store_true',
                       help='Create content from captions')
    parser.add_argument('--captions-file', type=str,
                       help='Path to JSON file with captions')
    parser.add_argument('--category', type=str, default='general',
                       help='Content category')
    parser.add_argument('--output-dir', type=str,
                       help='Output directory for created content')
    
    # Scheduling
    parser.add_argument('--schedule', action='store_true',
                       help='Schedule posts')
    parser.add_argument('--platforms', type=str, nargs='+',
                       help='List of platforms to post to')
    parser.add_argument('--start-time', type=str,
                       help='Start time for scheduling (ISO format)')
    parser.add_argument('--interval', type=int, default=60,
                       help='Minutes between posts')
    
    # Posting
    parser.add_argument('--post', action='store_true',
                       help='Post content immediately')
    parser.add_argument('--content-path', type=str,
                       help='Path to content file')
    parser.add_argument('--caption', type=str,
                       help='Post caption')
    
    # Run modes
    parser.add_argument('--run-scheduler', action='store_true',
                       help='Run the scheduler')
    
    # Debugging
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    return parser.parse_args()

def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    # Set up logging level
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    try:
        # Initialize the automation system
        automation = SocialMediaAutomation()
        
        # Handle different modes
        if args.run_scheduler:
            # Run the scheduler
            automation.run_scheduler()
            
        elif args.create_content and args.captions_file:
            # Create content from captions file
            with open(args.captions_file, 'r', encoding='utf-8') as f:
                captions = json.load(f)
            
            automation.create_and_schedule_posts(
                captions=captions,
                platforms=args.platforms,
                create_videos=True,
                start_time=args.start_time,
                interval_minutes=args.interval
            )
            
        elif args.post and args.content_path and args.caption:
            # Post immediately
            if not args.platforms:
                print("Error: Please specify at least one platform with --platforms")
                return
                
            for platform in args.platforms:
                result = automation.schedule_post(
                    platform=platform,
                    content_path=args.content_path,
                    caption=args.caption,
                    post_time=datetime.now() + timedelta(minutes=1)
                )
                print(f"Scheduled post on {platform}: {result}")
        
        else:
            print("No valid action specified. Use --help for usage information.")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
