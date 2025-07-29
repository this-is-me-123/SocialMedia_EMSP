# WordPress Marketing Automation Setup

This directory contains the configuration and automation scripts for the Encompass MSP WordPress marketing system. The setup includes email marketing, SEO optimization, social media integration, conversion rate optimization, and CRM integration.

## Features

- **Email Marketing**: Mailchimp integration with automated drip campaigns
- **SEO Optimization**: On-page and technical SEO with Yoast SEO
- **Social Media**: Auto-posting and social proof integration
- **Conversion Optimization**: A/B testing and exit-intent popups
- **CRM Integration**: HubSpot CRM integration for lead management
- **Analytics**: Comprehensive tracking and reporting

## Prerequisites

- WordPress 5.8 or higher
- PHP 7.4 or higher
- MySQL 5.7 or higher
- WP-CLI installed on the server
- Command line access to the server

## Installation

1. **Copy the configuration file**:
   ```bash
   cp marketing_config.example.json marketing_config.json
   ```

2. **Edit the configuration**:
   Update `marketing_config.json` with your specific settings:
   - WordPress admin credentials
   - API keys for third-party services
   - Email marketing settings
   - Social media accounts
   - CRM configuration

3. **Run the setup script**:
   ```bash
   python3 setup_marketing_tools.py
   ```

## Configuration

### Email Marketing

Edit the `email_marketing` section in `marketing_config.json`:

```json
"email_marketing": {
  "provider": "mailchimp",
  "api_key": "your_mailchimp_api_key",
  "list_id": "your_audience_id",
  "enable_drip_campaigns": true
}
```

### SEO Settings

Configure SEO settings in the `seo` section:

```json
"seo": {
  "enable_yoast": true,
  "site_name": "Encompass MSP",
  "site_description": "Managed IT Services & Digital Marketing Solutions"
}
```

### Social Media

Set up social media integration:

```json
"social_media": {
  "facebook_pixel_id": "1234567890",
  "enable_auto_posting": true,
  "auto_post_to": ["facebook", "twitter", "linkedin"]
}
```

### CRM Integration

Configure CRM settings:

```json
"crm": {
  "enable_crm": true,
  "crm_provider": "hubspot",
  "api_key": "your_hubspot_api_key"
}
```

## Usage

### Running the Setup

```bash
python3 setup_marketing_tools.py
```

### Scheduled Tasks

Set up the following cron jobs for automated tasks:

```bash
# Daily content digest
0 8 * * * /usr/bin/python3 /path/to/wordpress/send_daily_digest.py

# Weekly analytics report
0 9 * * 1 /usr/bin/python3 /path/to/wordpress/send_weekly_report.py

# Monthly maintenance
0 7 1 * * /usr/bin/python3 /path/to/wordpress/run_monthly_maintenance.py
```

## Maintenance

### Updating the Configuration

1. Edit the `marketing_config.json` file
2. Run the setup script again:
   ```bash
   python3 setup_marketing_tools.py
   ```

### Monitoring Logs

Check the log file for any issues:

```bash
tail -f marketing_setup.log
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure the script has execute permissions:
     ```bash
     chmod +x setup_marketing_tools.py
     ```

2. **Missing Dependencies**
   - Install required Python packages:
     ```bash
     pip3 install -r requirements.txt
     ```

3. **WP-CLI Not Found**
   - Ensure WP-CLI is installed and in your PATH
   - Or specify the full path in the configuration

## Security Considerations

1. **Protect Sensitive Data**
   - Never commit `marketing_config.json` to version control
   - Add it to `.gitignore`
   - Use environment variables for production credentials

2. **File Permissions**
   - Set appropriate file permissions:
     ```bash
     chmod 600 marketing_config.json
     chmod 700 ./
     ```

## Support

For support, please contact the development team at [support@encompass-msp.com](mailto:support@encompass-msp.com).

## License

This project is proprietary software. All rights reserved © Encompass MSP.
