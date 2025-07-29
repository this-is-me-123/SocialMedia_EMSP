"""
Simple test script for Instagram platform integration.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_instagram_auth():
    """Test Instagram authentication with detailed logging."""
    logger.info("Starting Instagram authentication test...")
    
    try:
        # Import InstagramPlatform here to catch any import errors
        from automation_stack.social_media.instagram_platform import InstagramPlatform
        logger.info("Successfully imported InstagramPlatform")
        
        # Configuration for Instagram with fallback values
        config = {
            'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', 'dummy_token'),
            'page_id': os.getenv('INSTAGRAM_PAGE_ID', 'dummy_page_id'),
            'app_id': os.getenv('FACEBOOK_APP_ID', 'dummy_app_id'),
            'app_secret': os.getenv('FACEBOOK_APP_SECRET', 'dummy_app_secret'),
            'dry_run': True,  # Enable dry run mode for testing
            'debug': True     # Enable debug logging
        }
        
        # Log the configuration (without sensitive data)
        logger.info("Instagram configuration:")
        for key, value in config.items():
            if key in ['access_token', 'app_secret']:
                logger.info(f"  {key}: {'*' * 8 + value[-4:] if value and len(value) > 4 else 'None'}")
            else:
                logger.info(f"  {key}: {value}")
        
        # Initialize Instagram platform
        logger.info("Initializing Instagram platform...")
        instagram = InstagramPlatform(config)
        logger.info("Instagram platform initialized successfully")
        
        # Test authentication
        logger.info("Attempting to authenticate with Instagram...")
        result = False
        try:
            result = instagram.authenticate()
        except Exception as auth_error:
            logger.error(f"Authentication error: {str(auth_error)}", exc_info=True)
            raise
        
        if result:
            logger.info("✅ Instagram authentication successful")
        else:
            logger.error("❌ Instagram authentication failed")
        
        return result
        
    except ImportError as ie:
        logger.error(f"Failed to import InstagramPlatform: {str(ie)}")
        logger.error("Please check if the module exists and all dependencies are installed")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Instagram authentication test: {str(e)}", exc_info=True)
        raise

def main():
    """Run the Instagram tests."""
    print("=== Testing Instagram Integration ===\n")
    
    # Test authentication
    print("Testing Instagram authentication...")
    try:
        auth_result = test_instagram_auth()
        if auth_result:
            print("\n✅ Instagram authentication test passed!")
        else:
            print("\n❌ Instagram authentication test failed.")
    except Exception as e:
        print(f"\n❌ Error during Instagram test: {str(e)}")
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    main()
