"""
Test script for the simple content creator.
"""
import os
from pathlib import Path
from automation_stack.content_creation.simple_creator import SimpleContentCreator

def test_simple_creator():
    """Test the simple content creator."""
    print("Testing SimpleContentCreator...")
    
    # Configuration
    config = {
        'output_dir': 'test_output',
        'image_size': (1080, 1080),
        'font_path': 'Arial',
        'text_color': (255, 255, 255),  # White text
        'background_color': (30, 30, 100),  # Dark blue background
        'text_padding': 50,
        'font_size': 40,
        'line_spacing': 1.2
    }
    
    try:
        # Initialize the creator
        creator = SimpleContentCreator(config)
        
        # Test text with hashtags
        test_text = """Simple Content Creator Test
        
This is a test of the simple content creation system.
It should generate an image with this text, properly wrapped and centered.

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
    """Run the simple creator test."""
    print("=== Testing Simple Content Creator ===")
    
    if test_simple_creator():
        print("\n✅ Simple content creator test completed successfully!")
        print("Check the 'test_output' directory for the generated image.")
    else:
        print("\n❌ Simple content creator test failed.")

if __name__ == "__main__":
    main()
