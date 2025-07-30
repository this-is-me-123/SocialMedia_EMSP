"""
Minimal test script for the base SocialMediaPlatform class.
"""
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_platform.log')
    ]
)

logger = logging.getLogger(__name__)

def test_base_platform():
    """Test the base SocialMediaPlatform class."""
    logger.info("Testing base SocialMediaPlatform class...")
    
    try:
        from automation_stack.social_media.base_platform import SocialMediaPlatform
        logger.info("Successfully imported SocialMediaPlatform")
        
        # Create a test implementation
        class TestPlatform(SocialMediaPlatform):
            """Test platform implementation."""
            
            def authenticate(self) -> bool:
                logger.info("Test platform authenticate called")
                self.authenticated = True
                return True
                
            def post_image(self, image_path: str, caption: str, **kwargs) -> dict:
                logger.info(f"Test platform post_image called with: {image_path}")
                return {
                    'status': 'success',
                    'platform': 'test',
                    'message': 'Test post successful',
                    'image_path': image_path,
                    'caption': caption
                }
        
        # Test the platform
        logger.info("Creating test platform instance...")
        platform = TestPlatform({
            'rate_limit': 5,
            'dry_run': False
        })
        
        logger.info("Testing authentication...")
        auth_result = platform.authenticate()
        logger.info(f"Authentication result: {auth_result}")
        
        logger.info("Testing post_image...")
        post_result = platform.post_image(
            image_path="test_image.png",
            caption="Test caption #test #automation"
        )
        logger.info(f"Post result: {post_result}")
        
        logger.info("Testing caption formatting...")
        caption = "Test caption with #hashtag1 and #hashtag2 #hashtag3 #hashtag4 #hashtag5"
        formatted = platform.format_caption(caption, max_hashtags=3)
        logger.info(f"Original: {caption}")
        logger.info(f"Formatted: {formatted}")
        
        logger.info("✅ Base platform test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in base platform test: {str(e)}", exc_info=True)
        return False

def main():
    """Run the tests."""
    print("=== Testing Social Media Platform ===\n")
    
    # Test the base platform
    print("Testing base platform functionality...")
    if test_base_platform():
        print("\n✅ Base platform test completed successfully!")
    else:
        print("\n❌ Base platform test failed.")
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    main()
