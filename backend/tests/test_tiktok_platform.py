""
Test script for the TikTok platform implementation.
"""
import os
import sys
import logging
import unittest
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
        logging.FileHandler('test_tiktok_platform.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_tiktok_platform')

class TestTikTokPlatform(unittest.TestCase):
    """Test cases for the TikTok platform implementation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        logger.info("Setting up TikTok platform test")
        
        # Create test output directory
        cls.test_output_dir = project_root / 'test_output'
        cls.test_output_dir.mkdir(exist_ok=True)
        
        # Create a test video
        from PIL import Image, ImageDraw, ImageFont
        
        cls.test_video = cls.test_output_dir / 'test_video.mp4'
        
        # Create a simple image as a placeholder for the video
        img = Image.new('RGB', (1280, 720), color='#FF0050')  # TikTok red
        d = ImageDraw.Draw(img)
        
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
            
        d.text((100, 100), "Test Video", fill="white", font=font)
        d.text((100, 200), "For TikTok Platform Test", fill="white", font=font)
        
        # Save as an image (in a real test, this would be a video)
        img_path = cls.test_output_dir / 'test_video_thumbnail.jpg'
        img.save(img_path)
        
        # Create a simple text file to simulate a video file
        with open(cls.test_video, 'w') as f:
            f.write("This is a test video file for TikTok testing.")
        
        logger.info(f"Created test video file: {cls.test_video}")
    
    def setUp(self):
        """Set up before each test method."""
        from automation_stack.social_media.platforms.tiktok import Tiktok
        
        # Test configuration with mock mode enabled
        self.test_config = {
            'mock_mode': True,
            'client_key': 'test_client_key',
            'client_secret': 'test_client_secret',
            'username': 'test_tiktok_user',
            'rate_limit': 1000  # Higher limit for testing
        }
        
        # Initialize the TikTok platform
        self.tiktok = Tiktok(self.test_config)
    
    def test_initialization(self):
        """Test that the TikTok platform initializes correctly."""
        self.assertIsNotNone(self.tiktok)
        self.assertEqual(self.tiktok.api_url, 'https://open-api.tiktok.com')
        self.assertTrue(self.tiktok.mock_mode)
    
    def test_authentication_mock_mode(self):
        """Test authentication in mock mode."""
        self.assertFalse(self.tiktok.authenticated)
        
        # Authenticate
        result = self.tiktok.authenticate()
        self.assertTrue(result)
        self.assertTrue(self.tiktok.authenticated)
        self.assertIsNotNone(self.tiktok.access_token)
        self.assertIsNotNone(self.tiktok.refresh_token)
        self.assertEqual(self.tiktok.username, 'mock_tiktok_user')
    
    def test_post_video_mock_mode(self):
        """Test posting a video in mock mode."""
        # First authenticate
        self.assertTrue(self.tiktok.authenticate())
        
        # Post a video
        caption = "Test video post #TikTok #Test #Automation"
        result = self.tiktok.post(
            content_path=str(self.test_video),
            caption=caption,
            privacy_level='PUBLIC_TO_EVERYONE',
            disable_comment=False,
            disable_duet=False,
            disable_stitch=False,
            disable_share=False
        )
        
        # Check the result
        self.assertEqual(result['status'], 'success')
        self.assertIn('id', result)
        self.assertIn('url', result)
        self.assertEqual(result['platform'], 'tiktok')
        self.assertIn('mock_tiktok_video_', result['id'])
        
        # Check that the mock video was stored
        self.assertEqual(len(self.tiktok.mock_videos), 1)
        self.assertEqual(self.tiktok.mock_videos[0]['id'], result['id'])
        self.assertEqual(self.tiktok.mock_videos[0]['caption'], caption)
    
    def test_rate_limiting(self):
        """Test that rate limiting is enforced."""
        import time
        
        # Set a very low rate limit for testing (1 call per second)
        self.tiktok.rate_limit = 1
        
        # First call should succeed immediately
        start_time = time.time()
        self.tiktok._rate_limit()
        first_call_time = time.time() - start_time
        
        # Second call should be rate limited
        start_time = time.time()
        self.tiktok._rate_limit()
        second_call_time = time.time() - start_time
        
        # The second call should have taken about 1 second due to rate limiting
        self.assertGreaterEqual(second_call_time, 0.9, "Rate limiting not enforced")
    
    def test_caption_formatting(self):
        """Test that captions are formatted correctly for TikTok."""
        # Test with a long caption that needs to be truncated
        long_caption = "This is a very long caption that should be truncated to fit within TikTok's character limit. " \
                      "#TikTok #Test #Automation #SocialMedia #Marketing #DigitalMarketing #ContentCreation #Viral " \
                      "#Trending #FYP #ForYouPage #ExplorePage #SocialMediaMarketing #DigitalStrategy"
        
        formatted_caption = self.tiktok._format_caption(long_caption)
        self.assertLessEqual(len(formatted_caption), 2200, "Caption exceeds maximum length")
        
        # Check that the caption ends with a complete word or hashtag
        self.assertNotEqual(formatted_caption[-1], ' ', "Caption ends with a space")
        self.assertNotEqual(formatted_caption[-1], '#', "Caption ends with an incomplete hashtag")
        
        # Test with a short caption
        short_caption = "Short caption #Test #TikTok"
        formatted_short = self.tiktok._format_caption(short_caption)
        self.assertEqual(short_caption, formatted_short, "Short caption should not be modified")

if __name__ == '__main__':
    unittest.main()
