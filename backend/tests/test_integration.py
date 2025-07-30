"""
Integration test for the social media automation system.
"""
import os
import sys
import logging
import tempfile
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_integration.log', mode='w')
    ]
)
logger = logging.getLogger('test_integration')

# Import our components
try:
    from automation_stack.social_media.simple_manager import SimpleSocialMediaManager
    from automation_stack.social_media.simple_base_platform import TestSimplePlatform
    logger.info("✅ Successfully imported components")
except ImportError as e:
    logger.error("❌ Error importing components: %s", e)
    sys.exit(1)

class IntegrationTest:
    """Integration test for the social media automation system."""
    
    def __init__(self):
        """Initialize the test environment."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="social_media_test_"))
        self.manager = None
        self.platform = None
        self.test_image = None
        logger.info("Initialized test environment in %s", self.test_dir)
    
    def setup(self):
        """Set up the test environment."""
        logger.info("\n=== Setting up test environment ===")
        
        # Create a test image
        self.test_image = self.test_dir / "test_post.jpg"
        if not self._create_test_image(self.test_image, "Social Media Test"):
            return False
        
        # Initialize the platform
        self.platform = TestSimplePlatform({
            'dry_run': True,
            'test_setting': 'test_value'
        })
        
        # Initialize the manager
        self.manager = SimpleSocialMediaManager()
        self.manager.register_platform('test', self.platform)
        
        logger.info("✅ Test environment setup complete")
        return True
    
    def _create_test_image(self, file_path, text):
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
            logger.info("Created test image: %s", file_path)
            return True
            
        except ImportError:
            # Fallback if PIL is not available
            with open(file_path, 'w') as f:
                f.write(f"Test image: {text}")
            logger.warning("Created text file instead of image: %s", file_path)
            return True
    
    def run_tests(self):
        """Run all integration tests."""
        if not self.setup():
            return False
        
        tests = [
            self.test_platform_registration,
            self.test_authentication,
            self.test_image_posting,
            self.test_error_handling
        ]
        
        results = []
        for test in tests:
            test_name = test.__name__
            logger.info("\n" + "="*80)
            logger.info(f"RUNNING TEST: {test_name}")
            logger.info("="*80)
            
            try:
                result = test()
                status = "PASSED" if result else "FAILED"
                logger.info(f"TEST {status}: {test_name}")
                results.append((test_name, result))
            except Exception as e:
                logger.error(f"❌ ERROR in test {test_name}: {str(e)}", exc_info=True)
                results.append((test_name, False))
        
        # Print summary
        self._print_summary(results)
        return all(result[1] for result in results)
    
    def test_platform_registration(self):
        """Test if the platform is properly registered with the manager."""
        logger.info("Testing platform registration...")
        
        if not hasattr(self.manager, 'platforms'):
            logger.error("Manager has no 'platforms' attribute")
            return False
        
        if 'test' not in self.manager.platforms:
            logger.error("Test platform not registered")
            return False
        
        if self.manager.platforms['test'] is not self.platform:
            logger.error("Registered platform instance doesn't match")
            return False
        
        logger.info("✅ Platform registration test passed")
        return True
    
    def test_authentication(self):
        """Test platform authentication."""
        logger.info("Testing authentication...")
        
        if not self.platform.authenticate():
            logger.error("Authentication failed")
            return False
        
        if not self.platform.authenticated:
            logger.error("Platform not marked as authenticated")
            return False
        
        logger.info("✅ Authentication test passed")
        return True
    
    def test_image_posting(self):
        """Test posting an image to the platform."""
        logger.info("Testing image posting...")
        
        if not self.platform.authenticated and not self.platform.authenticate():
            logger.error("Authentication required before posting")
            return False
        
        caption = "Test post from integration test #test #automation"
        
        result = self.manager.post_to_platform(
            platform_name='test',
            content_path=str(self.test_image),
            caption=caption,
            test_param='test_value'
        )
        
        logger.debug("Post result: %s", result)
        
        if result.get('status') != 'success':
            logger.error("Post failed: %s", result.get('message', 'Unknown error'))
            return False
        
        if not hasattr(self.platform, 'posts') or not self.platform.posts:
            logger.error("No posts found on the platform after posting")
            return False
        
        post = self.platform.posts[-1]
        if post['caption'] != caption:
            logger.error("Caption mismatch. Expected: %s, Got: %s", caption, post.get('caption'))
            return False
        
        logger.info("✅ Image posting test passed")
        return True
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        logger.info("Testing error handling...")
        
        # Test with non-existent platform
        result = self.manager.post_to_platform(
            platform_name='nonexistent',
            content_path=str(self.test_image),
            caption="This should fail"
        )
        
        if result.get('status') != 'error':
            logger.error("Expected error for non-existent platform, got: %s", result)
            return False
        
        # Test with non-existent image
        result = self.manager.post_to_platform(
            platform_name='test',
            content_path=str(self.test_dir / "nonexistent.jpg"),
            caption="This should fail"
        )
        
        if result.get('status') != 'error':
            logger.error("Expected error for non-existent image, got: %s", result)
            return False
        
        logger.info("✅ Error handling test passed")
        return True
    
    def _print_summary(self, results):
        """Print a summary of test results."""
        logger.info("\n" + "="*80)
        logger.info("TEST SUMMARY")
        logger.info("="*80)
        
        for name, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            logger.info(f"{status}: {name}")
        
        total = len(results)
        passed = sum(1 for _, p in results if p)
        logger.info("\nTOTAL: %d/%d tests passed", passed, total)
        logger.info("="*80)

if __name__ == "__main__":
    print("=== Social Media Automation Integration Test ===\n")
    
    test = IntegrationTest()
    success = test.run_tests()
    
    if success:
        print("\n✅ All integration tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some integration tests failed - check the log file for details")
        sys.exit(1)
