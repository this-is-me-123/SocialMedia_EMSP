"""
Test script for the simplified base platform implementation.
"""
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_simple_platform():
    """Test the simplified base platform implementation."""
    try:
        # Import the simplified platform
        from automation_stack.social_media.simple_base_platform import TestSimplePlatform
        
        # Create a test instance
        logger.info("Creating test platform instance...")
        platform = TestSimplePlatform({
            'dry_run': True
        })
        
        # Test authentication
        logger.info("Testing authentication...")
        if platform.authenticate():
            logger.info("✅ Authentication successful")
        else:
            logger.error("❌ Authentication failed")
            return False
        
        # Test caption formatting
        logger.info("\nTesting caption formatting...")
        test_caption = "Test caption with #hashtag1 and #hashtag2 #hashtag3 #hashtag4 #hashtag5 #hashtag6"
        formatted = platform.format_caption(test_caption, max_hashtags=3)
        logger.info(f"Original: {test_caption}")
        logger.info(f"Formatted: {formatted}")
        
        # Test image posting (dry run)
        logger.info("\nTesting image posting (dry run)...")
        result = platform.post_image(
            image_path="test_image.png",
            caption=formatted
        )
        logger.info(f"Post result: {result}")
        
        logger.info("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    print("=== Testing Simplified Base Platform ===\n")
    
    if test_simple_platform():
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
