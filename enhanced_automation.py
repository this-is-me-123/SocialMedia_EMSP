"""
Enhanced Social Media Automation System

This script provides a command-line interface for managing social media posts
across multiple platforms (Instagram, Facebook, Twitter, TikTok) with advanced
scheduling, monitoring, and error handling capabilities.
"""
import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import our modules
from automation_stack.social_media.enhanced_manager import EnhancedSocialMediaManager, PostStatus
from automation_stack.social_media.platforms import (
    Instagram, Facebook, Twitter, Tiktok
)

# Import configuration
from config import (
    PLATFORMS,
    LOG_LEVEL,
    TESTING,
    BASE_DIR
)

# Set up logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / 'social_media_automation.log')
    ]
)
logger = logging.getLogger('enhanced_automation')

class SocialMediaAutomation:
    """
    Enhanced Social Media Automation System
    
    This class provides methods to manage social media posts across multiple
    platforms with advanced scheduling and monitoring capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the social media automation system.
        
        Args:
            config: Optional configuration dictionary to override defaults
        """
        self.config = config or {}
        self.manager = EnhancedSocialMediaManager(
            storage_path=str(BASE_DIR / 'scheduled_posts.json'),
            **self.config.get('manager', {})
        )
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
                        # Enable mock mode for testing
                        if TESTING:
                            platform_config['mock_mode'] = True
                            logger.info(f"Enabled mock mode for {platform_name}")
                        
                        # Initialize the platform
                        platform = platform_class(platform_config)
                        self.manager.platforms[platform_name] = platform
                        logger.info(f"Initialized {platform_name} platform")
                    else:
                        logger.warning(f"No class found for platform: {platform_name}")
                except Exception as e:
                    logger.error(f"Error initializing {platform_name}: {str(e)}", exc_info=True)
    
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
            platform: Platform name (instagram, facebook, twitter, tiktok)
            content_path: Path to the content file (image or video)
            caption: Post caption
            post_time: When to post (datetime object or ISO format string)
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Dictionary with scheduling details
        """
        try:
            # Convert string post_time to datetime if needed
            if isinstance(post_time, str):
                post_time = datetime.fromisoformat(post_time)
            
            # Schedule the post
            post = self.manager.schedule_post(
                platform_name=platform,
                content_path=content_path,
                caption=caption,
                post_time=post_time,
                **kwargs
            )
            
            logger.info(f"Scheduled post on {platform} for {post.scheduled_time}")
            return {
                'status': 'scheduled',
                'post_id': post.post_id,
                'platform': platform,
                'scheduled_time': post.scheduled_time.isoformat(),
                'caption': caption[:50] + '...' if len(caption) > 50 else caption
            }
            
        except Exception as e:
            error_msg = f"Error scheduling post: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg,
                'platform': platform
            }
    
    def list_scheduled_posts(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all scheduled posts, optionally filtered by status.
        
        Args:
            status: Optional status filter (scheduled, posted, failed, cancelled)
            
        Returns:
            List of dictionaries with post details
        """
        try:
            posts = self.manager.get_scheduled_posts()
            
            # Filter by status if specified
            if status:
                status_enum = PostStatus[status.upper()]
                posts = [p for p in posts if p.status == status_enum]
            
            # Convert posts to dictionaries
            result = []
            for post in posts:
                result.append({
                    'id': post.post_id,
                    'platform': post.platform,
                    'status': post.status.name,
                    'scheduled_time': post.scheduled_time.isoformat(),
                    'caption': post.caption[:50] + '...' if len(post.caption) > 50 else post.caption,
                    'content_path': post.content_path
                })
            
            return result
            
        except Exception as e:
            error_msg = f"Error listing scheduled posts: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return []
    
    def cancel_post(self, post_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled post.
        
        Args:
            post_id: ID of the post to cancel
            
        Returns:
            Dictionary with cancellation status
        """
        try:
            success = self.manager.cancel_post(post_id)
            if success:
                logger.info(f"Cancelled post: {post_id}")
                return {
                    'status': 'cancelled',
                    'post_id': post_id
                }
            else:
                logger.warning(f"Failed to cancel post: {post_id}")
                return {
                    'status': 'error',
                    'message': 'Post not found or already processed',
                    'post_id': post_id
                }
                
        except Exception as e:
            error_msg = f"Error cancelling post: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg,
                'post_id': post_id
            }
    
    def run_scheduler(self, interval: int = 60) -> None:
        """
        Run the scheduler to process scheduled posts.
        
        Args:
            interval: How often to check for posts to publish (in seconds)
        """
        logger.info("Starting social media scheduler...")
        logger.info(f"Checking for scheduled posts every {interval} seconds")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                # Process pending posts
                processed = self.manager.process_pending_posts()
                
                # Log the number of processed posts
                if processed > 0:
                    logger.info(f"Processed {processed} pending posts")
                
                # Wait for the next interval
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}", exc_info=True)
            raise
        finally:
            # Ensure we clean up resources
            self.manager.shutdown()

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Social Media Automation System')
    
    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule a new post')
    schedule_parser.add_argument('platform', choices=['instagram', 'facebook', 'twitter', 'tiktok'],
                               help='Platform to post to')
    schedule_parser.add_argument('content_path', help='Path to the content file (image or video)')
    schedule_parser.add_argument('caption', help='Post caption')
    schedule_parser.add_argument('--time', help='Scheduled time (ISO format or "now")', default='now')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List scheduled posts')
    list_parser.add_argument('--status', choices=['scheduled', 'posted', 'failed', 'cancelled'],
                           help='Filter by status')
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a scheduled post')
    cancel_parser.add_argument('post_id', help='ID of the post to cancel')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the scheduler')
    run_parser.add_argument('--interval', type=int, default=60,
                          help='How often to check for posts (in seconds)')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test platform connections')
    test_parser.add_argument('platform', nargs='?', choices=['all', 'instagram', 'facebook', 'twitter', 'tiktok'],
                           default='all', help='Platform to test')
    
    return parser.parse_args()

def test_platform_connection(automation: SocialMediaAutomation, platform: str) -> bool:
    """Test connection to a specific platform."""
    logger.info(f"Testing connection to {platform}...")
    
    if platform not in automation.manager.platforms:
        logger.error(f"{platform} is not enabled in the configuration")
        return False
    
    platform_obj = automation.manager.platforms[platform]
    
    # Test authentication
    try:
        if not platform_obj.authenticated and not platform_obj.authenticate():
            logger.error(f"Failed to authenticate with {platform}")
            return False
        
        logger.info(f"Successfully connected to {platform}")
        
        # Test a mock post if in mock mode
        if getattr(platform_obj, 'mock_mode', False):
            logger.info(f"Testing mock post to {platform}...")
            test_file = Path(__file__).parent / 'test_output' / f'test_{platform}.txt'
            test_file.parent.mkdir(exist_ok=True, parents=True)
            test_file.write_text(f"Test file for {platform}")
            
            result = automation.schedule_post(
                platform=platform,
                content_path=str(test_file),
                caption=f"Test post from Social Media Automation - {datetime.now().isoformat()}",
                post_time=datetime.now() + timedelta(minutes=5)
            )
            
            if result.get('status') == 'scheduled':
                logger.info(f"Successfully scheduled test post on {platform}")
                
                # Clean up the test post
                automation.cancel_post(result['post_id'])
                test_file.unlink(missing_ok=True)
                
                return True
            else:
                logger.error(f"Failed to schedule test post on {platform}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing {platform}: {str(e)}", exc_info=True)
        return False

def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    try:
        # Initialize the automation system
        automation = SocialMediaAutomation()
        
        # Handle different commands
        if args.command == 'schedule':
            # Parse the post time
            if args.time.lower() == 'now':
                post_time = datetime.now() + timedelta(minutes=5)  # 5 minutes from now
            else:
                try:
                    post_time = datetime.fromisoformat(args.time)
                except ValueError:
                    logger.error(f"Invalid time format. Please use ISO format (e.g., '2023-01-01T12:00:00')")
                    return 1
            
            # Schedule the post
            result = automation.schedule_post(
                platform=args.platform,
                content_path=args.content_path,
                caption=args.caption,
                post_time=post_time
            )
            
            print(json.dumps(result, indent=2))
            
        elif args.command == 'list':
            posts = automation.list_scheduled_posts(status=args.status)
            print(json.dumps(posts, indent=2))
            
        elif args.command == 'cancel':
            result = automation.cancel_post(args.post_id)
            print(json.dumps(result, indent=2))
            
        elif args.command == 'run':
            automation.run_scheduler(interval=args.interval)
            
        elif args.command == 'test':
            platforms = ['instagram', 'facebook', 'twitter', 'tiktok'] if args.platform == 'all' else [args.platform]
            
            all_success = True
            for platform in platforms:
                if not test_platform_connection(automation, platform):
                    all_success = False
            
            if all_success:
                logger.info("All platform tests completed successfully")
                return 0
            else:
                logger.error("Some platform tests failed")
                return 1
                
        else:
            logger.error("No command specified. Use --help for usage information.")
            return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
