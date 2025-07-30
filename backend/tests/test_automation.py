"""
Test script for the social media automation system.
This script performs a dry run to test the automation without posting to social media.
"""
import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Import the automation system
from automation_stack.content_creation.create_content import ContentCreator
from automation_stack.social_media.manager import SocialMediaManager
from automation_stack.social_media.platforms import Instagram, Facebook, Twitter, Tiktok
from automation_stack.config import CONTENT, PLATFORMS, LOGGING

# Set up logging
logging.basicConfig(
    level=LOGGING['handlers']['console']['level'],
    format=LOGGING['formatters']['standard']['format'],
    datefmt=LOGGING['formatters']['standard']['datefmt']
)
logger = logging.getLogger(__name__)

def test_content_creation():
    """Test content creation (image generation)."""
    logger.info("Testing content creation...")
    
    try:
        # Initialize content creator
        creator = ContentCreator(CONTENT)
        
        # Test image creation
        test_text = "Testing content creation for Encompass MSP\n#Test #Automation #EncompassMSP"
        image_path = creator.create_image(
            text=test_text,
            category="test",
            index=1
        )
        
        if os.path.exists(image_path):
            logger.info(f"✅ Successfully created test image: {image_path}")
            return image_path
        else:
            logger.error("❌ Failed to create test image")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error in content creation test: {str(e)}", exc_info=True)
        return None

def test_social_media_manager(test_image_path):
    """Test social media manager with a test post."""
    if not test_image_path or not os.path.exists(test_image_path):
        logger.error("❌ No test image available for social media test")
        return False
    
    logger.info("Testing social media manager (dry run)...")
    
    try:
        # Initialize social media manager with test configuration
        manager = SocialMediaManager()
        
        # Register test platforms (in dry run mode)
        test_config = {
            'enabled': True,
            'dry_run': True  # Enable dry run mode
        }
        
        manager.register_platform('instagram', Instagram(test_config))
        manager.register_platform('facebook', Facebook(test_config))
        
        # Test scheduling a post
        test_caption = "🚀 Testing social media automation for Encompass MSP! #Test #Automation #EncompassMSP"
        
        logger.info("Scheduling test post...")
        result = manager.schedule_post(
            platform_name='instagram',
            content_path=test_image_path,
            caption=test_caption,
            post_time='now'
        )
        
        if result.get('status') == 'scheduled' or result.get('dry_run'):
            logger.info("✅ Social media manager test passed (dry run)")
            logger.info(f"Dry run results: {result}")
            return True
        else:
            logger.error(f"❌ Social media manager test failed: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in social media manager test: {str(e)}", exc_info=True)
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting social media automation tests...")
    
    # Test 1: Content Creation
    logger.info("\n=== TEST 1: CONTENT CREATION ===")
    test_image_path = test_content_creation()
    
    # Test 2: Social Media Manager
    if test_image_path:
        logger.info("\n=== TEST 2: SOCIAL MEDIA MANAGER ===")
        test_social_media_manager(test_image_path)
    
    logger.info("\n=== TEST COMPLETE ===")
    logger.info("Note: This was a dry run. No actual posts were made to social media.")
    logger.info("To post to social media, update the .env file with your API credentials and set dry_run=False")

if __name__ == "__main__":
    main()
