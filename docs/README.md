# Social Media Automation System

A Python-based system for automating content creation and posting to multiple social media platforms. This system supports Instagram, Facebook, Twitter, and TikTok with advanced scheduling, monitoring, and error handling capabilities.

## Features

- **Multi-Platform Support**: Post to Instagram, Facebook, Twitter, and TikTok
- **Advanced Scheduling**: Schedule posts with precise timing and timezone support
- **Content Management**: Queue and monitor posts with status tracking
- **Mock Mode**: Test without posting to live platforms
- **Rate Limiting**: Built-in rate limiting to prevent API bans
- **Error Handling**: Comprehensive error handling and retry logic
- **Command-Line Interface**: Easy-to-use CLI for all operations

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd social-media-automation
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your API credentials:
   ```env
   # Instagram
   INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
   INSTAGRAM_PAGE_ID=your_instagram_page_id
   
   # Facebook
   FACEBOOK_APP_ID=your_facebook_app_id
   FACEBOOK_APP_SECRET=your_facebook_app_secret
   FACEBOOK_PAGE_ID=your_facebook_page_id
   
   # Twitter
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_SECRET=your_twitter_access_secret
   
   # TikTok
   TIKTOK_APP_ID=your_tiktok_app_id
   TIKTOK_APP_SECRET=your_tiktok_app_secret
   ```

## Command Line Interface

The enhanced automation system provides a command-line interface for all operations:

### 1. Schedule a Post

Schedule a post to one or more platforms:

```bash
python enhanced_automation.py schedule instagram path/to/image.jpg "Your caption here" --time "2023-01-01T12:00:00"
```

For immediate posting (within 5 minutes):
```bash
python enhanced_automation.py schedule instagram path/to/image.jpg "Your caption here" --time now
```

### 2. List Scheduled Posts

View all scheduled posts (optionally filter by status):

```bash
# List all scheduled posts
python enhanced_automation.py list

# List only failed posts
python enhanced_automation.py list --status failed
```

### 3. Cancel a Scheduled Post

Cancel a scheduled post by its ID:

```bash
python enhanced_automation.py cancel POST_ID
```

### 4. Run the Scheduler

Start the scheduler to process scheduled posts:

```bash
# Run with default settings (checks every 60 seconds)
python enhanced_automation.py run

# Run with custom check interval
python enhanced_automation.py run --interval 300  # Check every 5 minutes
```

### 5. Test Platform Connections

Test connections to social media platforms:

```bash
# Test all enabled platforms
python enhanced_automation.py test

# Test a specific platform
python enhanced_automation.py test instagram
```

## Project Structure

```
social-media-automation/
├── automation_stack/
│   ├── __init__.py
│   ├── main.py                 # Original main script
│   ├── enhanced_automation.py  # Enhanced automation script with CLI
│   ├── config.py               # Configuration settings
│   └── social_media/           # Platform integrations
│       ├── __init__.py
│       ├── base.py             # Base platform class
│       ├── manager.py          # Basic manager
│       ├── enhanced_manager.py # Enhanced manager with advanced features
│       └── platforms/
│           ├── __init__.py
│           ├── base.py         # Base platform implementation
│           ├── instagram.py    # Instagram platform
│           ├── facebook.py     # Facebook platform
│           ├── twitter.py      # Twitter platform
│           └── tiktok.py       # TikTok platform
├── test_output/               # Test output files
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with your API credentials:

```env
# Instagram
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
INSTAGRAM_API_KEY=your_api_key

# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id

# Twitter
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# TikTok
TIKTOK_USERNAME=your_username
TIKTOK_PASSWORD=your_password
TIKTOK_API_KEY=your_api_key

# General
TIMEZONE=America/New_York
LOG_LEVEL=INFO
```

### Platform Configuration

Edit `config.py` to customize platform settings, rate limits, and other options.

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/feature-name`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/feature-name`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.

---

*This project was created for educational purposes and should be used in compliance with the terms of service of each social media platform.*
