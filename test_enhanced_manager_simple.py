"""
Simple test script for the EnhancedSocialMediaManager.
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_enhanced_manager')

def main():
    """Run a simple test of the EnhancedSocialMediaManager."""
    from automation_stack.social_media.enhanced_manager import EnhancedSocialMediaManager, PostStatus
    
    print("=== EnhancedSocialMediaManager Simple Test ===\n")
    
    # Create test output directory
    test_output_dir = project_root / 'test_output'
    test_output_dir.mkdir(exist_ok=True)
    
    # Create a test image
    from PIL import Image, ImageDraw, ImageFont
    
    test_image = test_output_dir / 'test_image.jpg'
    img = Image.new('RGB', (1200, 675), color='#1DA1F2')
    d = ImageDraw.Draw(img)
    
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
        
    d.text((100, 100), "Test Image", fill="white", font=font)
    d.text((100, 200), "For EnhancedSocialMediaManager Test", fill="white", font=font)
    img.save(test_image)
    logger.info(f"Created test image: {test_image}")
    
    # Set up test configuration
    test_config = {
        'storage_path': str(test_output_dir / 'social_media_data'),
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
    
    # Initialize the manager
    print("Initializing EnhancedSocialMediaManager...")
    manager = EnhancedSocialMediaManager(storage_path=test_config['storage_path'])
    
    # Register test platforms
    from automation_stack.social_media.platforms import Twitter, Facebook, Instagram
    
    for platform_name, config in test_config['platforms'].items():
        if config['enabled']:
            platform_class = {
                'twitter': Twitter,
                'facebook': Facebook,
                'instagram': Instagram
            }.get(platform_name)
            
            if platform_class:
                manager.platforms[platform_name] = platform_class(config)
                print(f"Initialized {platform_name} platform for testing")
    
    # Test 1: Schedule a post
    print("\n=== Test 1: Schedule a post ===")
    post_time = datetime.now() + timedelta(minutes=5)
    
    post = manager.schedule_post(
        platform_name='twitter',
        content_path=str(test_image),
        caption='Test post from EnhancedSocialMediaManager #test #automation',
        post_time=post_time,
        media_alt_text='Test image for social media post'
    )
    
    print(f"Scheduled post: {post}")
    print(f"Post ID: {post.post_id}")
    print(f"Status: {post.status.name}")
    print(f"Scheduled for: {post.scheduled_time}")
    
    # Test 2: Get scheduled posts
    print("\n=== Test 2: Get scheduled posts ===")
    scheduled_posts = manager.get_scheduled_posts()
    print(f"Found {len(scheduled_posts)} scheduled posts")
    
    for i, scheduled_post in enumerate(scheduled_posts, 1):
        print(f"\nPost {i}:")
        print(f"  Platform: {scheduled_post.platform}")
        print(f"  Caption: {scheduled_post.caption[:50]}...")
        print(f"  Status: {scheduled_post.status.name}")
        print(f"  Scheduled for: {scheduled_post.scheduled_time}")
    
    # Test 3: Cancel a post
    print("\n=== Test 3: Cancel a post ===")
    if scheduled_posts:
        post_to_cancel = scheduled_posts[0]
        print(f"Cancelling post: {post_to_cancel.post_id}")
        result = manager.cancel_post(post_to_cancel.post_id or str(id(post_to_cancel)))
        print(f"Cancellation {'succeeded' if result else 'failed'}")
    
    # Test 4: Process posts (simulate)
    print("\n=== Test 4: Process posts (simulated) ===")
    print("Manually processing posts in the queue...")
    
    # Simulate processing by directly calling _process_post
    if hasattr(manager, '_process_post'):
        for post in scheduled_posts:
            if post.status == PostStatus.SCHEDULED:
                print(f"Processing post: {post.post_id}")
                manager._process_post(post)
                print(f"Post status after processing: {post.status.name}")
    else:
        print("Skipping post processing test (method not found)")
    
    # Clean up
    print("\n=== Test Complete ===")
    manager.shutdown()
    print("Social media manager shut down")

if __name__ == "__main__":
    main()
