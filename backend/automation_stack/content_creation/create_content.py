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
import requests
import openai
import json
from datetime import datetime

# Import configuration
from config.config import CONTENT
import os

# Set up logging
logger = logging.getLogger(__name__)

# Load API keys from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
SD_API_URL = os.getenv('SD_API_URL')
SD_API_KEY = os.getenv('SD_API_KEY')

class ContentCreator:
    """
    Handles the creation of visual content for social media posts.
    Supports image generation, text overlays, and video creation.
    Also supports AI-powered caption and image generation (GPT/Stable Diffusion), and analytics event logging.
    """

    def generate_caption_with_gpt(self, prompt: str, max_tokens: int = 60) -> str:
        """
        Generate a caption using OpenAI GPT.
        Args:
            prompt: Prompt to send to GPT
            max_tokens: Maximum tokens for the response
        Returns:
            Generated caption string
        """
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. Falling back to prompt as caption.")
            return prompt
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            caption = response.choices[0].message.content.strip()
            logger.info(f"Generated caption with GPT: {caption}")
            # Send analytics event to backend
            try:
                requests.post(
                    "http://localhost:8000/api/analytics/event",
                    json={
                        "event": "caption_generated",
                        "provider": "openai_gpt",
                        "prompt": prompt,
                        "caption": caption,
                        "timestamp": datetime.utcnow().isoformat()
                    }, timeout=3
                )
            except Exception:
                pass
            return caption
        except Exception as e:
            logger.error(f"GPT caption generation failed: {e}")
            # Send analytics event to backend
            try:
                requests.post(
                    "http://localhost:8000/api/analytics/event",
                    json={
                        "event": "caption_generation_failed",
                        "provider": "openai_gpt",
                        "prompt": prompt,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }, timeout=3
                )
            except Exception:
                pass
            return prompt

    def generate_image_with_stable_diffusion(self, prompt: str, output_path: str) -> Optional[str]:
        """
        Generate an image using a Stable Diffusion API.
        Args:
            prompt: Text prompt for image generation
            output_path: Where to save the generated image
        Returns:
            Path to the generated image, or None if failed
        """
        if not SD_API_URL or not SD_API_KEY:
            logger.warning("Stable Diffusion API config missing. Skipping AI image generation.")
            # Send analytics event to backend
            try:
                requests.post(
                    "http://localhost:8000/api/analytics/event",
                    json={
                        "event": "image_generation_skipped",
                        "provider": "stable_diffusion",
                        "reason": "missing_api_config",
                        "timestamp": datetime.utcnow().isoformat()
                    }, timeout=3
                )
            except Exception:
                pass
            return None
        headers = {"Authorization": f"Bearer {SD_API_KEY}", "Content-Type": "application/json"}
        payload = {"prompt": prompt, "num_inference_steps": 30, "guidance_scale": 7.5}
        try:
            resp = requests.post(SD_API_URL, headers=headers, data=json.dumps(payload), timeout=60)
            resp.raise_for_status()
            result = resp.json()
            if 'image' in result:
                # Assume base64-encoded PNG
                import base64
                img_bytes = base64.b64decode(result['image'])
                with open(output_path, 'wb') as f:
                    f.write(img_bytes)
                logger.info(f"Stable Diffusion image saved: {output_path}")
                # Send analytics event to backend
                try:
                    requests.post(
                        "http://localhost:8000/api/analytics/event",
                        json={
                            "event": "image_generated",
                            "provider": "stable_diffusion",
                            "prompt": prompt,
                            "output_path": output_path,
                            "timestamp": datetime.utcnow().isoformat()
                        }, timeout=3
                    )
                except Exception:
                    pass
                return output_path
            else:
                logger.error(f"Stable Diffusion API did not return image: {result}")
                # Send analytics event to backend
                try:
                    requests.post(
                        "http://localhost:8000/api/analytics/event",
                        json={
                            "event": "image_generation_failed",
                            "provider": "stable_diffusion",
                            "prompt": prompt,
                            "error": str(result),
                            "timestamp": datetime.utcnow().isoformat()
                        }, timeout=3
                    )
                except Exception:
                    pass
                return None
        except Exception as e:
            logger.error(f"Stable Diffusion image generation failed: {e}")
            # Send analytics event to backend
            try:
                requests.post(
                    "http://localhost:8000/api/analytics/event",
                    json={
                        "event": "image_generation_failed",
                        "provider": "stable_diffusion",
                        "prompt": prompt,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }, timeout=3
                )
            except Exception:
                pass
            return None

    def log_analytics_event(self, event_type: str, platform: str, post_id: str, metrics: dict, extra: dict = None):
        """
        Log analytics event (e.g., after posting or after engagement update).
        Args:
            event_type: e.g., 'post_published', 'post_engagement'
            platform: Platform name
            post_id: ID of the post
            metrics: Dict of engagement metrics (likes, shares, etc.)
            extra: Any extra data
        """
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'platform': platform,
            'post_id': post_id,
            'metrics': metrics,
            'extra': extra or {}
        }
        # For now, just log to file. Expand to DB or API as needed.
        logger.info(f"ANALYTICS_EVENT: {json.dumps(event)}")

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
    
    # Example: Generate a caption with GPT
    prompt = "Write a catchy Instagram caption for a sunrise yoga session."
    caption = creator.generate_caption_with_gpt(prompt)
    print(f"Generated caption: {caption}")
    
    # Example: Generate an image with Stable Diffusion
    sd_prompt = "A serene sunrise over a yoga class, vibrant colors, peaceful mood, photorealistic"
    ai_image_path = os.path.join(creator.output_dir, "sd_yoga_sunrise.png")
    sd_image = creator.generate_image_with_stable_diffusion(sd_prompt, ai_image_path)
    if sd_image:
        print(f"Stable Diffusion image saved: {sd_image}")
    else:
        print("Stable Diffusion image generation failed or not configured.")
    
    # Example: Create a single image (classic method)
    image_path = creator.create_image(
        caption,
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
    
    # Example: Log analytics event for engagement
    creator.log_analytics_event(
        event_type='post_engagement',
        platform='instagram',
        post_id='1234567890',
        metrics={'likes': 120, 'shares': 15, 'comments': 7},
        extra={'caption': caption}
    )

