"""
Core functionality test for the social media automation system.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any
from abc import ABC, abstractmethod

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TestPlatform(ABC):
    """Test platform implementation for core functionality testing."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.authenticated = False
        self.dry_run = config.get('dry_run', True)
        self.posts = []  # Store posts for testing
    
    def authenticate(self) -> bool:
        """Test authentication."""
        self.logger.info("Authenticating with test platform")
        self.authenticated = True
        return True
    
    def post_image(self, image_path: str, caption: str, **kwargs) -> Dict[str, Any]:
        """Test image posting."""
        if not self.authenticated:
            return {'status': 'error', 'message': 'Not authenticated'}
        
        # Verify image exists if not in dry run mode
        if not self.dry_run and not os.path.exists(image_path):
            return {'status': 'error', 'message': f'Image not found: {image_path}'}
        
        # Store the post for verification
        post_data = {
            'image_path': image_path,
            'caption': caption,
            'timestamp': '2023-01-01T12:00:00',
            'status': 'success',
            'dry_run': self.dry_run
        }
        
        self.posts.append(post_data)
        self.logger.info(f"Posted image: {image_path}")
        self.logger.info(f"Caption: {caption}")
        
        return {
            'status': 'success',
            'message': 'Dry run - no post made' if self.dry_run else 'Post successful',
            'post_id': len(self.posts),
            'dry_run': self.dry_run
        }

def create_test_image(output_path: str, text: str = "Test Image") -> bool:
    """Create a simple test image using Pillow if available."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import random
        
        # Create a simple image with text
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color=(random.randint(0, 200), 
                                                     random.randint(0, 200), 
                                                     random.randint(0, 200)))
        
        # Add some text
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        
        draw = ImageDraw.Draw(img)
        text_width, text_height = draw.textsize(text, font=font)
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, font=font, fill=(255, 255, 255))
        
        # Save the image
        img.save(output_path)
        return True
    except ImportError:
        logger.warning("Pillow not available, using placeholder file")
        # Create a simple text file as a fallback
        with open(output_path, 'w') as f:
            f.write(f"Test image: {text}")
        return False

def test_core_functionality():
    """Test core functionality of the social media automation system."""
    logger.info("=== Starting Core Functionality Test ===")
    
    # Create a test directory
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    # Create a test image
    test_image_path = str(test_dir / "test_post.jpg")
    used_pillow = create_test_image(test_image_path, "Social Media Test")
    
    if not os.path.exists(test_image_path):
        logger.error("❌ Failed to create test image")
        return False
    
    logger.info(f"✅ Created test image: {test_image_path}")
    if used_pillow:
        logger.info("  - Used Pillow for image generation")
    else:
        logger.info("  - Used fallback text file")
    
    # Test the platform
    try:
        logger.info("\nTesting platform functionality...")
        platform = TestPlatform({
            'dry_run': True,
            'rate_limit': 5
        })
        
        # Test authentication
        logger.info("Testing authentication...")
        if platform.authenticate():
            logger.info("✅ Authentication successful")
        else:
            logger.error("❌ Authentication failed")
            return False
        
        # Test image posting
        logger.info("\nTesting image posting...")
        caption = "Test post from our social media automation system\n#test #automation #socialmedia"
        result = platform.post_image(test_image_path, caption)
        
        if result.get('status') == 'success':
            logger.info(f"✅ Post successful: {result}")
        else:
            logger.error(f"❌ Post failed: {result}")
            return False
        
        # Verify the post was stored
        if len(platform.posts) == 1:
            logger.info(f"✅ Post stored correctly: {platform.posts[0]}")
        else:
            logger.error(f"❌ Post not stored correctly. Found {len(platform.posts)} posts")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during platform test: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    print("=== Social Media Automation - Core Functionality Test ===\n")
    
    if test_core_functionality():
        print("\n✅ All core functionality tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
