<?php
/**
 * Handles all REST API endpoints for the plugin
 */
class Encompass_MSP_REST_API {
    private $namespace = 'encompass/v1';
    private $api_key;
    private $debug_mode;

    public function __construct() {
        $this->api_key = get_option('encompass_msp_api_key', '');
        $this->debug_mode = defined('WP_DEBUG') && WP_DEBUG;
    }

    public function register_routes(): void {
        // Analytics endpoints
        register_rest_route($this->namespace, '/analytics/overview', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_analytics_overview'),
            'permission_callback' => array($this, 'check_permissions')
        ));

        register_rest_route($this->namespace, '/analytics/events', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_events'),
            'permission_callback' => array($this, 'check_permissions')
        ));

        // Event tracking endpoint
        register_rest_route($this->namespace, '/events', array(
            'methods' => 'POST',
            'callback' => array($this, 'track_event'),
            'permission_callback' => '__return_true'
        ));

        // Settings endpoints
        register_rest_route($this->namespace, '/settings', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_settings'),
            'permission_callback' => array($this, 'check_permissions')
        ));

        register_rest_route($this->namespace, '/settings', array(
            'methods' => 'POST',
            'callback' => array($this, 'update_settings'),
            'permission_callback' => array($this, 'check_permissions')
        ));
    }

    public function check_permissions(\WP_REST_Request $request): bool|int {
        // Verify API key
        $api_key = $request->get_header('X-API-Key');
        if ($api_key && $api_key === $this->api_key) {
            return true;
        }

        // Check WordPress nonce for logged-in users
        if (is_user_logged_in() && current_user_can('manage_options')) {
            $nonce = $request->get_header('X-WP-Nonce');
            return wp_verify_nonce($nonce, 'wp_rest');
        }

        return false;
    }

    public function track_event(\WP_REST_Request $request): \WP_REST_Response|\WP_Error {
        $params = $request->get_json_params();
        
        // Basic validation
        if (empty($params['event']) || empty($params['data'])) {
            return new WP_Error('invalid_data', 'Invalid event data', array('status' => 400));
        }

        // Sanitize and prepare data
        $event = sanitize_text_field($params['event']);
        $data = $this->sanitize_event_data($params['data']);

        // Store event in database
        $result = $this->store_event($event, $data);

        if (is_wp_error($result)) {
            return $result;
        }

        return new WP_REST_Response(array(
            'success' => true,
            'event_id' => $result
        ), 200);
    }

    private function store_event($event, $data) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'encompass_events';

        $result = $wpdb->insert(
            $table_name,
            array(
                'event_type' => $event,
                'event_data' => maybe_serialize($data),
                'user_id' => !empty($data['user_id']) ? $data['user_id'] : 'anonymous',
                'session_id' => !empty($data['session_id']) ? $data['session_id'] : '',
                'ip_address' => $this->get_client_ip(),
                'user_agent' => !empty($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : '',
                'page_url' => !empty($data['url']) ? $data['url'] : '',
                'referrer' => !empty($data['referrer']) ? $data['referrer'] : '',
                'time_on_page' => isset($data['time_on_page']) ? (int)$data['time_on_page'] : 0,
                'created_at' => current_time('mysql')
            ),
            array('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s')
        );

        return $result ? $wpdb->insert_id : new WP_Error('db_error', 'Error storing event');
    }

    private function get_client_ip() {
        $ip = '';

        if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
            $ip = $_SERVER['HTTP_CLIENT_IP'];
        } elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
            $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
        } elseif (!empty($_SERVER['REMOTE_ADDR'])) {
            $ip = $_SERVER['REMOTE_ADDR'];
        }

        // Anonymize IP if setting is enabled
        if (get_option('encompass_msp_anonymize_ip', 'yes') === 'yes') {
            if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
                $ip = preg_replace('/\.\d+$/', '.0', $ip);
            } elseif (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) {
                $ip = preg_replace('/:[0-9a-f]{0,4}$/', ':0000', $ip);
            }
        }

        return $ip;
    }

    private function sanitize_event_data($data) {
        if (!is_array($data)) {
            return array();
        }

        $sanitized = array();
        foreach ($data as $key => $value) {
            $sanitized[sanitize_key($key)] = is_array($value) 
                ? $this->sanitize_event_data($value)
                : sanitize_text_field($value);
        }

        return $sanitized;
    }

    public function get_analytics_overview(\WP_REST_Request $request): \WP_REST_Response|array {
        $params = $request->get_params();
        $start_date = date('Y-m-d', strtotime('-30 days'));
        $end_date = date('Y-m-d');
        
        if (isset($params['start_date']) && !empty($params['start_date'])) {
            $start_date = sanitize_text_field($params['start_date']);
        }
        
        if (isset($params['end_date']) && !empty($params['end_date'])) {
            $end_date = sanitize_text_field($params['end_date']);
        }

        global $wpdb;
        $table_name = $wpdb->prefix . 'encompass_events';
        
        $query = $wpdb->prepare(
            "SELECT 
                COUNT(DISTINCT session_id) as sessions,
                COUNT(DISTINCT user_id) as users,
                COUNT(*) as events,
                AVG(time_on_page) as avg_time_on_page
             FROM $table_name
             WHERE created_at BETWEEN %s AND %s",
            [$start_date, $end_date . ' 23:59:59']
        );

        $data = $wpdb->get_row($query, ARRAY_A);

        // Get top pages
        $top_pages = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT 
                    event_data->>'$.url' as page_url,
                    COUNT(*) as pageviews,
                    COUNT(DISTINCT session_id) as unique_pageviews,
                    AVG(time_on_page) as avg_time_on_page
                 FROM $table_name
                 WHERE event_type = 'page_view'
                 AND created_at BETWEEN %s AND %s
                 GROUP BY event_data->>'$.url'
                 ORDER BY pageviews DESC
                 LIMIT 10",
                [$start_date, $end_date . ' 23:59:59']
            ),
            ARRAY_A
        );

        return rest_ensure_response([
            'success' => true,
            'data' => [
                'overview' => $data,
                'top_pages' => $top_pages
            ]
        ]);
    }

    public function get_events(\WP_REST_Request $request): \WP_REST_Response|array {
        $params = $request->get_params();
        $start_date = isset($params['start_date']) ? $params['start_date'] : date('Y-m-d', strtotime('-7 days'));
        $end_date = isset($params['end_date']) ? $params['end_date'] : date('Y-m-d');
        $event_type = isset($params['event_type']) ? $params['event_type'] : '';
        $per_page = min(absint(isset($params['per_page']) ? $params['per_page'] : 10), 100);
        $page = max(1, absint(isset($params['page']) ? $params['page'] : 1));
        $offset = ($page - 1) * $per_page;

        global $wpdb;
        $table_name = $wpdb->prefix . 'encompass_events';
        
        // Build query
        $where = ['created_at BETWEEN %s AND %s'];
        $query_args = [$start_date, $end_date . ' 23:59:59'];
        
        if ($event_type) {
            $where[] = 'event_type = %s';
            $query_args[] = $event_type;
        }

        // Get events
        $events = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT * FROM $table_name 
                 WHERE " . implode(' AND ', $where) . " 
                 ORDER BY created_at DESC 
                 LIMIT %d OFFSET %d",
                array_merge($query_args, [$per_page, $offset])
            ),
            ARRAY_A
        );

        // Get total count for pagination
        $total = $wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(*) FROM $table_name WHERE " . implode(' AND ', $where),
                $query_args
            )
        );

        // Process event data
        foreach ($events as &$event) {
            $event['event_data'] = maybe_unserialize($event['event_data']);
        }

        return rest_ensure_response([
            'success' => true,
            'data' => $events,
            'pagination' => [
                'total' => (int)$total,
                'per_page' => $per_page,
                'current_page' => $page,
                'total_pages' => ceil($total / $per_page)
            ]
        ]);
    }

    public function get_settings(\WP_REST_Request $request): \WP_REST_Response|array {
        $settings = [
            'api_key' => $this->api_key,
            'tracking_enabled' => get_option('encompass_msp_tracking_enabled', 'yes'),
            'track_admin_users' => get_option('encompass_msp_track_admin_users', 'no'),
            'anonymize_ip' => get_option('encompass_msp_anonymize_ip', 'yes'),
            'track_outbound_links' => get_option('encompass_msp_track_outbound_links', 'yes'),
            'track_downloads' => get_option('encompass_msp_track_downloads', 'yes'),
            'track_forms' => get_option('encompass_msp_track_forms', 'yes'),
            'track_videos' => get_option('encompass_msp_track_videos', 'yes'),
            'track_clicks' => get_option('encompass_msp_track_clicks', 'no'),
            'track_scroll' => get_option('encompass_msp_track_scroll', 'no'),
            'track_time_on_page' => get_option('encompass_msp_track_time_on_page', 'yes'),
            'custom_tracking_code' => get_option('encompass_msp_custom_tracking_code', '')
        ];

        return rest_ensure_response([
            'success' => true,
            'data' => $settings
        ]);
    }

    public function update_settings(\WP_REST_Request $request): \WP_REST_Response|array {
        $params = $request->get_params();
        $updated = [];

        // Update settings
        $settings = [
            'encompass_msp_api_key' => 'api_key',
            'encompass_msp_tracking_enabled' => 'tracking_enabled',
            'encompass_msp_track_admin_users' => 'track_admin_users',
            'encompass_msp_anonymize_ip' => 'anonymize_ip',
            'encompass_msp_track_outbound_links' => 'track_outbound_links',
            'encompass_msp_track_downloads' => 'track_downloads',
            'encompass_msp_track_forms' => 'track_forms',
            'encompass_msp_track_videos' => 'track_videos',
            'encompass_msp_track_clicks' => 'track_clicks',
            'encompass_msp_track_scroll' => 'track_scroll',
            'encompass_msp_track_time_on_page' => 'track_time_on_page',
            'encompass_msp_custom_tracking_code' => 'custom_tracking_code'
        ];

        foreach ($settings as $option => $param) {
            if (isset($params[$param])) {
                $value = sanitize_text_field($params[$param]);
                update_option($option, $value);
                $updated[$param] = $value;
            }
        }

        // Update API key in instance if it was changed
        if (isset($updated['api_key'])) {
            $this->api_key = $updated['api_key'];
        }

        return rest_ensure_response([
            'success' => true,
            'message' => 'Settings updated successfully',
            'data' => $updated
        ]);
    }
}
