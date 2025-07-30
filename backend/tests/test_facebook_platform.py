"""
Test script for the Facebook platform implementation.
"""
import os
import sys
import logging
import unittest
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_facebook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_facebook')

class TestFacebookPlatform(unittest.TestCase):
    """Test cases for the Facebook platform."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        logger.info("Setting up Facebook platform test")
        
        # Create test output directory if it doesn't exist
        cls.test_output_dir = project_root / 'test_output'
        cls.test_output_dir.mkdir(exist_ok=True)
        
        # Create a test image
        from PIL import Image, ImageDraw, ImageFont
        
        cls.test_image = cls.test_output_dir / 'facebook_test.jpg'
        img = Image.new('RGB', (1200, 630), color='#3b5998')
        d = ImageDraw.Draw(img)
        
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
            
        d.text((100, 100), "Facebook Test Image", fill="white", font=font)
        d.text((100, 200), "This is a test image for Facebook", fill="white", font=font)
        img.save(cls.test_image)
        logger.info(f"Created test image: {cls.test_image}")
        
        # Import the Facebook platform
        try:
            from automation_stack.social_media.platforms.facebook import Facebook
            
            # Use test configuration with mock mode enabled
            config = {
                'username': 'test_user',
                'password': 'test_pass',
                'dry_run': True,
                'access_token': 'test_access_token',
                'page_id': 'test_page_id',
                'rate_limit': 200,
                'mock_mode': True  # Enable mock mode for testing
            }
            
            cls.facebook = Facebook(config)
            logger.info("Initialized Facebook platform for testing")
            
        except ImportError as e:
            logger.error(f"Failed to import Facebook platform: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Facebook platform: {str(e)}")
            raise
    
    def test_authentication(self):
        """Test Facebook authentication."""
        try:
            # In mock mode, we expect authentication to succeed
            result = self.facebook.authenticate()
            
            # The method should return a boolean
            if not isinstance(result, bool):
                logger.error("Authentication should return a boolean")
                return False
                
            # In mock mode, we expect authentication to succeed
            if not result:
                logger.error("Authentication should succeed in mock mode")
                return False
                
            # Verify the page was set correctly in mock mode
            if not hasattr(self.facebook, 'page_name') or not self.facebook.page_name:
                logger.error("Page name not set after authentication")
                return False
                
            logger.info("Authentication successful in mock mode")
            return True
            
        except Exception as e:
            logger.error(f"Error during authentication test: {str(e)}", exc_info=True)
            return False
    
    def test_image_posting(self):
        """Test posting an image to Facebook."""
        try:
            # Create a test caption with hashtags
            caption = "Test post from Facebook platform test #test #automation #encompassmsp"
            
            # Call the post method with the test image
            result = self.facebook.post(str(self.test_image), caption)
            
            # Verify the result is a dictionary with a status key
            if not isinstance(result, dict) or 'status' not in result:
                logger.error("post should return a dictionary with a 'status' key")
                return False
            
            # In mock mode, we expect the post to succeed
            if result.get('status') != 'success':
                logger.error("Post should succeed in mock mode")
                return False
                
            # Verify the post was added to mock_posts
            if not hasattr(self.facebook, 'mock_posts') or not self.facebook.mock_posts:
                logger.error("Post was not added to mock_posts")
                return False
                
            # Verify the post data
            post = self.facebook.mock_posts[0]
            if 'id' not in post or 'caption' not in post or 'url' not in post:
                logger.error("Post data is incomplete")
                return False
                
            logger.info(f"Post successful in mock mode. Post ID: {post['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error during image posting test: {str(e)}", exc_info=True)
            return False

if __name__ == "__main__":
    print("=== Facebook Platform Test ===\n")
    
    # Run tests
    test_cases = [
        'test_authentication',
        'test_image_posting'
    ]
    
    # Track test results
    results = {}
    
    # Run each test case
    for test_case in test_cases:
        test = TestFacebookPlatform(test_case)
        test.setUpClass()
        result = getattr(test, test_case)()
        results[test_case] = "PASSED" if result else "FAILED"
    
    # Print test summary
    print("\n=== Test Summary ===")
    for test_name, status in results.items():
        print(f"{test_name}: {status}")
    
    # Exit with appropriate status code
    if all(status == "PASSED" for status in results.values()):
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
