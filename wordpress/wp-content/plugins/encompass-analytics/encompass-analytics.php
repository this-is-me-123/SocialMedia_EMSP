<?php
/**
 * Plugin Name: Encompass Analytics & Marketing
 * Plugin URI: https://www.encompass-msp.com/
 * Description: Enhanced analytics and marketing features for Encompass MSP
 * Version: 1.0.0
 * Author: Encompass MSP
 * Author URI: https://www.encompass-msp.com/
 * Text Domain: encompass-analytics
 * Domain Path: /languages
 * Requires at least: 5.6
 * Requires PHP: 7.4
 *
 * @package Encompass_Analytics
 */

// If this file is called directly, abort.
if (!defined('WPINC')) {
    die;
}

// Define plugin constants
define('ENCOMPASS_ANALYTICS_VERSION', '1.0.0');
define('ENCOMPASS_ANALYTICS_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('ENCOMPASS_ANALYTICS_PLUGIN_URL', plugin_dir_url(__FILE__));

// Include required files
require_once ENCOMPASS_ANALYTICS_PLUGIN_DIR . 'includes/class-encompass-analytics.php';
require_once ENCOMPASS_ANALYTICS_PLUGIN_DIR . 'includes/class-encompass-rest-api.php';
require_once ENCOMPASS_ANALYTICS_PLUGIN_DIR . 'public/class-encompass-analytics-public.php';
require_once ENCOMPASS_ANALYTICS_PLUGIN_DIR . 'admin/class-encompass-analytics-admin.php';

// Initialize the plugin
function run_encompass_analytics() {
    // Initialize the core plugin class
    $plugin = new Encompass_MSP_Analytics();
    $plugin->run();

    // Register REST API endpoints
    if (file_exists(dirname(__FILE__) . '/includes/class-encompass-analytics-rest.php')) {
        require_once dirname(__FILE__) . '/includes/class-encompass-analytics-rest.php';
        new Encompass_MSP_Analytics_REST();
    }
}
run_encompass_analytics();

// Activation and deactivation hooks
register_activation_hook(__FILE__, 'encompass_analytics_activate');
register_deactivation_hook(__FILE__, 'encompass_analytics_deactivate');

function encompass_analytics_activate() {
    require_once ENCOMPASS_ANALYTICS_PLUGIN_DIR . 'includes/class-encompass-analytics-activator.php';
    Encompass_MSP_Analytics_Activator::activate();
    
    // Schedule any required cron jobs
    if (!wp_next_scheduled('encompass_analytics_daily_cleanup')) {
        wp_schedule_event(time(), 'daily', 'encompass_analytics_daily_cleanup');
    }
    
    // Flush rewrite rules
    flush_rewrite_rules();
}

function encompass_analytics_deactivate() {
    require_once ENCOMPASS_ANALYTICS_PLUGIN_DIR . 'includes/class-encompass-analytics-deactivator.php';
    Encompass_MSP_Analytics_Deactivator::deactivate();
    
    // Clear scheduled hooks
    wp_clear_scheduled_hook('encompass_analytics_daily_cleanup');
    
    // Flush rewrite rules
    flush_rewrite_rules();
}
