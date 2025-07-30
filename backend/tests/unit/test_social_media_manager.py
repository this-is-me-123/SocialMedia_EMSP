"""Unit tests for the social media manager."""
import unittest
import tempfile
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from automation_stack.manager import SocialMediaManager
from automation_stack.platforms.base_platform import SocialMediaPlatform

class MockPlatform(SocialMediaPlatform):
    """Mock platform for testing."""
    
    def __init__(self):
        self.name = "mock"
        self.posted_content = []
        
    def authenticate(self, **kwargs):
        return True
        
    def post(self, content, **kwargs):
        self.posted_content.append(content)
        return {"status": "success", "post_id": "123"}

class TestSocialMediaManager(unittest.TestCase):
    """Test the social media manager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.db_path = f"sqlite:///{self.test_dir}/test.db"
        
        # Initialize manager with test database
        self.manager = SocialMediaManager(database_url=self.db_path)
        
        # Register mock platform
        self.mock_platform = MockPlatform()
        self.manager.register_platform("mock", self.mock_platform)
        
        # Create test posts
        self.test_posts = [
            {
                "platform": "mock",
                "content": "Test post 1",
                "scheduled_time": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
                "status": "scheduled"
            },
            {
                "platform": "mock",
                "content": "Test post 2",
                "scheduled_time": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "status": "scheduled"
            }
        ]
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_schedule_post(self):
        """Test scheduling a new post."""
        post_data = self.test_posts[0]
        post_id = self.manager.schedule_post(
            platform=post_data["platform"],
            content=post_data["content"],
            scheduled_time=post_data["scheduled_time"]
        )
        
        # Verify post was added to the database
        post = self.manager.get_post(post_id)
        self.assertEqual(post["content"], post_data["content"])
        self.assertEqual(post["status"], "scheduled")
    
    def test_process_scheduled_posts(self):
        """Test processing of scheduled posts."""
        # Add test posts to the database
        for post in self.test_posts:
            self.manager.schedule_post(
                platform=post["platform"],
                content=post["content"],
                scheduled_time=post["scheduled_time"]
            )
        
        # Process scheduled posts
        with patch('automation_stack.manager.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow()
            processed = self.manager.process_scheduled_posts()
        
        # Verify one post was processed (the one in the past)
        self.assertEqual(processed, 1)
        
        # Verify the post was marked as posted
        posts = self.manager.get_posts(status="posted")
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["content"], "Test post 2")
        
        # Verify the platform's post method was called
        self.assertEqual(len(self.mock_platform.posted_content), 1)
        self.assertEqual(self.mock_platform.posted_content[0], "Test post 2")
    
    def test_cancel_post(self):
        """Test canceling a scheduled post."""
        # Schedule a post
        post_id = self.manager.schedule_post(
            platform="mock",
            content="Test post to cancel",
            scheduled_time=(datetime.utcnow() + timedelta(hours=1)).isoformat()
        )
        
        # Cancel the post
        self.assertTrue(self.manager.cancel_post(post_id))
        
        # Verify the post was marked as canceled
        post = self.manager.get_post(post_id)
        self.assertEqual(post["status"], "canceled")
    
    @patch('automation_stack.manager.SocialMediaManager._notify')
    def test_error_handling(self, mock_notify):
        """Test error handling during post processing."""
        # Create a failing platform
        class FailingPlatform(MockPlatform):
            def post(self, content, **kwargs):
                raise Exception("Posting failed")
        
        failing_platform = FailingPlatform()
        self.manager.register_platform("failing", failing_platform)
        
        # Schedule a post that will fail
        post_id = self.manager.schedule_post(
            platform="failing",
            content="This will fail",
            scheduled_time=(datetime.utcnow() - timedelta(minutes=5)).isoformat()
        )
        
        # Process the post
        with self.assertLogs(level='ERROR') as log:
            processed = self.manager.process_scheduled_posts()
        
        # Verify error was logged and notification was sent
        self.assertIn("Failed to post", "".join(log.output))
        mock_notify.assert_called_once()
        
        # Verify post was marked as failed
        post = self.manager.get_post(post_id)
        self.assertEqual(post["status"], "failed")
        self.assertIn("Posting failed", post.get("error", ""))

if __name__ == "__main__":
    unittest.main()
