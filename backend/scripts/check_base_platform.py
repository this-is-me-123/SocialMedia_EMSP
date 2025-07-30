"""
Script to check for syntax errors in base_platform.py
"""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

print("=== Checking base_platform.py for syntax errors ===\n")

try:
    # Try to import the base_platform module
    print("Attempting to import base_platform...")
    import automation_stack.social_media.base_platform
    print("✅ Successfully imported base_platform")
    
    # Check if we can access the SocialMediaPlatform class
    print("\nChecking SocialMediaPlatform class...")
    from automation_stack.social_media.base_platform import SocialMediaPlatform
    print("✅ Successfully imported SocialMediaPlatform")
    
    # Try to create a simple subclass
    print("\nCreating a test platform class...")
    class TestPlatform(SocialMediaPlatform):
        def authenticate(self):
            return True
            
        def post_image(self, image_path, caption, **kwargs):
            return {
                'status': 'success',
                'platform': 'test',
                'message': 'Test post successful'
            }
    
    # Create an instance
    print("Creating a test platform instance...")
    platform = TestPlatform({'dry_run': True})
    print("✅ Successfully created test platform instance")
    
    # Test authentication
    print("\nTesting authentication...")
    if platform.authenticate():
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
    
    print("\n✅ All tests passed!")
    
except SyntaxError as e:
    print(f"❌ Syntax error in base_platform.py: {str(e)}")
    print(f"Error on line {e.lineno}: {e.text}")
except ImportError as e:
    print(f"❌ Import error: {str(e)}")
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
