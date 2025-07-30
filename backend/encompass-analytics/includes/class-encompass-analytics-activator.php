<?php
/**
 * Fired during plugin activation
 *
 * @package Encompass_MSP_Analytics
 */

// If this file is called directly, abort.
if (!defined('WPINC')) {
    die;
}

/**
 * Fired during plugin activation.
 */
class Encompass_MSP_Analytics_Activator {

    /**
     * Activation function.
     */
    public static function activate(): void {
        self::create_tables();
        self::set_default_options();
    }

    /**
     * Create database tables.
     *
     * @return bool True if tables were created successfully, false otherwise.
     */
    private static function create_tables() {
        global $wpdb;
        $charset_collate = $wpdb->get_charset_collate();
        
        // Include WordPress upgrade functions.
        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
        
        // SQL statements for table creation.
        $sql = array();
        
        // Events table
        $table_name = $wpdb->prefix . 'encompass_events';
        $sql = "
        CREATE TABLE IF NOT EXISTS `$table_name` (
            `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            `event_type` varchar(100) NOT NULL,
            `event_data` longtext,
            `user_id` varchar(100) NOT NULL,
            `session_id` varchar(100) NOT NULL,
            `ip_address` varchar(45) DEFAULT NULL,
            `user_agent` text,
            `page_url` text,
            `referrer` text,
            `time_on_page` int(11) DEFAULT 0,
            `created_at` datetime NOT NULL,
            PRIMARY KEY (`id`),
            KEY `event_type` (`event_type`),
            KEY `user_id` (`user_id`),
            KEY `session_id` (`session_id`),
            KEY `created_at` (`created_at`)
        ) $charset_collate;";
        
        // Sessions table
        $table_name = $wpdb->prefix . 'encompass_sessions';
        $sql[] = "
        CREATE TABLE IF NOT EXISTS `$table_name` (
            `session_id` varchar(100) NOT NULL,
            `user_id` varchar(100) NOT NULL,
            `ip_address` varchar(45) DEFAULT NULL,
            `user_agent` text,
            `referrer` text,
            `landing_page` text,
            `exit_page` text,
            `page_views` int(11) DEFAULT 1,
            `start_time` datetime NOT NULL,
            `end_time` datetime DEFAULT NULL,
            `duration` int(11) DEFAULT 0,
            `is_bounce` tinyint(1) DEFAULT 1,
            `utm_source` varchar(100) DEFAULT NULL,
            `utm_medium` varchar(100) DEFAULT NULL,
            `utm_campaign` varchar(100) DEFAULT NULL,
            `utm_term` varchar(100) DEFAULT NULL,
            `utm_content` varchar(100) DEFAULT NULL,
            `device_type` varchar(50) DEFAULT NULL,
            `browser` varchar(100) DEFAULT NULL,
            `os` varchar(100) DEFAULT NULL,
            `screen_resolution` varchar(20) DEFAULT NULL,
            `country` varchar(100) DEFAULT NULL,
            `city` varchar(100) DEFAULT NULL,
            PRIMARY KEY (`session_id`),
            KEY `user_id` (`user_id`),
            KEY `start_time` (`start_time`),
            KEY `utm_source` (`utm_source`),
            KEY `utm_campaign` (`utm_campaign`)
        ) $charset_collate;";
        
        // Pageviews table
        $table_name = $wpdb->prefix . 'encompass_pageviews';
        $sql[] = "
        CREATE TABLE IF NOT EXISTS `$table_name` (
            `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            `session_id` varchar(100) NOT NULL,
            `page_url` text NOT NULL,
            `page_title` text,
            `referrer` text,
            `time_on_page` int(11) DEFAULT 0,
            `created_at` datetime NOT NULL,
            PRIMARY KEY (`id`),
            KEY `session_id` (`session_id`),
            KEY `created_at` (`created_at`)
        ) $charset_collate;";
        
        // Custom Events table
        $table_name = $wpdb->prefix . 'encompass_custom_events';
        $sql[] = "
        CREATE TABLE IF NOT EXISTS `$table_name` (
            `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            `event_name` varchar(100) NOT NULL,
            `event_data` longtext,
            `user_id` varchar(100) NOT NULL,
            `session_id` varchar(100) NOT NULL,
            `page_url` text,
            `created_at` datetime NOT NULL,
            PRIMARY KEY (`id`),
            KEY `event_name` (`event_name`),
            KEY `user_id` (`user_id`),
            KEY `session_id` (`session_id`),
            KEY `created_at` (`created_at`)
        ) $charset_collate;";
        
        // Execute SQL statements.
        $success = true;
        foreach ($sql as $query) {
            if (false === dbDelta($query)) {
                $success = false;
                error_log('Encompass Analytics: Error executing query - ' . $wpdb->last_error);
            }
        }
        
        // Add database version for future updates.
        if ($success) {
            add_option('encompass_analytics_db_version', ENCOMPASS_ANALYTICS_VERSION);
        }
        
        return $success;
    }

    /**
     * Set default plugin options.
     */
    private static function set_default_options() {
        // General settings.
        add_option('encompass_msp_tracking_enabled', 'yes');
        add_option('encompass_msp_track_admin_users', 'no');
        add_option('encompass_msp_anonymize_ip', 'yes');
        
        // Event tracking settings.
        add_option('encompass_msp_track_outbound_links', 'yes');
        add_option('encompass_msp_track_downloads', 'yes');
        add_option('encompass_msp_track_forms', 'yes');
        add_option('encompass_msp_track_videos', 'yes');
        add_option('encompass_msp_track_clicks', 'no');
        add_option('encompass_msp_track_scroll', 'no');
        add_option('encompass_msp_track_time_on_page', 'yes');
        
        // API settings.
        add_option('encompass_msp_api_key', wp_generate_password(32, false, false));
        
        // Custom tracking code.
        add_option('encompass_msp_custom_tracking_code', '');
    }
}
