# Social Media Automation Stack for Health & Beauty Influencers

This repository contains a complete set of tools and configurations to automate your social media presence as a Health & Beauty influencer.

## 🚀 Getting Started

---

## ⚡ Backend Developer Onboarding

This section documents how to set up, configure, and run the backend automation stack for developers and deployers.

### 1. Backend Setup & Dependency Installation

- **Python 3.8+** required
- Recommended: Create a virtual environment
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Required Environment Variables

Create a `.env` file or set these variables in your environment:

- **Database & Cache:**
  - `POSTGRES_URL` (e.g., `postgresql://user:password@localhost:5432/dbname`)
  - `REDIS_URL` (e.g., `redis://localhost:6379/0`)
- **Social Media API Keys:**
  - `FACEBOOK_ACCESS_TOKEN`, `FACEBOOK_PAGE_ID`
  - `INSTAGRAM_API_KEY`, `INSTAGRAM_PAGE_ID`
  - `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`
  - `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`
- **AI/Content Generation:**
  - `OPENAI_API_KEY`, `OPENAI_MODEL`
  - `STABLE_DIFFUSION_API_URL`, `STABLE_DIFFUSION_API_KEY`
- **Email Notifications:**
  - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_TO`
- **Other:**
  - Any additional custom keys referenced in `config.py`

### 3. Running the Backend

- **FastAPI Server:**
  ```bash
  uvicorn automation_stack.main:app --reload
  ```
  The API will be available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

- **Health Check Server:**
  ```bash
  python automation_stack/health.py
  ```
  Or run as a FastAPI endpoint if enabled.

- **Database Initialization:**
  ```bash
  python automation_stack/init_db.py
  ```

### 4. API Endpoints & Usage

- **Swagger/OpenAPI docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Authentication:**
  - JWT Bearer tokens are required for most endpoints. Obtain a token via `/api/auth/login` and include it as `Authorization: Bearer <token>` in requests.
  - Registration and login endpoints do not require authentication.
  - For demo, users are stored in-memory; use a real DB for production.
- **CORS:**
  - CORS is restricted by `CORS_ALLOW_ORIGINS` env var. Defaults to localhost for dev.

#### **Endpoints**

| Endpoint                | Method | Auth Required | Description                       |
|------------------------|--------|---------------|-----------------------------------|
| `/api/auth/register`   | POST   | No            | Register a new user               |
| `/api/auth/login`      | POST   | No            | Obtain JWT access token           |
| `/api/post`            | POST   | Yes           | Create and schedule a new post    |
| `/api/post/{id}`       | GET    | Yes           | Get a single post by ID           |
| `/api/posts`           | GET    | Yes           | List all posts                    |
| `/api/post/{id}/cancel`| POST   | Yes           | Cancel a scheduled post           |
| `/api/analytics`       | GET    | Yes           | Get analytics summary             |
| `/api/analytics/event` | POST   | Yes           | Log analytics event               |
| `/api/health`          | GET    | No            | Health check                      |

#### **Authentication Flow**

1. **Register:**
   - `POST /api/auth/register`
   - Form fields: `username`, `password`
   - Example:
     ```bash
     curl -X POST http://localhost:8000/api/auth/register \
       -d 'username=testuser' -d 'password=secret'
     ```
2. **Login:**
   - `POST /api/auth/login`
   - Form fields: `username`, `password`
   - Returns: `{ "access_token": "...", "token_type": "bearer" }`
   - Example:
     ```bash
     curl -X POST http://localhost:8000/api/auth/login \
       -d 'username=testuser' -d 'password=secret'
     ```
3. **Authenticated Requests:**
   - Include header: `Authorization: Bearer <access_token>`
   - Example:
     ```bash
     curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/posts
     ```

#### **Example: Create Post**
- `POST /api/post`
- Body (JSON):
  ```json
  {
    "platform": "instagram",
    "content": "Check out our new product!",
    "caption": "Exciting news!",
    "scheduled_time": "2025-08-04T18:00:00Z",
    "media_urls": [],
    "metadata": {}
  }
  ```
- Auth required: Yes

#### **Example: Get Analytics**
- `GET /api/analytics`
- Auth required: Yes
- Returns: Analytics summary (see Swagger docs for schema)

#### **Health Check**
- `GET /health`
- No authentication required
- Returns: `{ "status": "ok" }`

For full request/response schemas, see [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

### 5. Developer Tips

- Use `.env` for local development and do not commit secrets.
- Logging is printed to the console; configure file/system logging for production.
- See code comments and `config.py` for more details on configuration.
- For any issues, check the logs and ensure all environment variables are set.

---


### Prerequisites
- Google Account (for Google Drive, Analytics, etc.)
- Social Media Accounts (Instagram, TikTok, Facebook, Twitter)
- Email for account creation on various platforms

## 🛠️ Automation Stack

### 1. Content Creation & Management

#### Canva (Free)
- **Setup**:
  1. Create an account at [canva.com](https://www.canva.com/)
  2. Set up your brand kit with colors, fonts, and logo
  3. Create templates for different post types
- **Templates Included**:
  - Instagram Post (1080x1080)
  - Instagram Story (1080x1920)
  - TikTok Cover (1080x1920)
  - Pinterest Pin (1000x1500)

#### CapCut (Free)
- **Setup**:
  1. Download from [capcut.com](https://www.capcut.com/)
  2. Import your brand assets
  3. Create video templates for Reels/TikToks

### 2. Scheduling & Posting

#### Buffer (Free Plan)
- **Setup**:
  1. Sign up at [buffer.com](https://buffer.com/)
  2. Connect your social accounts
  3. Set up posting schedule
- **Configuration**:
  - 3 posts per day (1x Instagram, 1x TikTok, 1x Twitter)
  - Best times: 9 AM, 12 PM, 6 PM (your timezone)

#### TweetDeck (Free)
- **Setup**:
  1. Log in with your Twitter at [tweetdeck.twitter.com](https://tweetdeck.twitter.com/)
  2. Set up columns for:
     - Mentions
     - DMs
     - Hashtags (#BeautyTips, #SkincareRoutine, etc.)

### 3. Analytics & Monitoring

#### Google Analytics 4 (Free)
- **Setup**:
  1. Go to [analytics.google.com](https://analytics.google.com/)
  2. Create a new property
  3. Add tracking code to your website
- **Key Metrics to Track**:
  - Traffic sources
  - User engagement
  - Conversion from social media

#### Brand24 (Free Trial)
- **Setup**:
  1. Sign up at [brand24.com](https://brand24.com/)
  2. Set up mentions tracking for:
     - Your brand name
     - Relevant hashtags
     - Competitors

### 4. Engagement & Growth

#### Followerwonk (Free)
- **Setup**:
  1. Connect your Twitter
  2. Analyze your followers
  3. Find influencers to engage with

#### Hashtagify (Free)
- **Setup**:
  1. Go to [hashtagify.me](https://hashtagify.me/)
  2. Research trending beauty hashtags
  3. Create hashtag groups for different post types

## 📂 File Structure

```
automation_stack/
│
├── assets/                  # Brand assets
│   ├── logos/
│   ├── fonts/
│   └── color-palette.json
│
├── content/                 # Content library
│   ├── captions/
│   ├── hashtags/
│   └── templates/
│
├── analytics/               # Analytics exports
│   ├── weekly-reports/
│   └── monthly-reports/
│
└── README.md               # This file
```

## ⚙️ Automation Workflow

1. **Content Planning (Weekly)**
   - Plan content using the content calendar
   - Create batch content (graphics, videos)
   - Write captions and prepare hashtags

2. **Scheduling (Twice a Week)**
   - Schedule posts in Buffer
   - Set up Twitter threads in TweetDeck
   - Plan engagement activities

3. **Engagement (Daily, 3x per day)**
   - Morning: Respond to comments/DMs
   - Afternoon: Engage with followers
   - Evening: Schedule next day's posts

4. **Analytics (Weekly/Monthly)**
   - Export reports
   - Analyze performance
   - Adjust strategy

## 📊 Performance Tracking

### Weekly Metrics to Track:
- Follower growth rate
- Engagement rate (likes, comments, shares)
- Click-through rate (CTR) on links
- Best performing content

## 🔄 Maintenance

- Update content templates monthly
- Refresh hashtag lists bi-weekly
- Backup all content weekly
- Review and update automation rules monthly

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

💡 **Pro Tip**: Always maintain a balance between automated and personal engagement. Automation should enhance, not replace, genuine interactions with your audience.
