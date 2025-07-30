"""
Simple test script for the TikTok platform implementation.
"""
import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_tiktok_simple')

def main():
    """Run a simple test of the TikTok platform."""
    from automation_stack.social_media.platforms.tiktok import Tiktok
    
    print("=== TikTok Platform Simple Test ===\n")
    
    # Create test output directory
    test_output_dir = project_root / 'test_output'
    test_output_dir.mkdir(exist_ok=True)
    
    # Create a test video file (just a text file for testing)
    test_video = test_output_dir / 'test_video.txt'
    with open(test_video, 'w') as f:
        f.write("This is a test video file for TikTok testing.")
    
    print(f"Created test video file: {test_video}")
    
    # Initialize the TikTok platform with mock mode
    print("\nInitializing TikTok platform with mock mode...")
    tiktok = Tiktok({
        'mock_mode': True,
        'client_key': 'test_client_key',
        'client_secret': 'test_client_secret',
        'username': 'test_tiktok_user'
    })
    
    # Test authentication
    print("\nTesting authentication...")
    if tiktok.authenticate():
        print("✅ Authentication successful")
        print(f"  - Username: {tiktok.username}")
        print(f"  - Access Token: {tiktok.access_token[:10]}...")
    else:
        print("❌ Authentication failed")
        return
    
    # Test posting a video
    print("\nTesting video post...")
    caption = "Test video post #TikTok #Test #Automation"
    result = tiktok.post(
        content_path=str(test_video),
        caption=caption,
        privacy_level='PUBLIC_TO_EVERYONE'
    )
    
    # Check the result
    if result.get('status') == 'success':
        print("✅ Video post successful")
        print(f"  - Video ID: {result.get('id')}")
        print(f"  - URL: {result.get('url')}")
        print(f"  - Caption: {result.get('caption')}")
        
        # Check mock videos
        if hasattr(tiktok, 'mock_videos') and tiktok.mock_videos:
            print("\nMock videos:")
            for i, video in enumerate(tiktok.mock_videos, 1):
                print(f"  {i}. {video.get('id')} - {video.get('caption')}")
    else:
        print(f"❌ Video post failed: {result.get('message', 'Unknown error')}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
