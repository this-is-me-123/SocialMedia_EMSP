"""
Test script for the social media automation system.
"""
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_instagram_post():
    """Test posting to Instagram."""
    from automation_stack.social_media.manager import SocialMediaManager
    from automation_stack.social_media.instagram_platform import InstagramPlatform
    
    # Configuration for Instagram
    config = {
        'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', 'dummy_token'),
        'page_id': os.getenv('INSTAGRAM_PAGE_ID', 'dummy_page_id'),
        'app_id': os.getenv('FACEBOOK_APP_ID', 'dummy_app_id'),
        'app_secret': os.getenv('FACEBOOK_APP_SECRET', 'dummy_app_secret'),
        'dry_run': True  # Enable dry run mode for testing
    }
    
    # Initialize the manager
    manager = SocialMediaManager()
    
    # Create and register Instagram platform
    instagram = InstagramPlatform(config)
    manager.register_platform('instagram', instagram)
    
    # Test image path (using our test image)
    test_image_path = os.path.join('test_output', 'test_output.png')
    
    # Create test image if it doesn't exist
    if not os.path.exists(test_image_path):
        from test_image_creator import create_test_image
        create_test_image()
    
    # Test caption
    caption = """Test Post from Encompass MSP
    
Testing our social media automation system.
This is a test post with a hashtag.

#EncompassMSP #ManagedIT #TechSolutions"""
    
    # Post to Instagram
    logger.info("Testing Instagram post...")
    result = manager.schedule_post(
        platform_name='instagram',
        content_path=test_image_path,
        caption=caption,
        post_time=None  # Post immediately
    )
    
    logger.info(f"Test result: {json.dumps(result, indent=2)}")
    
    return result

def main():
    """Run the social media tests."""
    print("=== Testing Social Media Integration ===\n")
    
    # Test Instagram
    print("Testing Instagram integration...")
    insta_result = test_instagram_post()
    
    if insta_result.get('status') in ['scheduled', 'success']:
        print("\n✅ Instagram test completed successfully!")
    else:
        print("\n❌ Instagram test failed.")
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    main()
