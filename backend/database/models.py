"""
Database models for the social media automation system.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class PostStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"
    CANCELED = "canceled"

@dataclass
class User:
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool = True
    is_superuser: bool = False
    hashed_password: str = ""
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class Post:
    id: str
    user_id: int
    platform: str
    content: str
    scheduled_time: datetime
    status: PostStatus = PostStatus.DRAFT
    media_urls: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.media_urls is None:
            self.media_urls = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class AnalyticsEvent:
    id: int
    event: str
    timestamp: datetime
    platform: str = ""
    post_id: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class Database:
    """Simple SQLite database for the social media automation system."""
    
    def __init__(self, db_path: str = "social_media.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_superuser BOOLEAN DEFAULT FALSE,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    platform TEXT NOT NULL,
                    content TEXT NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'draft',
                    media_urls TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    platform TEXT DEFAULT '',
                    post_id TEXT DEFAULT '',
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            conn.commit()
    
    def create_user(self, user: User) -> User:
        """Create a new user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO users (username, email, full_name, is_active, is_superuser, hashed_password)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user.username, user.email, user.full_name, user.is_active, user.is_superuser, user.hashed_password))
            user.id = cursor.lastrowid
            conn.commit()
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(**dict(row))
        return None
    
    def create_post(self, post: Post) -> Post:
        """Create a new post."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO posts (id, user_id, platform, content, scheduled_time, status, media_urls, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.id, post.user_id, post.platform, post.content, 
                post.scheduled_time.isoformat(), post.status.value,
                json.dumps(post.media_urls), json.dumps(post.metadata)
            ))
            conn.commit()
        return post
    
    def get_post(self, post_id: str) -> Optional[Post]:
        """Get a post by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['scheduled_time'] = datetime.fromisoformat(data['scheduled_time'])
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                data['status'] = PostStatus(data['status'])
                data['media_urls'] = json.loads(data['media_urls'])
                data['metadata'] = json.loads(data['metadata'])
                return Post(**data)
        return None
    
    def update_post_status(self, post_id: str, status: PostStatus) -> bool:
        """Update a post's status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE posts SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (status.value, post_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_scheduled_posts(self) -> List[Post]:
        """Get all scheduled posts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM posts WHERE status = 'scheduled' 
                ORDER BY scheduled_time ASC
            """)
            posts = []
            for row in cursor.fetchall():
                data = dict(row)
                data['scheduled_time'] = datetime.fromisoformat(data['scheduled_time'])
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                data['status'] = PostStatus(data['status'])
                data['media_urls'] = json.loads(data['media_urls'])
                data['metadata'] = json.loads(data['metadata'])
                posts.append(Post(**data))
            return posts
    
    def log_analytics_event(self, event: AnalyticsEvent) -> AnalyticsEvent:
        """Log an analytics event."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO analytics_events (event, platform, post_id, metadata)
                VALUES (?, ?, ?, ?)
            """, (event.event, event.platform, event.post_id, json.dumps(event.metadata)))
            event.id = cursor.lastrowid
            conn.commit()
        return event
    
    def get_analytics_events(self, limit: int = 100) -> List[AnalyticsEvent]:
        """Get recent analytics events."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM analytics_events 
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            events = []
            for row in cursor.fetchall():
                data = dict(row)
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                data['metadata'] = json.loads(data['metadata'])
                events.append(AnalyticsEvent(**data))
            return events
