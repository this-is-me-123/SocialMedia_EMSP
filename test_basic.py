"""
Basic test script for the social media automation system.
"""
print("=== Starting Basic Test ===\n")

# Test 1: Basic Python functionality
print("Test 1: Basic Python functionality")
print("✅ Python is working")

# Test 2: Import base_platform module
try:
    print("\nTest 2: Import base_platform")
    import automation_stack.social_media.base_platform
    print("✅ Successfully imported base_platform")
except Exception as e:
    print(f"❌ Error importing base_platform: {str(e)}")
    raise

# Test 3: Create a simple platform
try:
    print("\nTest 3: Create a simple platform")
    from automation_stack.social_media.base_platform import SocialMediaPlatform
    
    class TestPlatform(SocialMediaPlatform):
        def authenticate(self):
            print("TestPlatform.authenticate() called")
            return True
            
        def post_image(self, image_path, caption, **kwargs):
            print(f"TestPlatform.post_image() called with: {image_path}")
            return {
                'status': 'success',
                'platform': 'test',
                'message': 'Test post successful'
            }
    
    # Create an instance
    platform = TestPlatform({'dry_run': True})
    print("✅ Successfully created TestPlatform instance")
    
    # Test authentication
    if platform.authenticate():
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
    
    # Test post_image
    result = platform.post_image("test.png", "Test caption")
    print(f"✅ Post result: {result}")
    
except Exception as e:
    print(f"❌ Error in TestPlatform: {str(e)}")
    raise

print("\n=== Test Complete ===")
