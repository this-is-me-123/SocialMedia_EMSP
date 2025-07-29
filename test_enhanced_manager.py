"""
Test script for the EnhancedSocialMediaManager.
"""
import os
import sys
import time
import shutil
import unittest
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_enhanced_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_enhanced_manager')

# Import the manager and related classes
from automation_stack.social_media.enhanced_manager import (
    EnhancedSocialMediaManager,
    Post,
    PostStatus
)

class TestEnhancedSocialMediaManager(unittest.TestCase):
    """Test cases for the EnhancedSocialMediaManager class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        logger.info("Setting up EnhancedSocialMediaManager test")
        
        # Create test output directory
        cls.test_output_dir = project_root / 'test_output'
        cls.test_output_dir.mkdir(exist_ok=True)
        
        # Create a test image
        from PIL import Image, ImageDraw, ImageFont
        
        cls.test_image = cls.test_output_dir / 'test_image.jpg'
        img = Image.new('RGB', (1200, 675), color='#1DA1F2')
        d = ImageDraw.Draw(img)
        
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
            
        d.text((100, 100), "Test Image", fill="white", font=font)
        d.text((100, 200), "For EnhancedSocialMediaManager Tests", fill="white", font=font)
        img.save(cls.test_image)
        logger.info(f"Created test image: {cls.test_image}")
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        logger.info("Setting up EnhancedSocialMediaManager test")
        
        # Create test output directory
        cls.test_output_dir = project_root / 'test_output'
        cls.test_output_dir.mkdir(exist_ok=True)
        
        # Create a test image
        from PIL import Image, ImageDraw, ImageFont
        
        cls.test_image = cls.test_output_dir / 'test_image.jpg'
        img = Image.new('RGB', (1200, 675), color='#1DA1F2')
        d = ImageDraw.Draw(img)
        
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
            
        d.text((100, 100), "Test Image", fill="white", font=font)
        d.text((100, 200), "For EnhancedSocialMediaManager Tests", fill="white", font=font)
        img.save(cls.test_image)
        logger.info(f"Created test image: {cls.test_image}")
        
        # Set up test configuration
        cls.test_config = {
            'storage_path': str(cls.test_output_dir / 'social_media_data'),
            'platforms': {
                'twitter': {
                    'enabled': True,
                    'mock_mode': True,
                    'api_key': 'test_api_key',
                    'api_secret': 'test_api_secret',
                    'access_token': 'test_access_token',
                    'access_secret': 'test_access_secret'
                },
                'facebook': {
                    'enabled': True,
                    'mock_mode': True,
                    'app_id': 'test_app_id',
                    'app_secret': 'test_app_secret',
                    'access_token': 'test_access_token',
                    'page_id': 'test_page_id'
                },
                'instagram': {
                    'enabled': True,
                    'mock_mode': True,
                    'username': 'test_user',
                    'password': 'test_password',
                    'api_key': 'test_api_key'
                }
            }
        }
    
    def setUp(self):
        """Set up before each test method."""
        # Create a fresh manager instance for each test
        self.manager = EnhancedSocialMediaManager(
            storage_path=self.test_config['storage_path']
        )
        
        # Register test platforms
        from automation_stack.social_media.platforms import (
            Twitter, Facebook, Instagram
        )
        
        for platform_name, config in self.test_config['platforms'].items():
            if config['enabled']:
                platform_class = {
                    'twitter': Twitter,
                    'facebook': Facebook,
                    'instagram': Instagram
                }.get(platform_name)
                
                if platform_class:
                    self.manager.platforms[platform_name] = platform_class(config)
                    logger.info(f"Initialized {platform_name} platform for testing")
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up the manager
        self.manager.shutdown()
        
        # Remove test data
        if os.path.exists(self.test_config['storage_path']):
            shutil.rmtree(self.test_config['storage_path'])
    
    def test_initialization(self):
        """Test that the manager initializes correctly."""
        self.assertIsInstance(self.manager, EnhancedSocialMediaManager)
        self.assertTrue(hasattr(self.manager, 'platforms'))
        self.assertGreater(len(self.manager.platforms), 0, "No platforms were initialized")
        logger.info("Manager initialized with platforms: %s", ", ".join(self.manager.platforms.keys()))
        return True
    
    def test_schedule_post(self):
        """Test scheduling a post."""
        # Schedule a post for 1 minute from now
        post_time = datetime.now() + timedelta(minutes=1)
        
        post = self.manager.schedule_post(
            platform_name='twitter',
            content_path=str(self.test_image),
            caption='Test scheduled post #test #automation',
            post_time=post_time,
            media_alt_text='Test image'
        )
        
        # Verify the post was created correctly
        self.assertIsInstance(post, Post)
        self.assertEqual(post.platform, 'twitter')
        self.assertEqual(post.status, PostStatus.SCHEDULED)
        self.assertEqual(post.scheduled_time.replace(second=0, microsecond=0),
                        post_time.replace(second=0, microsecond=0))
        
        # Verify the post is in the scheduled posts
        scheduled_posts = self.manager.get_scheduled_posts()
        self.assertIn(post, scheduled_posts)
        
        logger.info("Successfully scheduled post: %s", post)
        return True
    
    def test_cancel_post(self):
        """Test canceling a scheduled post."""
        # Schedule a post
        post = self.manager.schedule_post(
            platform_name='facebook',
            content_path=str(self.test_image),
            caption='Test post to be cancelled',
            post_time=datetime.now() + timedelta(minutes=30)
        )
        
        # Cancel the post
        result = self.manager.cancel_post(post.post_id or str(id(post)))
        self.assertTrue(result, "Failed to cancel post")
        
        # Verify the post status is CANCELLED
        updated_post = next(
            (p for p in self.manager.get_scheduled_posts() 
             if p.post_id == post.post_id or p.caption == post.caption),
            None
        )
        
        self.assertIsNotNone(updated_post, "Post not found after cancellation")
        self.assertEqual(updated_post.status, PostStatus.CANCELLED)
        
        logger.info("Successfully cancelled post: %s", updated_post)
        return True
    
    def test_post_processing(self):
        """Test the post processing workflow."""
        # Create a callback to track post status changes
        status_changes = []
        
        def status_callback(post: Post, **kwargs):
            status_changes.append((post.status, kwargs.get('result', {}).get('status', '')))
        
        # Register the callback
        self.manager.register_callback('post_scheduled', status_callback)
        self.manager.register_callback('post_started', status_callback)
        self.manager.register_callback('post_completed', status_callback)
        
        # Schedule a post for now
        post = self.manager.schedule_post(
            platform_name='instagram',
            content_path=str(self.test_image),
            caption='Test post processing #test',
            post_time=datetime.now(),
            media_alt_text='Test image for post processing'
        )
        
        # Process the post queue
        start_time = time.time()
        timeout = 10  # seconds
        
        while (time.time() - start_time) < timeout:
            if post.status in [PostStatus.POSTED, PostStatus.FAILED]:
                break
            
            # Process any pending posts
            try:
                queued_post = self.manager.post_queue.get_nowait()
                self.manager._process_post(queued_post)
                self.manager.post_queue.task_done()
            except queue.Empty:
                pass
            
            time.sleep(0.1)
        
        # Verify the post was processed
        self.assertEqual(post.status, PostStatus.POSTED, 
                        f"Post was not processed successfully. Final status: {post.status}")
        
        # Verify the status changes were tracked
        self.assertGreaterEqual(len(status_changes), 2, "Expected at least 2 status changes")
        
        # Check the first status change (should be SCHEDULED)
        self.assertEqual(status_changes[0][0], PostStatus.SCHEDULED)
        
        # The last status change should be POSTED
        self.assertEqual(status_changes[-1][0], PostStatus.POSTED)
        
        logger.info("Post processing test completed successfully")
        return True

def run_tests():
    """Run all tests and print results."""
    print("=== EnhancedSocialMediaManager Tests ===\n")
    
    # Run tests
    test_cases = [
        'test_initialization',
        'test_schedule_post',
        'test_cancel_post',
        'test_post_processing'
    ]
    
    # Track test results
    results = {}
    
    # Create test instance
    test = TestEnhancedSocialMediaManager()
    
    # Run each test case
    for test_case in test_cases:
        test.setUp()
        try:
            result = getattr(test, test_case)()
            results[test_case] = result is not False  # Treat None as success
        except Exception as e:
            logger.error(f"Test {test_case} failed: {str(e)}", exc_info=True)
            results[test_case] = False
        finally:
            test.tearDown()
    
    # Print test summary
    print("\n=== Test Summary ===")
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name}: {status}")
    
    # Exit with appropriate status code
    if all(results.values()):
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
