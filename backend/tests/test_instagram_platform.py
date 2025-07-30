"""
Test script for the Instagram platform implementation.
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_instagram.log', mode='w')
    ]
)
logger = logging.getLogger('test_instagram')

def create_test_image(file_path, text="Test Image"):
    """Create a test image file."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (1080, 1080), color=(200, 200, 200))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((100, 100), text, fill=(0, 0, 0), font=font)
        img.save(file_path)
        logger.info("Created test image: %s", file_path)
        return True
    except ImportError:
        with open(file_path, 'w') as f:
            f.write(f"Test image: {text}")
        logger.warning("Created text file instead of image: %s", file_path)
        return False

class TestInstagramPlatform:
    """Test class for Instagram platform functionality."""
    
    def __init__(self):
        self.test_dir = Path("test_output")
        self.test_dir.mkdir(exist_ok=True)
        self.test_image = self.test_dir / "instagram_test.jpg"
        self.instagram = None
    
    def setup(self):
        """Set up the test environment."""
        if not create_test_image(self.test_image, "Instagram Test"):
            return False
        
        try:
            from automation_stack.social_media.platforms.instagram import Instagram
            
            # Use test configuration with mock mode enabled
            config = {
                'username': 'test_user',
                'password': 'test_pass',
                'dry_run': True,
                'api_key': 'test_api_key',
                'api_secret': 'test_api_secret',
                'access_token': 'test_access_token',
                'page_id': 'test_page_id',
                'rate_limit': 200,
                'mock_mode': True  # Enable mock mode for testing
            }
            
            self.instagram = Instagram(config)
            return True
            
        except Exception as e:
            logger.error("Error setting up Instagram test: %s", e, exc_info=True)
            return False
    
    def run_tests(self):
        """Run all Instagram platform tests."""
        if not self.setup():
            return False
        
        tests = [self.test_authentication, self.test_image_posting]
        results = []
        
        for test in tests:
            try:
                result = test()
                status = "PASSED" if result else "FAILED"
                logger.info("%s: %s", status, test.__name__)
                results.append((test.__name__, result))
            except Exception as e:
                logger.error("❌ Error in %s: %s", test.__name__, e, exc_info=True)
                results.append((test.__name__, False))
        
        # Print summary
        logger.info("\n=== Test Summary ===")
        for name, passed in results:
            logger.info("%s: %s", "✅ PASSED" if passed else "❌ FAILED", name)
        
        return all(result[1] for result in results)
    
    def test_authentication(self):
        """Test Instagram authentication."""
        try:
            # In mock mode, we expect authentication to succeed
            result = self.instagram.authenticate()
            
            # The method should return a boolean
            if not isinstance(result, bool):
                logger.error("Authentication should return a boolean")
                return False
                
            # In mock mode, we expect authentication to succeed
            if not result:
                logger.error("Authentication should succeed in mock mode")
                return False
                
            # Verify the user was set correctly in mock mode
            if not hasattr(self.instagram, 'user_id') or not self.instagram.user_id:
                logger.error("User ID not set after authentication")
                return False
                
            logger.info("Authentication successful in mock mode")
            return True
            
        except Exception as e:
            logger.error("Error during authentication test: %s", str(e), exc_info=True)
            return False
    
    def test_image_posting(self):
        """Test posting an image to Instagram."""
        try:
            # Create a test caption with hashtags
            caption = "Test post from Instagram platform test #test #automation #encompassmsp"
            
            # Call the post_image method
            result = self.instagram.post_image(str(self.test_image), caption)
            
            # Verify the result is a dictionary with a status key
            if not isinstance(result, dict) or 'status' not in result:
                logger.error("post_image should return a dictionary with a 'status' key")
                return False
            
            # In mock mode, we expect the post to succeed
            if result.get('status') != 'success':
                logger.error("Post should succeed in mock mode")
                return False
                
            # Verify the post was added to mock_posts
            if not hasattr(self.instagram, 'mock_posts') or not self.instagram.mock_posts:
                logger.error("Post was not added to mock_posts")
                return False
                
            # Verify the post data
            post = self.instagram.mock_posts[0]
            if 'id' not in post or 'caption' not in post or 'url' not in post:
                logger.error("Post data is incomplete")
                return False
                
            logger.info("Post successful in mock mode. Post ID: %s", post['id'])
            return True
            
        except Exception as e:
            logger.error("Error during image posting test: %s", str(e), exc_info=True)
            return False

if __name__ == "__main__":
    print("=== Instagram Platform Test ===\n")
    
    test = TestInstagramPlatform()
    success = test.run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed - check the log file for details")
        sys.exit(1)
