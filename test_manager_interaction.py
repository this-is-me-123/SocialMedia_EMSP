"""
Detailed test script to verify manager-platform interaction.
"""
import os
import sys
import logging
import tempfile
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # More verbose logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_manager_interaction.log', mode='w')
    ]
)
logger = logging.getLogger('test_manager')

class TestPlatform:
    """Test platform with detailed logging."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.authenticated = False
        self.posts = []
        self.logger = logging.getLogger('test_platform')
        self.logger.info("Initializing TestPlatform with config: %s", config)
    
    def authenticate(self):
        """Simulate authentication with detailed logging."""
        self.logger.info("Starting authentication")
        try:
            self.authenticated = True
            self.logger.info("Authentication successful")
            return True
        except Exception as e:
            self.logger.error("Authentication failed: %s", str(e), exc_info=True)
            return False
    
    def post_image(self, image_path, caption, **kwargs):
        """Simulate posting an image with detailed logging."""
        self.logger.info("Starting post_image")
        self.logger.debug("  image_path: %s", image_path)
        self.logger.debug("  caption: %s", caption)
        self.logger.debug("  kwargs: %s", kwargs)
        
        if not self.authenticated:
            error_msg = 'Not authenticated'
            self.logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}
        
        if not os.path.exists(image_path):
            error_msg = f'Image not found: {image_path}'
            self.logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}
        
        try:
            post_data = {
                'image_path': image_path,
                'caption': caption,
                'status': 'success',
                **kwargs
            }
            
            self.posts.append(post_data)
            self.logger.info("Successfully added post: %s", post_data)
            
            return {
                'status': 'success',
                'message': 'Post successful',
                'post_id': len(self.posts)
            }
            
        except Exception as e:
            error_msg = f'Error in post_image: {str(e)}'
            self.logger.error(error_msg, exc_info=True)
            return {'status': 'error', 'message': error_msg}

def create_test_file(file_path, content="Test content"):
    """Create a test file with logging."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        logger.info("Created test file: %s", file_path)
        return True
    except Exception as e:
        logger.error("Error creating test file: %s", str(e), exc_info=True)
        return False

def test_manager_interaction():
    """Test interaction between manager and platform."""
    logger.info("=== Starting Manager-Platform Interaction Test ===")
    
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        logger.info("Using temporary directory: %s", temp_dir)
        
        # Create a test file
        test_file = temp_dir / "test_post.txt"
        if not create_test_file(test_file, "This is a test post"):
            return False
        
        # Import the simple manager
        try:
            from automation_stack.social_media.simple_manager import SimpleSocialMediaManager
            logger.info("✅ Successfully imported SimpleSocialMediaManager")
        except ImportError as e:
            logger.error("❌ Error importing SimpleSocialMediaManager: %s", e)
            return False
        
        # Create and configure the manager and platform
        try:
            logger.info("Creating and configuring test platform...")
            test_platform = TestPlatform({'test_setting': 'test_value'})
            
            logger.info("Creating and configuring manager...")
            manager = SimpleSocialMediaManager()
            manager.register_platform('test', test_platform)
            
            logger.info("✅ Test environment setup complete")
            
            # Test 1: Verify platform registration
            logger.info("\n=== Test 1: Verify platform registration ===")
            if 'test' not in manager.platforms:
                logger.error("❌ Test platform not registered")
                return False
            logger.info("✅ Test platform registered successfully")
            
            # Test 2: Post to platform
            logger.info("\n=== Test 2: Post to platform ===")
            test_caption = "Test post from interaction test"
            
            result = manager.post_to_platform(
                platform_name='test',
                content_path=str(test_file),
                caption=test_caption,
                test_param='test_value'
            )
            
            logger.info("Post result: %s", result)
            
            if result.get('status') != 'success':
                logger.error("❌ Post failed: %s", result)
                return False
            
            logger.info("✅ Post was successful")
            
            # Test 3: Verify post was recorded
            logger.info("\n=== Test 3: Verify post was recorded ===")
            if len(test_platform.posts) != 1:
                logger.error("❌ Expected 1 post, found %d", len(test_platform.posts))
                return False
            
            logger.info("✅ Post was recorded: %s", test_platform.posts[0])
            
            return True
            
        except Exception as e:
            logger.error("❌ Error during test: %s", str(e), exc_info=True)
            return False

if __name__ == "__main__":
    print("=== Manager-Platform Interaction Test ===\n")
    
    if test_manager_interaction():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed - check the log file for details")
        sys.exit(1)
