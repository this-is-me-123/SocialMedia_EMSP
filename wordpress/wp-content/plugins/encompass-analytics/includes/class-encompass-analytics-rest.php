<?php
/**
 * REST API endpoints for Encompass Analytics plugin settings and data.
 */
class Encompass_MSP_Analytics_REST {
    public function __construct() {
        add_action('rest_api_init', array($this, 'register_routes'));
    }

    public function register_routes() {
        register_rest_route('encompass/v1', '/settings', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_settings'),
            'permission_callback' => '__return_true', // Make public or restrict as needed
        ));
    }

    public function get_settings($request) {
        $options = array(
            'tracking_enabled' => get_option('encompass_msp_tracking_enabled', 'yes'),
            'track_admin_users' => get_option('encompass_msp_track_admin_users', 'no'),
            'anonymize_ip' => get_option('encompass_msp_anonymize_ip', 'yes'),
            'api_key' => get_option('encompass_msp_api_key', ''),
            'track_outbound_links' => get_option('encompass_msp_track_outbound_links', 'yes'),
            'track_downloads' => get_option('encompass_msp_track_downloads', 'yes'),
            'track_forms' => get_option('encompass_msp_track_forms', 'yes'),
            'track_videos' => get_option('encompass_msp_track_videos', 'yes'),
            'track_clicks' => get_option('encompass_msp_track_clicks', 'no'),
            'track_scroll' => get_option('encompass_msp_track_scroll', 'no'),
            'track_time_on_page' => get_option('encompass_msp_track_time_on_page', 'yes'),
            'custom_tracking_code' => get_option('encompass_msp_custom_tracking_code', ''),
        );
        return rest_ensure_response($options);
    }
}
