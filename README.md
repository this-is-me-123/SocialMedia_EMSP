# Social Media Automation System

A fully automated social media content generation and posting system that supports Instagram, Facebook, Twitter/X, and TikTok with AI-driven content creation.

## 🚀 Features

- **Fully Automated**: No manual intervention after initial setup
- **Multi-Platform Support**: Instagram, Facebook, Twitter/X, TikTok
- **AI Content Generation**: GPT-4 for captions, Stable Diffusion for images
- **Scheduling System**: Automated daily posting with customizable schedules
- **Analytics Dashboard**: Track posting status and engagement metrics
- **Mock Mode**: Test without real API calls during development

## 📋 Prerequisites

- Python 3.8+
- API keys for social media platforms
- OpenAI API key (optional, for AI content generation)
- Stable Diffusion API access (optional, for AI image generation)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SocialMedia_EMSP
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.template .env
   # Edit .env file with your actual API keys and credentials
   ```

## ⚙️ Configuration

### Environment Variables

Copy `env.template` to `.env` and configure the following:

#### Required Platform Credentials

**Instagram:**
- `INSTAGRAM_ENABLED=true`
- `INSTAGRAM_ACCESS_TOKEN=your_token`
- `INSTAGRAM_PAGE_ID=your_page_id`

**Facebook:**
- `FACEBOOK_ENABLED=true`
- `FACEBOOK_ACCESS_TOKEN=your_token`
- `FACEBOOK_PAGE_ID=your_page_id`

**Twitter:**
- `TWITTER_ENABLED=true`
- `TWITTER_API_KEY=your_api_key`
- `TWITTER_API_SECRET=your_api_secret`
- `TWITTER_ACCESS_TOKEN=your_access_token`
- `TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret`

**TikTok:**
- `TIKTOK_ENABLED=true`
- `TIKTOK_API_KEY=your_api_key`

#### Optional AI Integration

**OpenAI (for AI captions):**
- `OPENAI_API_KEY=your_openai_key`
- `OPENAI_MODEL=gpt-4`

**Stable Diffusion (for AI images):**
- `SD_API_URL=your_sd_api_url`
- `SD_API_KEY=your_sd_api_key`

### Getting API Keys

#### Instagram & Facebook
1. Create a Facebook Developer account
2. Create a new app and get Graph API access
3. Generate long-lived access tokens
4. Get your Page ID from Facebook Page settings

#### Twitter
1. Apply for Twitter Developer account
2. Create a new app in Twitter Developer Portal
3. Generate API keys and access tokens
4. Enable OAuth 1.0a authentication

#### TikTok
1. Apply for TikTok for Developers
2. Create a new app and get approval
3. Generate API credentials

## 🚀 Usage

### Basic Usage

1. **Start the FastAPI server**
   ```bash
   cd backend
   python -m uvicorn automation_stack.main:app --reload
   ```

2. **Run the automation system**
   ```bash
   python enhanced_automation.py --help
   ```

### Command Line Options

```bash
# Test platform connections
python enhanced_automation.py --test-connection instagram

# Create and schedule posts
python enhanced_automation.py --create-posts --platforms instagram facebook

# Run the scheduler (for automated posting)
python enhanced_automation.py --run-scheduler

# Enable testing mode (uses mock APIs)
python enhanced_automation.py --testing
```

### Web Interface

1. Start the FastAPI server
2. Open your browser to `http://localhost:8000`
3. Access the analytics dashboard at `http://localhost:8000/analytics_dashboard.html`

## 📊 Analytics Dashboard

The system includes a web-based analytics dashboard that shows:
- Recent posting activity
- Platform-specific metrics
- Error logs and status updates
- Scheduled posts queue

Access it at: `http://localhost:8000/analytics_dashboard.html`

## 🔧 Development

### Testing Mode

For development and testing, enable testing mode:

```bash
# In .env file
TESTING=true

# Or via command line
python enhanced_automation.py --testing
```

This enables mock mode for all platforms, allowing you to test without making real API calls.

### Project Structure

```
backend/
├── automation_stack/          # Core automation logic
│   ├── social_media/         # Platform integrations
│   │   └── platforms/        # Individual platform implementations
│   ├── content_creation/     # AI content generation
│   └── main.py              # FastAPI application
├── config/                   # Configuration management
├── database/                 # Database models and operations
├── enhanced_automation.py    # Main CLI interface
└── requirements.txt         # Python dependencies

frontend/                     # Web interface files
├── analytics_dashboard.html
├── login.html
└── scheduled_posts_dashboard.html
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the `backend` directory
   - Check that all dependencies are installed

2. **API Authentication Failures**
   - Verify all API keys are correct in `.env`
   - Check that tokens haven't expired
   - Ensure proper permissions for social media accounts

3. **Database Issues**
   - Database file will be created automatically
   - Check file permissions in the backend directory

4. **Content Generation Failures**
   - Verify OpenAI API key if using AI content generation
   - Check Stable Diffusion API configuration
   - Ensure content directory exists and is writable

### Logs

Check the log file for detailed error information:
```bash
tail -f social_media_automation.log
```

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📞 Support

[Add support contact information here]
