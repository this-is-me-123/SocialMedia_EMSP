"""
Test script for the SocialMediaManager class.
"""
import os
import sys
import logging
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TestPlatform:
    """Test platform implementation for testing the manager."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(f"test_platform.{self.__class__.__name__}")
        self.authenticated = False
        self.dry_run = config.get('dry_run', True)
        self.posts = []
    
    def authenticate(self):
        """Test authentication."""
        self.logger.info("Authenticating with test platform")
        self.authenticated = True
        return True
    
    def post_image(self, image_path, caption, **kwargs):
        """Test image posting."""
        if not self.authenticated:
            return {'status': 'error', 'message': 'Not authenticated'}
        
        if not os.path.exists(image_path):
            return {'status': 'error', 'message': f'Image not found: {image_path}'}
        
        post_data = {
            'image_path': image_path,
            'caption': caption,
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'dry_run': self.dry_run,
            'platform': 'test',
            **kwargs
        }
        
        self.posts.append(post_data)
        self.logger.info(f"Posted to test platform: {caption[:50]}...")
        
        return {
            'status': 'success',
            'message': 'Dry run - no post made' if self.dry_run else 'Post successful',
            'post_id': len(self.posts),
            'platform': 'test'
        }

def create_test_image(file_path, text="Test Image"):
    """Create a test image file."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import random
        
        # Create a simple image with text
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color=(
            random.randint(0, 200), 
            random.randint(0, 200), 
            random.randint(0, 200)
        ))
        
        # Add some text
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        
        draw = ImageDraw.Draw(img)
        text_width = draw.textlength(text, font=font)
        text_height = 40  # Approximate height
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, font=font, fill=(255, 255, 255))
        
        # Save the image
        img.save(file_path)
        logger.info(f"Created test image: {file_path}")
        return True
    except ImportError:
        # Fallback if PIL is not available
        with open(file_path, 'w') as f:
            f.write(f"Test image: {text}")
        logger.warning(f"Created text file instead of image: {file_path}")
        return False

def test_manager():
    """Test the SocialMediaManager with a test platform."""
    logger.info("=== Starting SocialMediaManager Test ===")
    
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        logger.info(f"Using temporary directory: {temp_dir}")
        
        # Create a test image
        test_image = temp_dir / "test_post.jpg"
        create_test_image(test_image, "Social Media Manager Test")
        
        if not test_image.exists():
            logger.error("❌ Failed to create test image")
            return False
        
        logger.info(f"✅ Created test image: {test_image}")
        
        # Import the manager
        try:
            from automation_stack.social_media.manager import SocialMediaManager
            logger.info("✅ Successfully imported SocialMediaManager")
        except ImportError as e:
            logger.error(f"❌ Error importing SocialMediaManager: {e}")
            return False
        
        # Create a test platform
        test_platform = TestPlatform({
            'dry_run': True,
            'test_setting': 'test_value'
        })
        
        # Create and configure the manager
        try:
            manager = SocialMediaManager()
            
            # Register the test platform
            manager.register_platform('test', test_platform)
            
            logger.info("✅ Created and configured SocialMediaManager")
            
            # Test authentication
            if not test_platform.authenticate():
                logger.error("❌ Test platform authentication failed")
                return False
            
            logger.info("✅ Test platform authentication successful")
            
            # Test posting
            test_caption = "Test post from SocialMediaManager\n#test #automation #socialmedia"
            
            logger.info("\nTesting post scheduling...")
            result = manager.schedule_post(
                platform_name='test',
                content_path=str(test_image),
                caption=test_caption,
                test_param='test_value'
            )
            
            if result.get('status') != 'success':
                logger.error(f"❌ Post scheduling failed: {result}")
                return False
            
            logger.info(f"✅ Post scheduled successfully: {result}")
            
            # Check if the post was added to the test platform
            if len(test_platform.posts) != 1:
                logger.error(f"❌ Expected 1 post, found {len(test_platform.posts)}")
                return False
            
            logger.info(f"✅ Post was added to the test platform: {test_platform.posts[0]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during manager test: {e}", exc_info=True)
            return False

if __name__ == "__main__":
    print("=== Social Media Manager Test ===\n")
    
    if test_manager():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
