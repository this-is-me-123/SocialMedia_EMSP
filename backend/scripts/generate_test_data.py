"""Generate test data for the Social Media Automation System."""
import os
import json
import random
from datetime import datetime, timedelta
from faker import Faker
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

# Initialize faker
fake = Faker()

# Output directories
OUTPUT_DIR = Path("tests/test_data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Sample data
HASHTAGS = [
    "#socialmedia", "#marketing", "#digitalmarketing", "#socialmediamarketing",
    "#contentmarketing", "#smm", "#socialmediamanager", "#socialmediapost",
    "#socialmediastrategy", "#socialmediamanagement"
]

PLATFORMS = ["instagram", "facebook", "twitter", "tiktok"]

MEDIA_TYPES = {
    "instagram": ["image/jpeg", "image/png", "video/mp4"],
    "facebook": ["image/jpeg", "image/png", "video/mp4"],
    "twitter": ["image/jpeg", "image/png", "video/mp4"],
    "tiktok": ["video/mp4"]
}

class TestDataGenerator:
    """Generate test data for the Social Media Automation System."""
    
    def __init__(self, base_dir: Path = OUTPUT_DIR):
        """Initialize the test data generator."""
        self.base_dir = base_dir
        self.fake = Faker()
        
    def generate_user(self, user_id: int = 1) -> Dict[str, Any]:
        """Generate a test user."""
        return {
            "id": user_id,
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "full_name": self.fake.name(),
            "is_active": True,
            "is_superuser": False,
            "created_at": self.fake.date_time_this_year().isoformat(),
            "updated_at": self.fake.date_time_this_year().isoformat()
        }
    
    def generate_platform_credentials(self, user_id: int, platform: str) -> Dict[str, Any]:
        """Generate platform credentials for a user."""
        return {
            "user_id": user_id,
            "platform": platform,
            "access_token": f"{platform}_access_token_{self.fake.sha256()}",
            "refresh_token": f"{platform}_refresh_token_{self.fake.sha256()}",
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "metadata": {
                "account_id": f"{platform}_account_{user_id}",
                "username": f"{platform}_user_{user_id}",
                "profile_picture": f"https://example.com/profiles/{user_id}.jpg"
            }
        }
    
    def generate_post(self, user_id: int, post_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate a test social media post."""
        platform = random.choice(PLATFORMS)
        scheduled_time = self.fake.date_time_between(
            start_date="-30d",
            end_date="+30d"
        ).isoformat()
        
        # Generate hashtags
        num_hashtags = random.randint(1, 5)
        content = f"{self.fake.sentence()}\n\n" + " ".join(random.sample(HASHTAGS, num_hashtags))
        
        # Generate media URLs
        media_urls = []
        if platform == "tiktok":
            media_type = "video/mp4"
            media_urls.append(f"https://example.com/videos/{self.fake.uuid4()}.mp4")
        else:
            media_type = random.choice(MEDIA_TYPES[platform])
            if "image" in media_type:
                media_urls.append(f"https://example.com/images/{self.fake.uuid4()}.jpg")
            else:
                media_urls.append(f"https://example.com/videos/{self.fake.uuid4()}.mp4")
        
        return {
            "id": post_id or self.fake.uuid4(),
            "user_id": user_id,
            "platform": platform,
            "content": content,
            "scheduled_time": scheduled_time,
            "status": random.choice(["draft", "scheduled", "posted", "failed"]),
            "media_urls": media_urls,
            "metadata": {
                "media_type": media_type,
                "location": self.fake.city() if random.random() > 0.5 else None,
                "tags": random.sample(HASHTAGS, random.randint(1, 3)),
                "mentions": [f"@{self.fake.user_name()}" for _ in range(random.randint(0, 3))]
            },
            "created_at": self.fake.date_time_this_year().isoformat(),
            "updated_at": self.fake.date_time_this_year().isoformat()
        }
    
    def generate_analytics(self, post_id: str) -> Dict[str, Any]:
        """Generate analytics data for a post."""
        return {
            "post_id": post_id,
            "impressions": random.randint(100, 10000),
            "engagements": random.randint(10, 1000),
            "likes": random.randint(0, 500),
            "comments": random.randint(0, 100),
            "shares": random.randint(0, 200),
            "clicks": random.randint(0, 300),
            "reach": random.randint(100, 5000),
            "saved": random.randint(0, 100),
            "video_views": random.randint(0, 1000) if random.random() > 0.7 else 0,
            "engagement_rate": random.uniform(0.5, 15.0),
            "collected_at": datetime.utcnow().isoformat()
        }
    
    def generate_test_data(self, num_users: int = 10, posts_per_user: int = 5) -> Dict[str, Any]:
        """Generate a complete test dataset."""
        users = [self.generate_user(i + 1) for i in range(num_users)]
        
        credentials = []
        posts = []
        analytics = []
        
        for user in users:
            # Generate credentials for each platform
            for platform in PLATFORMS:
                if random.random() > 0.3:  # 70% chance to have credentials for each platform
                    credentials.append(self.generate_platform_credentials(user["id"], platform))
            
            # Generate posts for the user
            for _ in range(random.randint(1, posts_per_user)):
                post = self.generate_post(user["id"])
                posts.append(post)
                
                # Generate analytics for some posts
                if post["status"] == "posted" and random.random() > 0.3:
                    analytics.append(self.generate_analytics(post["id"]))
        
        return {
            "users": users,
            "credentials": credentials,
            "posts": posts,
            "analytics": analytics
        }
    
    def save_test_data(self, data: Dict[str, Any], format: str = "json") -> None:
        """Save test data to files."
        
        # Create output directories
        (self.base_dir / "users").mkdir(exist_ok=True)
        (self.base_dir / "credentials").mkdir(exist_ok=True)
        (self.base_dir / "posts").mkdir(exist_ok=True)
        (self.base_dir / "analytics").mkdir(exist_ok=True)
        
        # Save users
        for user in data["users"]:
            filename = self.base_dir / "users" / f"user_{user['id']}.{format}"
            self._save_to_file(user, filename, format)
        
        # Save credentials
        for cred in data["credentials"]:
            filename = self.base_dir / "credentials" / f"cred_{cred['user_id']}_{cred['platform']}.{format}"
            self._save_to_file(cred, filename, format)
        
        # Save posts
        for post in data["posts"]:
            filename = self.base_dir / "posts" / f"post_{post['id']}.{format}"
            self._save_to_file(post, filename, format)
        
        # Save analytics
        for analytic in data["analytics"]:
            filename = self.base_dir / "analytics" / f"analytics_{analytic['post_id']}.{format}"
            self._save_to_file(analytic, filename, format)
        
        # Save complete dataset
        self._save_to_file(data, self.base_dir / f"complete_dataset.{format}", format)
    
    def _save_to_file(self, data: Any, filename: Path, format: str = "json") -> None:
        """Save data to a file in the specified format."""
        with open(filename, "w", encoding="utf-8") as f:
            if format.lower() == "json":
                json.dump(data, f, indent=2, ensure_ascii=False)
            elif format.lower() in ["yaml", "yml"]:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(f"Unsupported format: {format}")

def main():
    """Generate and save test data."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test data for the Social Media Automation System.")
    parser.add_argument("--users", type=int, default=10, help="Number of users to generate")
    parser.add_argument("--posts", type=int, default=5, help="Maximum number of posts per user")
    parser.add_argument("--format", type=str, default="json", choices=["json", "yaml"], 
                       help="Output format (json or yaml)")
    parser.add_argument("--output", type=str, default=str(OUTPUT_DIR), 
                       help="Output directory for test data")
    
    args = parser.parse_args()
    
    print(f"Generating test data for {args.users} users with up to {args.posts} posts each...")
    
    generator = TestDataGenerator(Path(args.output))
    test_data = generator.generate_test_data(args.users, args.posts)
    generator.save_test_data(test_data, args.format)
    
    print(f"Test data generated successfully in {args.output}")
    print(f"- Users: {len(test_data['users'])}")
    print(f"- Credentials: {len(test_data['credentials'])}")
    print(f"- Posts: {len(test_data['posts'])}")
    print(f"- Analytics: {len(test_data['analytics'])}")

if __name__ == "__main__":
    main()
