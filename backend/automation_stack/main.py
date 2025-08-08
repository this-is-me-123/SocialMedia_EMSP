"""
Main script for the social media automation system.
Handles content creation, scheduling, and posting to multiple platforms.
"""
import os
from dotenv import load_dotenv
load_dotenv()  # Make sure this is called before any os.getenv()


import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure config is imported after dotenv is loaded
# Remove any earlier import of automation_stack.config or SocialMediaManager above this point

# --- Centralized Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("automation_stack.main")

app = FastAPI()

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ... (all routers, endpoints, and logic)

# Serve React frontend static files from /app/static
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")

from fastapi import Request, Response

@app.get("/webhook/")
@app.get("/webhook")
async def instagram_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    VERIFY_TOKEN = os.getenv("INSTAGRAM_VERIFY_TOKEN")
    if not VERIFY_TOKEN:
        return Response(content="VERIFY_TOKEN not set", status_code=500)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)

# --- CORS Configuration ---
# For production, set CORS_ALLOW_ORIGINS as a comma-separated list of allowed origins (e.g., https://yourdomain.com)
# For development, defaults to localhost. DO NOT use '*' in production!
import os
cors_origins = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
if "*" in cors_origins:
    logger.warning("CORS is set to allow all origins ('*'). This is insecure for production!")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api")

from datetime import datetime
from pydantic import BaseModel



from passlib.context import CryptContext
import jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional

from automation_stack.database import User, get_db
from sqlalchemy.orm import Session
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY must be set in environment variables.")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    hashed_password: str
    created_at: datetime
    updated_at: datetime

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict):
    from datetime import timedelta
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/auth/register", status_code=201, response_model=UserInDB, responses={201: {"description": "User registered"}, 400: {"description": "User already exists"}})
def register_user(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Register a new user. In production, use a real database and add email verification, rate limiting, etc.
    """
    existing = db.query(User).filter(User.username == form.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(form.password)
    new_user = User(
        username=form.username,
        email=f"{form.username}@example.com",
        full_name=form.username,
        is_active=True,
        is_superuser=False,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserInDB(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser,
        hashed_password=new_user.hashed_password,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )

@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

    is_superuser=False,
    hashed_password="fakehashed",
    created_at=now,
    updated_at=now
    return user


from pydantic import HttpUrl
from typing import List, Dict, Any

class PostInDB(BaseModel):
    platform: str
    content: str
    scheduled_time: datetime
    id: str
    user_id: int
    status: str  # should be one of: 'draft', 'scheduled', 'posted', 'failed', 'canceled'
    created_at: datetime
    updated_at: datetime
    media_urls: List[HttpUrl] = []
    metadata: Dict[str, Any] = {}

from .social_media.manager import SocialMediaManager
manager = SocialMediaManager()  # Singleton instance

class PostSchema(BaseModel):
    platform: str
    content: str
    caption: str
    scheduled_time: datetime
    user_id: int = 1
    media_urls: List[HttpUrl] = []
    metadata: Dict[str, Any] = {}

@router.post("/post", status_code=201, responses={201: {"description": "Post created successfully"}, 400: {"description": "Invalid post data"}, 500: {"description": "Internal server error"}})
def create_post(post: PostSchema, token: str = Depends(oauth2_scheme)):
    """
    Create a new post and schedule it for publishing.
    """
    logger.info(f"POST /post - payload: {post.dict()}")
    try:
        # Unpack post fields for direct argument passing
        result = manager.create_post(
            post.platform,   # platform_name
            post.content,    # content_path
            post.caption,    # caption
            scheduled_time=post.scheduled_time,
            user_id=post.user_id,
            media_urls=post.media_urls,
            metadata=post.metadata
        )
        logger.info(f"Post created: {result}")
        return result
    except Exception as e:
        logger.exception("Error creating post")
        raise HTTPException(status_code=500, detail="Failed to create post")

@router.get("/post/{post_id}", responses={200: {"description": "Post found"}, 404: {"description": "Post not found"}})
def get_single_post(post_id: str, token: str = Depends(oauth2_scheme)):
    """
    Get a single post by ID.
    """
    logger.info(f"GET /post/{post_id}")
    post = manager.get_post(post_id)
    if not post:
        logger.warning(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/posts", responses={200: {"description": "List all posts"}})
def get_posts(token: str = Depends(oauth2_scheme)):
    """
    List all posts.
    """
    logger.info("GET /posts")
    return manager.get_all_posts()

@router.delete("/post/{post_id}", responses={200: {"description": "Post cancelled"}, 404: {"description": "Post not found or already published"}})
def cancel_post(post_id: str, token: str = Depends(oauth2_scheme)):
    """
    Cancel a scheduled post by ID.
    """
    logger.info(f"DELETE /post/{post_id}")
    success = manager.cancel_post(post_id)
    if not success:
        logger.warning(f"Cancel failed: post not found or already published: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found or already published")
    return {"status": "cancelled", "post_id": post_id}

@router.get("/analytics", responses={200: {"description": "Get analytics summary"}})
def get_analytics(token: str = Depends(oauth2_scheme)):
    """
    Get analytics summary for all posts.
    """
    logger.info("GET /analytics")
    return manager.get_analytics()

from fastapi import Request
import json

class AnalyticsEvent(BaseModel):
    event: str
    timestamp: str
    # Accept arbitrary event data
    class Config:
        extra = "allow"

from automation_stack.database import AnalyticsEvent as AnalyticsEventModel
from sqlalchemy.orm import Session
import json as pyjson

@router.post("/analytics/event")
async def analytics_event(event: AnalyticsEvent, request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Store analytics event in DB
    event_dict = event.dict()
    ip = request.client.host
    db_event = AnalyticsEventModel(
        event=event.event,
        timestamp=event.timestamp,
        ip=ip,
        data=pyjson.dumps({k: v for k, v in event_dict.items() if k not in ["event", "timestamp"]})
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {"status": "ok"}

@router.get("/analytics/view")
async def analytics_view(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Return most recent analytics events first
    events = db.query(AnalyticsEventModel).order_by(AnalyticsEventModel.timestamp.desc()).all()
    result = []
    for e in events:
        try:
            data = pyjson.loads(e.data) if e.data else {}
        except Exception:
            data = {}
        result.append({
            "id": e.id,
            "event": e.event,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "ip": e.ip,
            **data
        })
    return result

@router.get("/analytics/summary")
def analytics_summary(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    stats = {
        'total_events': 0,
        'total_posts': 0,
        'successes': 0,
        'failures': 0,
        'retries': 0,
        'notifications_sent': 0,
        'per_platform': {}
    }
    events = db.query(AnalyticsEventModel).all()
    for event in events:
        stats['total_events'] += 1
        try:
            data = pyjson.loads(event.data) if event.data else {}
        except Exception:
            data = {}
        platform = data.get('platform', 'unknown')
        if platform not in stats['per_platform']:
            stats['per_platform'][platform] = {'successes': 0, 'failures': 0, 'retries': 0, 'posts': 0}
        if event.event == 'post_published':
            stats['successes'] += 1
            stats['per_platform'][platform]['successes'] += 1
            stats['per_platform'][platform]['posts'] += 1
            stats['total_posts'] += 1
        elif event.event == 'post_failed':
            stats['failures'] += 1
            stats['per_platform'][platform]['failures'] += 1
            stats['per_platform'][platform]['posts'] += 1
            stats['total_posts'] += 1
        elif event.event == 'post_retry_scheduled':
            stats['retries'] += 1
            stats['per_platform'][platform]['retries'] += 1
        elif event.event == 'notification_sent':
            stats['notifications_sent'] += 1
    return stats

@router.get("/scheduled_posts")
def get_scheduled_posts(token: str = Depends(oauth2_scheme)):
    # Import or access the singleton SocialMediaManager instance
    # For now, create a new one if not already global
    from .social_media.manager import SocialMediaManager
    manager = SocialMediaManager()
    return manager.scheduled_posts

app.include_router(router)

@app.on_event("startup")
async def log_routes():
    logger.info("REGISTERED ROUTES (on startup):")
    for route in app.routes:
        if hasattr(route, 'methods'):
            logger.info(f"{route.path} {route.methods}")
        else:
            logger.info(f"{route.path} ({type(route).__name__})")

from fastapi import Request
import requests

INSTAGRAM_CLIENT_ID = os.getenv('INSTAGRAM_CLIENT_ID')
if not INSTAGRAM_CLIENT_ID:
    raise RuntimeError("INSTAGRAM_CLIENT_ID must be set in environment variables.")

# --- TikTok OAuth Callback ---
from fastapi.responses import RedirectResponse, JSONResponse

TIKTOK_CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY')
TIKTOK_CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET')
TIKTOK_REDIRECT_URI = os.getenv('TIKTOK_REDIRECT_URI')
if not all([TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI]):
    raise RuntimeError("TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, and TIKTOK_REDIRECT_URI must be set in environment variables.")

@app.get('/auth/tiktok/callback')
@app.get('/auth/tiktok/callback/')
async def tiktok_oauth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    import datetime
    print('TIKTOK CALLBACK HIT', flush=True)
    print('CALLBACK RECEIVED AT:', datetime.datetime.utcnow().isoformat(), flush=True)
    if error:
        return JSONResponse({'error': error}, status_code=400)
    print('RAW QUERY STRING:', request.url.query, flush=True)
    print('CODE PARAM:', code, flush=True)
    if not code:
        return JSONResponse({'error': 'Missing code parameter'}, status_code=400)

    # Exchange code for access token
    token_url = 'https://open-api.tiktok.com/oauth/access_token/'
    import urllib.parse
    encoded_code = urllib.parse.quote(code, safe='')
    print('ENCODED CODE FOR TIKTOK:', encoded_code, flush=True)
    data = {
        'client_key': TIKTOK_CLIENT_KEY,
        'client_secret': TIKTOK_CLIENT_SECRET,
        'code': encoded_code,
        'grant_type': 'authorization_code',
        'redirect_uri': TIKTOK_REDIRECT_URI
    }
    print('TIKTOK TOKEN EXCHANGE PAYLOAD:', data, flush=True)
    resp = requests.post(token_url, data=data)
    print('TIKTOK TOKEN EXCHANGE RESPONSE:', resp.status_code, resp.text, flush=True)
    if resp.status_code != 200:
        return JSONResponse({'error': 'Failed to get access token', 'details': resp.text}, status_code=400)
    token_data = resp.json()
    access_token = token_data.get('data', {}).get('access_token')
    open_id = token_data.get('data', {}).get('open_id')
    if not access_token or not open_id:
        return JSONResponse({'error': 'Missing access_token or open_id', 'details': token_data}, status_code=400)

    # Fetch user profile
    userinfo_url = 'https://open-api.tiktok.com/user/info/'
    params = {
        'access_token': access_token,
        'open_id': open_id,
        'fields': 'open_id,union_id,avatar_url,display_name'
    }
    userinfo_resp = requests.get(userinfo_url, params=params)
    if userinfo_resp.status_code != 200:
        return JSONResponse({'error': 'Failed to fetch user info', 'details': userinfo_resp.text}, status_code=400)
    userinfo = userinfo_resp.json()

    # Here you would log the user in, create a session, etc.
    # For now, just return profile info
    return JSONResponse({'access_token': access_token, 'open_id': open_id, 'profile': userinfo.get('data', {})})

INSTAGRAM_CLIENT_SECRET = os.getenv('INSTAGRAM_CLIENT_SECRET')
INSTAGRAM_REDIRECT_URI = os.getenv('INSTAGRAM_REDIRECT_URI')
if not all([INSTAGRAM_CLIENT_SECRET, INSTAGRAM_REDIRECT_URI]):
    raise RuntimeError("INSTAGRAM_CLIENT_SECRET and INSTAGRAM_REDIRECT_URI must be set in environment variables.")

@app.get('/api/auth/instagram/callback')
def instagram_oauth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """
    Instagram OAuth callback endpoint. Exchanges code for access token and fetches user profile.
    """
    if error:
        return JSONResponse({'error': error}, status_code=400)
    if not code:
        return JSONResponse({'error': 'Missing code parameter'}, status_code=400)
    # Exchange code for access token
    token_url = 'https://api.instagram.com/oauth/access_token'
    data = {
        'client_id': INSTAGRAM_CLIENT_ID,
        'client_secret': INSTAGRAM_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': INSTAGRAM_REDIRECT_URI,
        'code': code,
    }
    try:
        resp = requests.post(token_url, data=data)
        token_data = resp.json()
        if 'access_token' not in token_data:
            return JSONResponse({'error': 'Failed to get access token', 'details': token_data}, status_code=400)
        access_token = token_data['access_token']
        user_id = token_data.get('user_id')
        # Fetch user profile info
        profile_url = f'https://graph.instagram.com/{user_id}?fields=id,username,account_type&access_token={access_token}'
        profile_resp = requests.get(profile_url)
        profile_data = profile_resp.json()
        # Here you can create a session/JWT for the user, etc.
        # For now, just return the profile data
        return JSONResponse({'access_token': access_token, 'profile': profile_data})
    except Exception as e:
        logger.exception("Instagram OAuth flow failed")
        return JSONResponse({'error': 'OAuth flow failed', 'details': str(e)}, status_code=500)

# --- FastAPI request/response logging middleware ---
from fastapi import Request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as exc:
        logger.error(f"Unhandled exception: {exc}")
        raise


import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import our modules
from content_creation import ContentCreator
from social_media import SocialMediaManager
from social_media.platforms import (
    Instagram,
    Facebook,
    Twitter,
    Tiktok
)

# Import configuration
from automation_stack.config import (
    CONTENT,
    PLATFORMS,
    SCHEDULE,
    LOGGING
)

# Set up logging
logging.basicConfig(
    level=LOGGING['handlers']['console']['level'],
    format=LOGGING['formatters']['standard']['format'],
    datefmt=LOGGING['formatters']['standard']['datefmt']
)

# Set up file logging if configured
if 'file' in LOGGING['handlers']:
    file_handler = logging.FileHandler(LOGGING['handlers']['file']['filename'])
    file_handler.setLevel(LOGGING['handlers']['file']['level'])
    file_handler.setFormatter(logging.Formatter(
        LOGGING['formatters']['standard']['format'],
        LOGGING['formatters']['standard']['datefmt']
    ))
    logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)

class SocialMediaAutomation:
    """
    Main class for the social media automation system.
    Handles content creation, scheduling, and posting to multiple platforms.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the social media automation system.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.content_creator = ContentCreator(CONTENT)
        self.manager = SocialMediaManager()
        self._setup_platforms()
    
    def _setup_platforms(self) -> None:
        """Initialize all enabled social media platforms."""
        platform_classes = {
            'instagram': Instagram,
            'facebook': Facebook,
            'twitter': Twitter,
            'tiktok': Tiktok
        }
        
        for platform_name, platform_config in PLATFORMS.items():
            if platform_config.get('enabled', False):
                try:
                    platform_class = platform_classes.get(platform_name.lower())
                    if platform_class:
                        self.manager.register_platform(platform_name, platform_class(platform_config))
                        logger.info(f"Initialized {platform_name} platform")
                    else:
                        logger.warning(f"No class found for platform: {platform_name}")
                except Exception as e:
                    logger.error(f"Error initializing {platform_name}: {str(e)}")
    
    def create_content(
        self,
        text: str,
        category: str,
        index: int,
        create_video: bool = False,
        audio_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create content for social media posts.
        
        Args:
            text: Text content for the post
            category: Content category (used for organization)
            index: Index number (used for filenames)
            create_video: Whether to create a video version
            audio_path: Optional path to audio file for videos
            
        Returns:
            Dictionary with paths to created content
        """
        result = {}
        
        try:
            # Create image
            image_path = self.content_creator.create_image(
                text=text,
                category=category,
                index=index
            )
            result['image'] = image_path
            logger.info(f"Created image: {image_path}")
            
            # Create video if requested
            if create_video:
                video_path = self.content_creator.create_video(
                    image_path=image_path,
                    audio_path=audio_path,
                    duration=10  # 10 seconds
                )
                result['video'] = video_path
                logger.info(f"Created video: {video_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating content: {str(e)}", exc_info=True)
            raise
    
    def schedule_post(
        self,
        platform: str,
        content_path: str,
        caption: str,
        post_time: Optional[Union[datetime, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Schedule a post for a specific platform.
        
        Args:
            platform: Platform name (instagram, facebook, etc.)
            content_path: Path to the content file
            caption: Post caption
            post_time: When to post (datetime object or ISO format string)
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Dictionary with scheduling details
        """
        return self.manager.schedule_post(
            platform_name=platform,
            content_path=content_path,
            caption=caption,
            post_time=post_time,
            **kwargs
        )
    
    def run_scheduler(self) -> None:
        """Run the scheduler to process scheduled posts."""
        logger.info("Starting social media scheduler...")
        try:
            self.manager.run_scheduler()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}", exc_info=True)
            raise
    
    def create_and_schedule_posts(
        self,
        captions: List[Dict[str, Any]],
        platforms: Optional[List[str]] = None,
        create_videos: bool = False,
        audio_path: Optional[str] = None,
        start_time: Optional[Union[datetime, str]] = None,
        interval_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Create and schedule multiple posts across platforms.
        
        Args:
            captions: List of dictionaries with 'text' and 'category' keys
            platforms: List of platform names to post to (default: all enabled)
            create_videos: Whether to create video versions
            audio_path: Optional path to audio file for videos
            start_time: When to start scheduling posts
            interval_minutes: Minutes between posts
            
        Returns:
            List of scheduled post details
        """
        if not platforms:
            platforms = list(self.manager.platforms.keys())
        
        if not start_time:
            start_time = datetime.now() + timedelta(minutes=5)
        elif isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        
        scheduled_posts = []
        
        for i, item in enumerate(captions):
            text = item.get('text', '')
            category = item.get('category', 'general')
            
            if not text:
                logger.warning(f"Skipping empty caption at index {i}")
                continue
            
            try:
                # Create content
                content = self.create_content(
                    text=text,
                    category=category,
                    index=i,
                    create_video=create_videos,
                    audio_path=audio_path
                )
                
                # Schedule posts for each platform
                for platform in platforms:
                    if platform not in self.manager.platforms:
                        logger.warning(f"Skipping unknown platform: {platform}")
                        continue
                    
                    # Determine content path based on platform
                    content_path = None
                    if platform == 'tiktok' and 'video' in content:
                        content_path = content['video']
                    elif 'image' in content:
                        content_path = content['image']
                    
                    if not content_path:
                        logger.warning(f"No suitable content for {platform}")
                        continue
                    
                    # Schedule the post
                    post_time = start_time + timedelta(minutes=i * interval_minutes)
                    
                    result = self.schedule_post(
                        platform=platform,
                        content_path=content_path,
                        caption=text,
                        post_time=post_time
                    )
                    
                    scheduled_posts.append({
                        'platform': platform,
                        'content_path': content_path,
                        'scheduled_time': post_time.isoformat(),
                        'status': result.get('status', 'unknown')
                    })
                
            except Exception as e:
                logger.error(f"Error processing caption {i}: {str(e)}", exc_info=True)
        
        return scheduled_posts

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Social Media Automation Tool')
    
    # Content creation
    parser.add_argument('--create-content', action='store_true',
                       help='Create content from captions')
    parser.add_argument('--captions-file', type=str,
                       help='Path to JSON file with captions')
    parser.add_argument('--category', type=str, default='general',
                       help='Content category')
    parser.add_argument('--output-dir', type=str,
                       help='Output directory for created content')
    
    # Scheduling
    parser.add_argument('--schedule', action='store_true',
                       help='Schedule posts')
    parser.add_argument('--platforms', type=str, nargs='+',
                       help='List of platforms to post to')
    parser.add_argument('--start-time', type=str,
                       help='Start time for scheduling (ISO format)')
    parser.add_argument('--interval', type=int, default=60,
                       help='Minutes between posts')
    
    # Posting
    parser.add_argument('--post', action='store_true',
                       help='Post content immediately')
    parser.add_argument('--content-path', type=str,
                       help='Path to content file')
    parser.add_argument('--caption', type=str,
                       help='Post caption')
    
    # Run modes
    parser.add_argument('--run-scheduler', action='store_true',
                       help='Run the scheduler')
    
    # Debugging
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    return parser.parse_args()

# def main():  # Legacy CLI entrypoint, now removed. Use FastAPI app only.
    """Main entry point for the script."""
    args = parse_arguments()
    
    # Set up logging level
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    try:
        # Initialize the automation system
        automation = SocialMediaAutomation()
        
        # Handle different modes
        if args.run_scheduler:
            # Run the scheduler
            automation.run_scheduler()
            
        elif args.create_content and args.captions_file:
            # Create content from captions file
            with open(args.captions_file, 'r', encoding='utf-8') as f:
                captions = json.load(f)
            
            automation.create_and_schedule_posts(
                captions=captions,
                platforms=args.platforms,
                create_videos=True,
                start_time=args.start_time,
                interval_minutes=args.interval
            )
            
        elif args.post and args.content_path and args.caption:
            # Post immediately
            if not args.platforms:
                print("Error: Please specify at least one platform with --platforms")
                return
                
            for platform in args.platforms:
                result = automation.schedule_post(
                    platform=platform,
                    content_path=args.content_path,
                    caption=args.caption,
                    post_time=datetime.now() + timedelta(minutes=1)
                )
                print(f"Scheduled post on {platform}: {result}")
        
        else:
            print("No valid action specified. Use --help for usage information.")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)


