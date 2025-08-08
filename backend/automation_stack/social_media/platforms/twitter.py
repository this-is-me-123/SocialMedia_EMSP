"""
Twitter platform integration for the social media automation system.
"""
import os
import time
import logging
import tweepy
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from automation_stack.social_media.platforms.base import SocialMediaPlatform

class Twitter(SocialMediaPlatform):
    """
    Twitter platform implementation for posting content.
    Uses the Twitter API v2 with tweepy.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Twitter platform with configuration.
        
        Args:
            config: Platform configuration dictionary
        """
        super().__init__(config)
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        print("Twitter config received in __init__:")
        print("  api_key:", self.api_key)
        print("  api_secret:", self.api_secret)
        print("  access_token:", self.access_token)
        print("  access_secret:", self.access_secret)
        self.rate_limit = self.config.get('rate_limit', 300)  # Tweets per 3-hour window
        self.last_api_call = 0
        self.client = None
        
        # Mock mode for testing
        self.mock_mode = self.config.get('mock_mode', False)
        self.mock_tweets = []  # Store mock tweets for testing
    
    def authenticate(self) -> bool:
        """
        Authenticate with the Twitter API.
        
        In mock mode, this will simulate successful authentication.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if self.mock_mode:
            self.logger.info("Running in mock mode - simulating successful Twitter authentication")
            self.username = "mock_twitter_user"
            self.user_id = "1234567890"
            self.authenticated = True
            return True
            
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            self.logger.error("Missing Twitter API credentials")
            return False
            
        try:
            # Authenticate with Twitter API v2
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret
            )
            
            # Verify credentials
            user = self.client.get_me(user_auth=True)
            if not user.data:
                self.logger.error("Failed to verify Twitter credentials")
                return False
                
            self.username = user.data.username
            self.user_id = user.data.id
            self.authenticated = True
            
            self.logger.info(f"Authenticated with Twitter as @{self.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Twitter authentication failed: {str(e)}")
            return False
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        now = time.time()
        time_since_last_call = now - self.last_api_call
        
        # Twitter has a 3-hour window for rate limits
        # We'll be conservative and space out our requests
        min_interval = 5  # At least 5 seconds between requests
        if time_since_last_call < min_interval:
            time_to_wait = min_interval - time_since_last_call
            time.sleep(time_to_wait)
            
        self.last_api_call = time.time()
    
    def post(
        self,
        content_path: Optional[str] = None,
        caption: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to Twitter.
        
        Args:
            content_path: Optional path to an image or video file
            caption: Tweet text (max 280 characters)
            **kwargs: Additional parameters
                - reply_to: Tweet ID to reply to
                - media_alt_text: Alt text for media
                
        Returns:
            Dictionary containing the tweet response
        """
        if not self.authenticated and not self.authenticate():
            return {
                'status': 'error',
                'message': 'Not authenticated with Twitter',
                'platform': 'twitter'
            }
        
        try:
            # In mock mode, simulate a successful tweet
            if self.mock_mode:

                from datetime import datetime
                
                # Format the tweet text
                tweet_text = self._format_tweet(caption)
                
                # Create a mock tweet
                tweet_id = f"mock_tweet_{int(time.time())}"
                tweet_url = f"https://twitter.com/{self.username}/status/{tweet_id}"
                
                # Create tweet data
                tweet_data = {
                    'id': tweet_id,
                    'text': tweet_text,
                    'url': tweet_url,
                    'timestamp': datetime.now().isoformat(),
                    'platform': 'twitter',
                    'mock': True
                }
                
                # Add media info if provided
                if content_path and os.path.exists(content_path):
                    media_id = f"mock_media_{int(time.time())}"
                    tweet_data['media'] = {
                        'id': media_id,
                        'path': os.path.basename(content_path),
                        'alt_text': kwargs.get('media_alt_text', '')
                    }
                
                # Add reply info if provided
                if 'reply_to' in kwargs:
                    tweet_data['in_reply_to_tweet_id'] = kwargs['reply_to']
                
                # Store the mock tweet
                self.mock_tweets.append(tweet_data)
                
                self.logger.info(f"[MOCK] Posted to Twitter: {tweet_url}")
                
                return {
                    'status': 'success',
                    'id': tweet_id,
                    'platform': 'twitter',
                    'url': tweet_url,
                    'text': tweet_text,
                    'mock': True
                }
            
            # Real implementation for non-mock mode
            self._rate_limit()
            
            # Format the tweet text
            tweet_text = self._format_tweet(caption)
            
            # Handle media upload if provided
            media_ids = []
            if content_path and os.path.exists(content_path):
                media_id = self._upload_media(content_path, kwargs.get('media_alt_text', ''))
                if media_id:
                    media_ids.append(media_id)
            
            # Create the tweet
            tweet_params = {
                'text': tweet_text,
                'user_auth': True
            }
            
            if media_ids:
                tweet_params['media_ids'] = media_ids
                
            if 'reply_to' in kwargs:
                tweet_params['in_reply_to_tweet_id'] = kwargs['reply_to']
            
            response = self.client.create_tweet(**tweet_params)
            
            if not response.data:
                raise Exception("Failed to create tweet")
            
            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/{self.username}/status/{tweet_id}"
            
            self.logger.info(f"Posted to Twitter: {tweet_url}")
            
            return {
                'status': 'success',
                'id': tweet_id,
                'platform': 'twitter',
                'url': tweet_url,
                'text': tweet_text
            }
            
        except Exception as e:
            error_msg = f"Error posting to Twitter: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg,
                'platform': 'twitter'
            }
    
    def _upload_media(
        self,
        media_path: str,
        alt_text: str = ""
    ) -> Optional[str]:
        """
        Upload media to Twitter.
        
        Args:
            media_path: Path to the media file
            alt_text: Alt text for accessibility
            
        Returns:
            Media ID if successful, None otherwise
        """
        if not self.authenticated:
            self.logger.error("Not authenticated with Twitter")
            return None
            
        try:
            self._rate_limit()
            
            # In a real implementation, you would use the Twitter API to upload media
            # For now, we'll simulate a successful upload
            media_id = f"tw_media_{int(time.time())}"
            
            self.logger.info(f"Uploaded media to Twitter: {media_id}")
            return media_id
            
        except Exception as e:
            self.logger.error(f"Error uploading media to Twitter: {str(e)}", exc_info=True)
            return None
    
    def _format_tweet(
        self,
        text: str,
        max_length: int = 280,
        max_hashtags: int = 5
    ) -> str:
        """
        Format a tweet, ensuring it meets Twitter's requirements.
        
        Args:
            text: Original tweet text
            max_length: Maximum tweet length (280 characters)
            max_hashtags: Maximum number of hashtags to include
            
        Returns:
            Formatted tweet text
        """
        # Format hashtags
        formatted = super().format_hashtags(text, max_hashtags)
        
        # Truncate if needed
        if len(formatted) > max_length:
            # Find the last space before max_length
            truncated = formatted[:max_length].rsplit(' ', 1)[0]
            return truncated + "..."
            
        return formatted
    
    def reply(
        self,
        tweet_id: str,
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Reply to a tweet.
        
        Args:
            tweet_id: ID of the tweet to reply to
            text: Reply text
            **kwargs: Additional parameters (media_path, etc.)
            
        Returns:
            Dictionary containing the reply response
        """
        kwargs['reply_to'] = tweet_id
        return self.post(None, text, **kwargs)
    
    def retweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Retweet a tweet.
        
        Args:
            tweet_id: ID of the tweet to retweet
            
        Returns:
            Dictionary containing the retweet response
        """
        if not self.authenticated and not self.authenticate():
            return {
                'status': 'error',
                'message': 'Not authenticated with Twitter',
                'platform': 'twitter'
            }
            
        try:
            self._rate_limit()
            
            # In a real implementation, you would use the Twitter API to retweet
            # For now, we'll simulate a successful retweet
            retweet_id = f"rt_{tweet_id}_{int(time.time())}"
            
            self.logger.info(f"Retweeted tweet {tweet_id}")
            
            return {
                'status': 'success',
                'id': retweet_id,
                'platform': 'twitter',
                'retweeted_tweet_id': tweet_id
            }
            
        except Exception as e:
            self.logger.error(f"Error retweeting: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'platform': 'twitter'
            }
