<?php
/**
 * The public-facing functionality of the plugin.
 */
class Encompass_MSP_Analytics_Public {
    private $plugin_name;
    private $version;
    private $tracking_enabled;
    private $track_admin_users;
    private $tracking_settings;
    private $nonce;

    public function __construct($plugin_name, $version) {
        add_action('init', array($this, 'defer_init_actions'));
        $this->plugin_name = $plugin_name;
        $this->version = $version;
        $this->tracking_enabled = get_option('encompass_msp_tracking_enabled', 'yes') === 'yes';
        $this->track_admin_users = get_option('encompass_msp_track_admin_users', 'no') === 'yes';
    }

    public function defer_init_actions() {
        // Place all wp_create_nonce and other pluggable function calls here
        $this->nonce = wp_create_nonce('wp_rest');
        
        // Defer admin user tracking check until init
        add_action('init', array($this, 'maybe_disable_tracking_for_admin'));
        
        // Defer tracking settings initialization to init
        add_action('init', array($this, 'initialize_tracking_settings'));
        
        // Add actions and filters
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_styles'));
        add_action('wp_footer', array($this, 'add_tracking_code'));
        
        // Add API endpoint for client-side tracking
        add_action('wp_ajax_encompass_track_event', array($this, 'track_event'));
        add_action('wp_ajax_nopriv_encompass_track_event', array($this, 'track_event'));
    }

    /**
     * Disable tracking for admin users if needed (run on init).
     */
    public function maybe_disable_tracking_for_admin() {
        if (current_user_can('manage_options') && !$this->track_admin_users) {
            $this->tracking_enabled = false;
        }
    }

    public function initialize_tracking_settings(): void {
        $this->tracking_settings = array(
            'trackOutboundLinks' => get_option('encompass_msp_track_outbound_links', 'yes') === 'yes',
            'trackDownloads' => get_option('encompass_msp_track_downloads', 'yes') === 'yes',
            'trackForms' => get_option('encompass_msp_track_forms', 'yes') === 'yes',
            'trackVideos' => get_option('encompass_msp_track_videos', 'yes') === 'yes',
            'trackClicks' => get_option('encompass_msp_track_clicks', 'no') === 'yes',
            'trackScroll' => get_option('encompass_msp_track_scroll', 'no') === 'yes',
            'trackTimeOnPage' => get_option('encompass_msp_track_time_on_page', 'yes') === 'yes',
            'anonymizeIp' => get_option('encompass_msp_anonymize_ip', 'yes') === 'yes',
            'apiUrl' => rest_url('encompass/v1/'),
            'nonce' => wp_create_nonce('wp_rest'),
            'currentUser' => is_user_logged_in() ? get_current_user_id() : 0,
            'postId' => get_the_ID(),
            'postType' => get_post_type(),
            'isSingle' => is_singular(),
            'isArchive' => is_archive(),
            'isSearch' => is_search(),
            'is404' => is_404(),
            'isFrontPage' => is_front_page(),
            'isHome' => is_home(),
            'referrer' => isset($_SERVER['HTTP_REFERER']) ? esc_url_raw(wp_unslash($_SERVER['HTTP_REFERER'])) : ''
        );
    }

    public function enqueue_styles(): void {
        // Only load if tracking is enabled
        if (!$this->tracking_enabled) {
            return;
        }
        
        // Enqueue public styles
        wp_enqueue_style(
            $this->plugin_name,
            ENCOMPASS_ANALYTICS_PLUGIN_URL . 'public/css/encompass-analytics-public.css',
            array(),
            $this->version,
            'all'
        );
    }

    public function enqueue_scripts(): void {
        // Only load if tracking is enabled
        if (!$this->tracking_enabled) {
            return;
        }
        
        // Enqueue the main tracking script
        wp_enqueue_script(
            $this->plugin_name,
            ENCOMPASS_ANALYTICS_PLUGIN_URL . 'public/js/encompass-analytics-public.js',
            array('jquery'),
            $this->version,
            true
        );
        
        // Localize the script with tracking settings
        wp_localize_script(
            $this->plugin_name,
            'encompassAnalytics',
            $this->tracking_settings
        );
    }
    
    public function add_tracking_code(): void {
        // Only add tracking code if enabled
        if (!$this->tracking_enabled) {
            return;
        }
        
        // Add custom tracking code if set
        $custom_code = get_option('encompass_msp_custom_tracking_code', '');
        if (!empty($custom_code)) {
            echo "\n" . '<!-- Encompass Analytics Custom Tracking Code -->' . "\n";
            echo $custom_code . "\n";
            echo '<!-- /Encompass Analytics Custom Tracking Code -->' . "\n\n";
        }
        
        // Add noscript fallback
        echo '<noscript><img src="' . esc_url(rest_url('encompass/v1/track/noscript?_wpnonce=' . wp_create_nonce('wp_rest'))) . '" alt="" style="display:none;" /></noscript>' . "\n";
    }
    
    public function track_event(): void {
        // Verify nonce
        if (!isset($_POST['_wpnonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['_wpnonce'])), 'wp_rest')) {
            wp_send_json_error('Invalid nonce', 403);
        }
        
        // Get event data
        $event_data = isset($_POST['data']) ? $this->sanitize_event_data(wp_unslash($_POST['data'])) : array();
        $event_type = isset($_POST['event']) ? sanitize_text_field(wp_unslash($_POST['event'])) : '';
        
        if (empty($event_type)) {
            wp_send_json_error('Event type is required', 400);
        }
        
        // Add additional context to event data
        $event_data['user_id'] = is_user_logged_in() ? get_current_user_id() : 'anonymous';
        $event_data['session_id'] = $this->get_session_id();
        $event_data['url'] = isset($_SERVER['HTTP_REFERER']) ? esc_url_raw(wp_unslash($_SERVER['HTTP_REFERER'])) : '';
        $event_data['page_title'] = wp_get_document_title();
        
        // Send event to REST API
        $response = wp_remote_post(
            rest_url('encompass/v1/events'),
            array(
                'method' => 'POST',
                'headers' => array(
                    'X-WP-Nonce' => wp_create_nonce('wp_rest'),
                    'Content-Type' => 'application/json',
                ),
                'body' => wp_json_encode(array(
                    'event' => $event_type,
                    'data' => $event_data
                ))
            )
        );
        
        if (is_wp_error($response)) {
            wp_send_json_error($response->get_error_message(), 500);
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        $body = json_decode(wp_remote_retrieve_body($response), true);
        
        if ($status_code >= 200 && $status_code < 300) {
            wp_send_json_success($body);
        } else {
            wp_send_json_error($body, $status_code);
        }
    }
    
    private function get_session_id() {
        if (isset($_COOKIE['_encompass_session'])) {
            return sanitize_text_field(wp_unslash($_COOKIE['_encompass_session']));
        }
        
        // Generate a new session ID
        $session_id = wp_generate_uuid4();
        
        // Set session cookie (30 days expiration)
        setcookie('_encompass_session', $session_id, time() + (DAY_IN_SECONDS * 30), COOKIEPATH, COOKIE_DOMAIN, is_ssl(), true);
        
        return $session_id;
    }
    
    private function sanitize_event_data(array $data): array {
        if (!is_array($data)) {
            return array();
        }
        
        $sanitized = array();
        
        foreach ($data as $key => $value) {
            if (is_array($value)) {
                $sanitized[sanitize_key($key)] = $this->sanitize_event_data($value);
            } else {
                $sanitized[sanitize_key($key)] = sanitize_text_field($value);
            }
        }
        
        return $sanitized;
    }
}
