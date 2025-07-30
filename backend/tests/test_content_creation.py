"""
Simple test script for content creation functionality.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Import the content creator
from automation_stack.content_creation.create_content import ContentCreator

def test_image_creation():
    """Test image creation with default settings."""
    print("Testing image creation...")
    
    # Create output directory if it doesn't exist
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize content creator with test settings
    config = {
        'output_dir': str(output_dir),
        'image_size': (1080, 1080),
        'font_path': 'Arial',
        'text_color': (255, 255, 255),
        'background_color': (0, 100, 200),
        'text_padding': 50,
        'font_size': 40,
        'line_spacing': 1.2
    }
    
    creator = ContentCreator(config)
    
    # Test text
    test_text = """Test Image Creation
    
This is a test of the content creation system.
It should generate an image with this text.

#Test #Automation #EncompassMSP"""
    
    try:
        # Create the image
        image_path = creator.create_image(
            text=test_text,
            category="test",
            index=1
        )
        
        if os.path.exists(image_path):
            print(f"✅ Successfully created test image: {os.path.abspath(image_path)}")
            return True
        else:
            print("❌ Failed to create test image")
            return False
            
    except Exception as e:
        print(f"❌ Error in content creation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testing Content Creation ===")
    success = test_image_creation()
    
    if success:
        print("\n✅ Content creation test completed successfully!")
        print("Check the 'test_output' directory for the generated image.")
    else:
        print("\n❌ Content creation test failed.")
