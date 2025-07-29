"""
Minimal test for base platform functionality.
"""
print("=== Starting Minimal Base Platform Test ===\n")

# Test 1: Basic Python functionality
print("Test 1: Basic Python functionality")
print("✅ Python is working")

# Test 2: Import base_platform
try:
    print("\nTest 2: Import base_platform")
    import automation_stack.social_media.base_platform as base_platform
    print("✅ Successfully imported base_platform")
    print(f"Base platform path: {base_platform.__file__}")
except Exception as e:
    print(f"❌ Error importing base_platform: {str(e)}")
    raise

print("\n=== Test Complete ===")
