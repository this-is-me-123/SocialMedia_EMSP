"""
Test script for the SimpleSocialMediaManager.
"""
import os
import sys
import logging
import tempfile
from pathlib import Path

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
    """Test platform for SimpleSocialMediaManager testing."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.authenticated = False
        self.posts = []
        self.logger = logging.getLogger('test_platform')
    
    def authenticate(self):
        """Simulate authentication."""
        self.logger.info("Authenticating with test platform")
        self.authenticated = True
        return True
    
    def post_image(self, image_path, caption, **kwargs):
        """Simulate posting an image."""
        if not self.authenticated:
            return {'status': 'error', 'message': 'Not authenticated'}
        
        if not os.path.exists(image_path):
            return {'status': 'error', 'message': f'Image not found: {image_path}'}
        
        post_data = {
            'image_path': image_path,
            'caption': caption,
            'status': 'success',
            **kwargs
        }
        
        self.posts.append(post_data)
        self.logger.info(f"Posted to test platform: {caption[:50]}...")
        
        return {
            'status': 'success',
            'message': 'Post successful',
            'post_id': len(self.posts)
        }

def create_test_file(file_path, content="Test content"):
    """Create a test file."""
    with open(file_path, 'w') as f:
        f.write(content)
    logger.info(f"Created test file: {file_path}")
    return file_path

def test_simple_manager():
    """Test the SimpleSocialMediaManager."""
    logger.info("=== Starting SimpleSocialMediaManager Test ===")
    
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        logger.info(f"Using temporary directory: {temp_dir}")
        
        # Create a test file
        test_file = temp_dir / "test_post.txt"
        create_test_file(test_file, "This is a test post")
        
        # Import the simple manager
        try:
            from automation_stack.social_media.simple_manager import SimpleSocialMediaManager
            logger.info("✅ Successfully imported SimpleSocialMediaManager")
        except ImportError as e:
            logger.error(f"❌ Error importing SimpleSocialMediaManager: {e}")
            return False
        
        # Create a test platform
        test_platform = TestPlatform({'test_setting': 'test_value'})
        
        # Create and configure the manager
        try:
            manager = SimpleSocialMediaManager()
            manager.register_platform('test', test_platform)
            logger.info("✅ Created and configured SimpleSocialMediaManager")
            
            # Test posting
            test_caption = "Test post from SimpleSocialMediaManager"
            logger.info("\nTesting post to platform...")
            
            result = manager.post_to_platform(
                platform_name='test',
                content_path=str(test_file),
                caption=test_caption,
                test_param='test_value'
            )
            
            logger.info(f"Post result: {result}")
            
            if result.get('status') != 'success':
                logger.error(f"❌ Post failed: {result}")
                return False
            
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
    print("=== Simple Social Media Manager Test ===\n")
    
    if test_simple_manager():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
