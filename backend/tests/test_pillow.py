"""
Simple script to test Pillow installation and basic image creation.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def main():
    print("Testing Pillow installation...")
    
    # Create a new image
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a font
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        print("Using default font (Arial not found)")
        font = ImageFont.load_default()
    
    # Draw some text
    text = "Pillow is working!"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Position the text in the center
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    draw.text((x, y), text, fill='black', font=font)
    
    # Save the image
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_pillow.png")
    image.save(output_path)
    
    print(f"Test image saved to: {os.path.abspath(output_path)}")
    print("✅ Pillow is working correctly!")

if __name__ == "__main__":
    main()
