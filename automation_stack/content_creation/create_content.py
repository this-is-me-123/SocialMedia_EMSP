"""
Content creation module for generating social media content.
Handles image and video creation with text overlays and branding.
"""
import os
import random
import textwrap
import logging
from pathlib import Path
from typing import Optional, Tuple, List, Union
from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# Import configuration
from config import CONTENT

# Set up logging
logger = logging.getLogger(__name__)

class ContentCreator:
    """
    Handles the creation of visual content for social media posts.
    Supports image generation, text overlays, and video creation.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the ContentCreator with configuration.
        
        Args:
            config: Optional configuration dictionary. Uses default config if not provided.
        """
        self.config = config or CONTENT
        self._setup_directories()
        self._load_font()
        
    def _setup_directories(self) -> None:
        """Ensure all required directories exist."""
        self.output_dir = Path(self.config['output_dir'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_font(self, font_size: Optional[int] = None) -> None:
        """
        Load the specified font with the given size.
        
        Args:
            font_size: Size of the font. Uses default from config if not provided.
        """
        font_size = font_size or self.config['default_font_size']
        font_path = self.config['font_path']
        
        try:
            self.font = ImageFont.truetype(font_path, font_size)
        except IOError:
            logger.warning(f"Font file not found at {font_path}. Using default font.")
            self.font = ImageFont.load_default()
    
    def create_image(
        self,
        text: str,
        category: str,
        index: int,
        size: Optional[Tuple[int, int]] = None,
        bg_color: Optional[str] = None,
        text_color: Optional[str] = None
    ) -> str:
        """
        Create an image with text overlay.
        
        Args:
            text: Text to display on the image
            category: Content category (used for filename)
            index: Index number (used for filename)
            size: Image dimensions (width, height)
            bg_color: Background color in hex format (e.g., '#003366')
            text_color: Text color in hex format (e.g., '#FFFFFF')
            
        Returns:
            Path to the created image file
        """
        size = size or self.config['image_size']
        bg_color = bg_color or random.choice(self.config['brand_colors'])
        text_color = text_color or self.config['text_color']
        
        # Create image with background color
        image = Image.new('RGB', size, color=bg_color)
        draw = ImageDraw.Draw(image)
        
        # Add text with proper wrapping
        margin = self.config.get('text_margin', 50)
        max_width = size[0] - (2 * margin)
        max_chars = self.config.get('text_max_width', 30)
        
        # Wrap text
        wrapper = textwrap.TextWrapper(width=max_chars)
        wrapped_text = wrapper.fill(text)
        
        # Calculate text position (centered)
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=self.font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Draw text with outline for better visibility
        outline_color = self._get_contrast_color(bg_color)
        for adj in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            draw.text((x + adj[0], y + adj[1]), wrapped_text, font=self.font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), wrapped_text, font=self.font, fill=text_color)
        
        # Save the image
        filename = f"{category}_{index:03d}.png"
        output_path = self.output_dir / filename
        image.save(output_path, quality=95)
        
        logger.info(f"Created image: {output_path}")
        return str(output_path)
    
    def create_video(
        self,
        image_path: Union[str, Path],
        audio_path: Optional[Union[str, Path]] = None,
        duration: int = 10,
        output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """
        Create a video from an image with optional audio.
        
        Args:
            image_path: Path to the source image
            audio_path: Optional path to audio file
            duration: Duration of the video in seconds
            output_path: Optional custom output path
            
        Returns:
            Path to the created video file
        """
        image_path = Path(image_path)
        if not output_path:
            output_path = self.output_dir / f"{image_path.stem}.mp4"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create video clip from image
        clip = ImageClip(str(image_path)).set_duration(duration)
        
        # Add audio if provided
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(str(audio_path))
            if audio.duration < duration:
                # Loop audio if it's shorter than the video
                audio = audio.audio_loop(duration=duration)
            clip = clip.set_audio(audio)
        
        # Write the video file
        clip.write_videofile(
            str(output_path),
            fps=24,
            codec='libx264',
            audio_codec='aac' if audio_path else None,
            logger=None  # Disable moviepy's logger
        )
        
        logger.info(f"Created video: {output_path}")
        return str(output_path)
    
    def _get_contrast_color(self, bg_color: str) -> str:
        """
        Get a contrasting color for text outlines.
        
        Args:
            bg_color: Background color in hex format
            
        Returns:
            Contrasting color in hex format
        """
        # Convert hex to RGB
        bg_color = bg_color.lstrip('#')
        r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        # Return black for light colors, white for dark colors
        return '#000000' if luminance > 0.5 else '#FFFFFF'
    
    def batch_create_images(
        self,
        text_list: List[str],
        category: str,
        start_index: int = 0,
        **kwargs
    ) -> List[str]:
        """
        Create multiple images from a list of text captions.
        
        Args:
            text_list: List of text captions
            category: Content category
            start_index: Starting index for filenames
            **kwargs: Additional arguments for create_image
            
        Returns:
            List of paths to created images
        """
        return [
            self.create_image(text, category, i + start_index, **kwargs)
            for i, text in enumerate(text_list)
        ]


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    creator = ContentCreator()
    
    # Example: Create a single image
    image_path = creator.create_image(
        "This is a test caption for social media post #1",
        "test",
        1
    )
    
    # Example: Create a video with the image
    video_path = creator.create_video(
        image_path,
        audio_path=os.path.join(CONTENT['audio_dir'], 'background_music.mp3') if os.path.exists(os.path.join(CONTENT['audio_dir'], 'background_music.mp3')) else None,
        duration=5
    )
    
    print(f"Created image: {image_path}")
    print(f"Created video: {video_path}")
