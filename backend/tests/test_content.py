"""
Test script for the content creation module.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Import the content creator
from automation_stack.content_creation.create_content import ContentCreator

def test_content_creation():
    """Test the content creation with default settings."""
    print("Testing content creation...")
    
    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Test configuration
    config = {
        'output_dir': str(output_dir),
        'image_size': (1080, 1080),
        'font_path': 'Arial',  # Use system Arial font
        'text_color': (255, 255, 255),  # White text
        'background_color': (0, 100, 200),  # Blue background
        'text_padding': 50,
        'font_size': 40,
        'line_spacing': 1.2
    }
    
    try:
        # Initialize content creator
        creator = ContentCreator(config)
        
        # Test text with hashtags
        test_text = """Test Content Creation
        
This is a test of the content creation system.
It should generate an image with this text.

#Test #Automation #EncompassMSP"""
        
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

def main():
    """Run the content creation test."""
    print("=== Testing Content Creation ===")
    
    if test_content_creation():
        print("\n✅ Content creation test completed successfully!")
        print("Check the 'test_output' directory for the generated image.")
    else:
        print("\n❌ Content creation test failed.")

if __name__ == "__main__":
    main()
