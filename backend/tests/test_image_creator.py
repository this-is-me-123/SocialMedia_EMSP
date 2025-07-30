"""
Standalone test for the simple image creator.
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_test_image():
    """Create a test image using basic Pillow functionality."""
    print("Creating test image...")
    
    # Configuration
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Image dimensions
    width, height = 1080, 1080
    
    # Colors
    background_color = (30, 30, 100)  # Dark blue
    text_color = (255, 255, 255)      # White
    
    # Create a new image
    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)
    
    # Try to use Arial, fall back to default font if not available
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        print("Using default font (Arial not found)")
        font = ImageFont.load_default()
    
    # Test text
    text = """Test Image Creation
    
This is a test of the image creation system.
It should generate an image with this text,
properly wrapped and centered.

#Test #Automation #EncompassMSP"""
    
    # Text parameters
    padding = 50
    max_width = width - (2 * padding)
    
    # Split text into lines and wrap long lines
    lines = []
    for line in text.split('\n'):
        if line.strip() == '':
            lines.append('')
            continue
            
        # Split long lines into multiple lines
        wrapped = textwrap.wrap(line, width=40)  # Approximate characters per line
        lines.extend(wrapped if wrapped else [''])
    
    # Calculate total text height
    line_height = 50  # Fixed line height
    total_text_height = len(lines) * line_height
    
    # Start Y position (centered vertically)
    y = (height - total_text_height) // 2
    
    # Draw each line of text
    for line in lines:
        if not line.strip():
            y += line_height  # Add empty line
            continue
            
        # Get text size and position
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2  # Center the text
        
        # Draw the text
        draw.text((x, y), line, fill=text_color, font=font)
        y += line_height
    
    # Save the image
    output_path = output_dir / "test_output.png"
    image.save(output_path)
    
    if output_path.exists():
        print(f"✅ Successfully created test image: {output_path.absolute()}")
        return str(output_path.absolute())
    else:
        print("❌ Failed to save test image")
        return None

def main():
    """Run the test."""
    print("=== Testing Image Creation ===")
    
    image_path = create_test_image()
    
    if image_path:
        print("\n✅ Image creation test completed successfully!")
        print(f"Check the file at: {image_path}")
    else:
        print("\n❌ Image creation test failed.")

if __name__ == "__main__":
    main()
