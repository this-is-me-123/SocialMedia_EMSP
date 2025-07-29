"""
Core functionality test for the social media automation system.
"""
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def test_imports():
    """Test if core modules can be imported."""
    print("\n=== Testing Core Imports ===")
    
    modules = [
        'automation_stack.social_media.base_platform',
        'automation_stack.social_media.instagram_platform',
        'automation_stack.social_media.manager',
        'automation_stack.content_creation.simple_creator'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {str(e)}")
            all_ok = False
    
    return all_ok

def test_base_platform():
    """Test the base platform functionality."""
    print("\n=== Testing Base Platform ===")
    
    try:
        from automation_stack.social_media.base_platform import SocialMediaPlatform
        
        # Create a test platform
        class TestPlatform(SocialMediaPlatform):
            def authenticate(self):
                self.authenticated = True
                return True
                
            def post_image(self, image_path, caption, **kwargs):
                return {
                    'status': 'success',
                    'platform': 'test',
                    'message': 'Test post successful'
                }
        
        # Test the platform
        platform = TestPlatform({'dry_run': True})
        
        # Test authentication
        if not platform.authenticate():
            print("❌ Authentication failed")
            return False
            
        print("✅ Base platform test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error in base platform test: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=== Starting Core Tests ===\n")
    
    # Run import tests
    if not test_imports():
        print("\n❌ Some core imports failed")
        return
    
    # Run base platform test
    if not test_base_platform():
        print("\n❌ Base platform test failed")
        return
    
    print("\n✅ All core tests passed!")

if __name__ == "__main__":
    main()
