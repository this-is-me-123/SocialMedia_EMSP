"""Performance testing for the Social Media Automation System."""
import time
import statistics
import pytest
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner
from locust import LoadTestShape
from datetime import datetime
import json
import random
from tests.test_config import TEST_POST, MOCK_RESPONSES

# Test configuration
USERS = 100  # Number of concurrent users
SPAWN_RATE = 10  # Users to spawn per second
DURATION = 300  # Test duration in seconds

class SocialMediaUser(HttpUser):
    """Simulate user interactions with the API."""
    wait_time = between(1, 5)  # Random wait between requests
    
    def on_start(self):
        """Initialize user session."""
        self.posts = []
        
        # Authenticate
        response = self.client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def create_post(self):
        """Simulate creating a new post."""
        post_data = TEST_POST.copy()
        post_data["content"] = f"Performance test post {datetime.utcnow().isoformat()}"
        
        with self.client.post(
            "/api/posts/",
            json=post_data,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                post_id = response.json().get("id")
                if post_id:
                    self.posts.append(post_id)
                    return
            response.failure(f"Failed to create post: {response.text}")
    
    @task(2)
    def list_posts(self):
        """Simulate listing posts."""
        self.client.get("/api/posts/", headers=self.headers)
    
    @task(1)
    def view_post(self):
        """Simulate viewing a post."""
        if self.posts:
            post_id = random.choice(self.posts)
            self.client.get(f"/api/posts/{post_id}", headers=self.headers)
    
    @task(1)
    def cancel_post(self):
        """Simulate canceling a post."""
        if self.posts:
            post_id = random.choice(self.posts)
            with self.client.post(
                f"/api/posts/{post_id}/cancel",
                headers=self.headers,
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    self.posts.remove(post_id)
                else:
                    response.failure(f"Failed to cancel post: {response.text}")

class StagesShape(LoadTestShape):
    """Define different stages of load testing."""
    
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 5},
        {"duration": 120, "users": 50, "spawn_rate": 10},
        {"duration": 180, "users": 100, "spawn_rate": 10},
        {"duration": 240, "users": 200, "spawn_rate": 20},
        {"duration": 300, "users": 100, "spawn_rate": 10},
        {"duration": 360, "users": 10, "spawn_rate": 5},
    ]
    
    def tick(self):
        """Determine the current stage of the test."""
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        
        return None

def test_performance():
    """Run performance tests and assert on metrics."""
    from locust.env import Environment
    from locust.stats import stats_printer, stats_history
    from locust.log import setup_logging
    import gevent
    
    # Setup logging
    setup_logging("INFO", None)
    
    # Setup Environment and Runner
    env = Environment(user_classes=[SocialMediaUser], host="http://localhost:8000")
    env.create_local_runner()
    
    # Start a greenlet that periodically outputs the current stats
    gevent.spawn(stats_printer(env.stats))
    
    # Start a greenlet that saves current stats to history
    gevent.spawn(stats_history, env.runner)
    
    # Start the test
    env.runner.start(USERS, spawn_rate=SPAWN_RATE)
    gevent.spawn_later(DURATION, lambda: env.runner.quit())
    env.runner.greenlet.join()
    
    # Calculate metrics
    total_requests = env.stats.total.num_requests
    avg_response_time = env.stats.total.avg_response_time
    failure_rate = env.stats.total.fail_ratio * 100
    
    # Print summary
    print("\nPerformance Test Results:")
    print(f"Total Requests: {total_requests}")
    print(f"Average Response Time: {avg_response_time:.2f}ms")
    print(f"Failure Rate: {failure_rate:.2f}%")
    
    # Assert performance metrics
    assert failure_rate < 1.0, "Failure rate too high"
    assert avg_response_time < 500, "Average response time too high"
    assert total_requests > 1000, "Insufficient request volume"

if __name__ == "__main__":
    test_performance()
