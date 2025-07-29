"""
Test script for the Twitter platform implementation.
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
        logging.FileHandler('test_twitter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_twitter')

class TestTwitterPlatform(unittest.TestCase):
    """Test cases for the Twitter platform."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        logger.info("Setting up Twitter platform test")
        
        # Create test output directory if it doesn't exist
        cls.test_output_dir = project_root / 'test_output'
        cls.test_output_dir.mkdir(exist_ok=True)
        
        # Create a test image
        from PIL import Image, ImageDraw, ImageFont
        
        cls.test_image = cls.test_output_dir / 'twitter_test.jpg'
        img = Image.new('RGB', (1200, 675), color='#1DA1F2')
        d = ImageDraw.Draw(img)
        
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
            
        d.text((100, 100), "Twitter Test Image", fill="white", font=font)
        d.text((100, 200), "This is a test image for Twitter", fill="white", font=font)
        img.save(cls.test_image)
        logger.info(f"Created test image: {cls.test_image}")
        
        # Import the Twitter platform
        try:
            from automation_stack.social_media.platforms.twitter import Twitter
            
            # Use test configuration with mock mode enabled
            config = {
                'api_key': 'test_api_key',
                'api_secret': 'test_api_secret',
                'access_token': 'test_access_token',
                'access_secret': 'test_access_secret',
                'rate_limit': 300,
                'mock_mode': True  # Enable mock mode for testing
            }
            
            cls.twitter = Twitter(config)
            logger.info("Initialized Twitter platform for testing")
            
        except ImportError as e:
            logger.error(f"Failed to import Twitter platform: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Twitter platform: {str(e)}")
            raise
    
    def test_authentication(self):
        """Test Twitter authentication."""
        try:
            # In mock mode, we expect authentication to succeed
            result = self.twitter.authenticate()
            
            # The method should return a boolean
            if not isinstance(result, bool):
                logger.error("Authentication should return a boolean")
                return False
                
            # In mock mode, we expect authentication to succeed
            if not result:
                logger.error("Authentication should succeed in mock mode")
                return False
                
            # Verify the user was set correctly in mock mode
            if not hasattr(self.twitter, 'username') or not self.twitter.username:
                logger.error("Username not set after authentication")
                return False
                
            logger.info("Authentication successful in mock mode")
            return True
            
        except Exception as e:
            logger.error(f"Error during authentication test: {str(e)}", exc_info=True)
            return False
    
    def test_text_tweet(self):
        """Test posting a text tweet to Twitter."""
        try:
            # Create a test tweet with hashtags
            tweet_text = "Test tweet from Twitter platform test #test #automation #encompassmsp"
            
            # Call the post method with just text
            result = self.twitter.post(caption=tweet_text)
            
            # Verify the result is a dictionary with a status key
            if not isinstance(result, dict) or 'status' not in result:
                logger.error("post should return a dictionary with a 'status' key")
                return False
            
            # In mock mode, we expect the tweet to succeed
            if result.get('status') != 'success':
                logger.error("Tweet should succeed in mock mode")
                return False
                
            # Verify the tweet was added to mock_tweets
            if not hasattr(self.twitter, 'mock_tweets') or not self.twitter.mock_tweets:
                logger.error("Tweet was not added to mock_tweets")
                return False
                
            # Verify the tweet data
            tweet = self.twitter.mock_tweets[0]
            if 'id' not in tweet or 'text' not in tweet or 'url' not in tweet:
                logger.error("Tweet data is incomplete")
                return False
                
            logger.info(f"Text tweet successful in mock mode. Tweet ID: {tweet['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error during text tweet test: {str(e)}", exc_info=True)
            return False
    
    def test_image_tweet(self):
        """Test posting an image tweet to Twitter."""
        try:
            # Create a test tweet with an image
            tweet_text = "Test image tweet from Twitter platform test #test #automation #encompassmsp"
            
            # Call the post method with an image
            result = self.twitter.post(
                content_path=str(self.test_image),
                caption=tweet_text,
                media_alt_text="Test image for Twitter"
            )
            
            # Verify the result is a dictionary with a status key
            if not isinstance(result, dict) or 'status' not in result:
                logger.error("post should return a dictionary with a 'status' key")
                return False
            
            # In mock mode, we expect the tweet to succeed
            if result.get('status') != 'success':
                logger.error("Image tweet should succeed in mock mode")
                return False
                
            # Verify the tweet was added to mock_tweets
            if not hasattr(self.twitter, 'mock_tweets') or not self.twitter.mock_tweets:
                logger.error("Tweet was not added to mock_tweets")
                return False
                
            # Verify the tweet data includes media
            tweet = self.twitter.mock_tweets[-1]  # Get the most recent tweet
            if 'media' not in tweet or 'id' not in tweet['media']:
                logger.error("Tweet media data is incomplete")
                return False
                
            logger.info(f"Image tweet successful in mock mode. Tweet ID: {tweet['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error during image tweet test: {str(e)}", exc_info=True)
            return False

if __name__ == "__main__":
    print("=== Twitter Platform Test ===\n")
    
    # Run tests
    test_cases = [
        'test_authentication',
        'test_text_tweet',
        'test_image_tweet'
    ]
    
    # Track test results
    results = {}
    
    # Run each test case
    for test_case in test_cases:
        test = TestTwitterPlatform(test_case)
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
