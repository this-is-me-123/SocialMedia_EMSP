"""
Simple test script to verify core functionality.
"""
import os
import sys
from pathlib import Path

def check_imports():
    """Check if required packages are installed."""
    print("Checking required packages...")
    
    packages = [
        'PIL',
        'dotenv',
        'requests',
        'schedule',
        'tweepy',
        'facebook',
        'pytz',
        'dateutil',
        'moviepy'
    ]
    
    all_ok = True
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg}")
        except ImportError:
            print(f"❌ {pkg} (missing)")
            all_ok = False
    
    return all_ok

def test_image_creation():
    """Test basic image creation with PIL."""
    print("\nTesting image creation...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple image
        img = Image.new('RGB', (800, 400), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        
        # Try to use a default font
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Add text
        d.text((10, 10), "Test Image Creation", fill=(255, 255, 0), font=font)
        d.text((10, 60), "This is a test of the content creation system.", fill=(255, 255, 255), font=font)
        
        # Save the image
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "test_output.png"
        img.save(output_path)
        
        if output_path.exists():
            print(f"✅ Successfully created test image: {output_path.absolute()}")
            return True
        else:
            print("❌ Failed to save test image")
            return False
            
    except Exception as e:
        print(f"❌ Error in image creation test: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=== Starting Simple Test ===")
    
    # Test 1: Check imports
    if not check_imports():
        print("\n❌ Some required packages are missing. Please install them first.")
        print("You can install them using: pip install -r requirements.txt")
        return
    
    # Test 2: Test basic image creation
    print("\n=== Testing Image Creation ===")
    if test_image_creation():
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
