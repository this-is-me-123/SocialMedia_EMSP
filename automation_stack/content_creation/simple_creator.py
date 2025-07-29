"""
Simple content creator that only handles image creation.
This is a simplified version that avoids the moviepy dependency.
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Optional
import textwrap

class SimpleContentCreator:
    """
    A simplified content creator that only handles image creation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the content creator with configuration.
        
        Args:
            config: Configuration dictionary with the following keys:
                - output_dir: Directory to save generated content
                - image_size: Tuple of (width, height) for the output image
                - font_path: Path to the font file or font name
                - text_color: RGB tuple for text color
                - background_color: RGB tuple for background color
                - text_padding: Padding around text in pixels
                - font_size: Base font size
                - line_spacing: Multiplier for line spacing
        """
        self.config = config
        self.output_dir = Path(config.get('output_dir', 'generated_content'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize font
        self.font_size = config.get('font_size', 40)
        try:
            self.font = ImageFont.truetype(config.get('font_path', 'Arial'), self.font_size)
        except IOError:
            # Fall back to default font if specified font is not found
            self.font = ImageFont.load_default()
            print("Warning: Could not load specified font. Using default font.")
    
    def create_image(
        self,
        text: str,
        category: str = "general",
        index: int = 0,
        **kwargs
    ) -> str:
        """
        Create an image with the given text.
        
        Args:
            text: Text to include in the image
            category: Category for organizing output files
            index: Index number for the output filename
            **kwargs: Additional arguments (ignored in this simple version)
            
        Returns:
            Path to the created image file
        """
        # Create output directory for the category
        category_dir = self.output_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Generate output filename
        output_path = category_dir / f"{category}_{index:03d}.png"
        
        # Get image size and create a new image
        width, height = self.config.get('image_size', (1080, 1080))
        image = Image.new('RGB', (width, height), color=self.config.get('background_color', (0, 0, 0)))
        draw = ImageDraw.Draw(image)
        
        # Set up text parameters
        padding = self.config.get('text_padding', 50)
        max_width = width - (2 * padding)
        max_height = height - (2 * padding)
        
        # Wrap text to fit within the image width
        lines = []
        for line in text.split('\n'):
            if line.strip() == '':
                lines.append('')
                continue
                
            # Split long lines into multiple lines
            wrapped = textwrap.wrap(line, width=40)  # Approximate characters per line
            lines.extend(wrapped)
        
        # Calculate total text height
        line_height = int(self.font_size * 1.2)  # Add 20% for line spacing
        total_text_height = len(lines) * line_height
        
        # Start Y position (centered vertically)
        y = (height - total_text_height) // 2
        
        # Draw each line of text
        for line in lines:
            if not line.strip():
                y += line_height  # Add empty line
                continue
                
            # Get text size and position
            bbox = draw.textbbox((0, 0), line, font=self.font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2  # Center the text
            
            # Draw the text
            draw.text((x, y), line, fill=self.config.get('text_color', (255, 255, 255)), font=self.font)
            y += line_height
        
        # Save the image
        image.save(output_path)
        return str(output_path)
    
    def create_video(self, *args, **kwargs):
        """
        Placeholder for video creation (not implemented in this simple version).
        """
        raise NotImplementedError("Video creation is not supported in the simple content creator.")
    
    def batch_create_images(self, text_list: list, category: str = "batch") -> list:
        """
        Create multiple images from a list of text strings.
        
        Args:
            text_list: List of text strings for each image
            category: Category for organizing output files
            
        Returns:
            List of paths to created images
        """
        return [self.create_image(text, category, i) for i, text in enumerate(text_list)]
