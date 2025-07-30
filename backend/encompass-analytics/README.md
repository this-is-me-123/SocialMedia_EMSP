# Encompass Analytics for WordPress

A comprehensive analytics and marketing plugin for WordPress, designed specifically for Encompass MSP to track and analyze website traffic and user behavior.

## Features

- Real-time visitor tracking
- Page view analytics
- User behavior analysis
- Event tracking (clicks, downloads, form submissions)
- Traffic source analysis
- Device and browser statistics
- Customizable dashboard
- GDPR compliance tools
- Marketing campaign tracking

## Requirements

- WordPress 5.6 or higher
- PHP 7.4 or higher
- MySQL 5.6 or higher
- cURL extension enabled
- JSON extension enabled

## Installation

### Method 1: WordPress Admin Dashboard

1. Log in to your WordPress admin dashboard
2. Navigate to **Plugins** > **Add New**
3. Click **Upload Plugin**
4. Select the `encompass-analytics.zip` file
5. Click **Install Now**
6. After installation, click **Activate Plugin**

### Method 2: Manual Installation via FTP/SFTP

1. Download the plugin zip file
2. Extract the `encompass-analytics` folder to your computer
3. Connect to your web server using an FTP/SFTP client
4. Navigate to `/wp-content/plugins/`
5. Upload the `encompass-analytics` folder
6. Log in to your WordPress admin dashboard
7. Navigate to **Plugins**
8. Find **Encompass Analytics** in the list and click **Activate**

## Configuration

### Initial Setup

1. After activation, go to **Analytics** > **Settings** in your WordPress admin
2. Configure the following settings:
   - **General Settings**: Enable/disable tracking, configure admin user tracking
   - **Event Tracking**: Choose which events to track (clicks, downloads, forms, etc.)
   - **Privacy**: Configure IP anonymization and data retention policies
   - **Advanced**: Custom tracking code and API settings

3. Save your settings

### Adding Tracking Code

The plugin will automatically add the necessary tracking code to your site. No additional code needs to be added to your theme files.

### Verifying Installation

1. Visit your website in a new incognito/private browsing window
2. Browse a few pages
3. Go to **Analytics** > **Dashboard** in your WordPress admin
4. You should see your visit in the analytics data

## Usage

### Dashboard Overview

The main dashboard provides an overview of your website's performance, including:

- Visitor statistics
- Page views
- Bounce rate
- Average session duration
- Top pages
- Traffic sources
- Device distribution
- Recent activity

### Reports

Access detailed reports under **Analytics** > **Reports** to analyze:

- Page performance
- User behavior
- Traffic sources
- Conversion tracking
- Custom events

### Event Tracking

Track custom events using the following JavaScript API:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Track a custom event
    if (typeof encompassTrackEvent === 'function') {
        encompassTrackEvent('Category', 'Action', 'Label', 'Value');
    }
});
```

## Troubleshooting

### Common Issues

1. **No data is being recorded**
   - Ensure the plugin is activated
   - Check that tracking is enabled in the settings
   - Clear your browser cache and test in incognito mode
   - Verify that your theme's `wp_footer()` function is present

2. **JavaScript errors**
   - Check your browser's console for errors
   - Ensure no other plugins are conflicting
   - Try temporarily switching to a default WordPress theme

3. **Performance issues**
   - Disable unused tracking features
   - Increase PHP memory limit if needed
   - Consider using a caching plugin with compatibility mode

### Debugging

To enable debug mode:

1. Add these lines to your `wp-config.php`:
   ```php
   define('WP_DEBUG', true);
   define('WP_DEBUG_LOG', true);
   define('WP_DEBUG_DISPLAY', false);
   ```

2. Check the debug log at `/wp-content/debug.log` for any errors

## Updating

### Automatic Updates

The plugin supports automatic updates through the WordPress update system. You'll be notified in your WordPress admin when updates are available.

### Manual Updates

1. Deactivate the current version of the plugin
2. Delete the plugin (your data will be preserved)
3. Install the new version following the installation instructions

## Uninstallation

### Removing the Plugin

1. Go to **Plugins** > **Installed Plugins**
2. Find **Encompass Analytics** and click **Deactivate**
3. Click **Delete** to remove the plugin

### Data Removal

By default, the plugin will remove all its data when uninstalled. To keep your data:

1. Go to **Analytics** > **Settings** > **Advanced**
2. Check the option "Keep data on uninstall"
3. Click **Save Changes**
4. Deactivate and delete the plugin

## Support

For support, please contact:
- Email: support@encompass-msp.com
- Phone: (555) 123-4567
- Website: [www.encompass-msp.com/support](https://www.encompass-msp.com/support)

## License

This plugin is proprietary software developed for Encompass MSP. Unauthorized distribution or modification is prohibited.

## Changelog

### 1.0.0
- Initial release
- Core tracking functionality
- Dashboard and reporting
- Event tracking
- GDPR compliance features
