<?php
/**
 * API Handler for the Encompass Feedback System
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class Encompass_Feedback_API {
    private $namespace = 'encompass-feedback/v1';
    
    public function __construct() {
        // Register REST API routes
        add_action('rest_api_init', array($this, 'register_routes'));
        
        // Add custom endpoints for AJAX compatibility
        add_action('wp_ajax_encompass_feedback_api', array($this, 'handle_ajax_request'));
        add_action('wp_ajax_nopriv_encompass_feedback_api', array($this, 'handle_ajax_request'));
    }
    
    /**
     * Register REST API routes
     */
    public function register_routes() {
        // Get feedback list
        register_rest_route($this->namespace, '/feedback', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_feedback'),
            'permission_callback' => array($this, 'check_admin_permission'),
            'args' => $this->get_collection_params(),
        ));
        
        // Get single feedback
        register_rest_route($this->namespace, '/feedback/(?P<id>\d+)', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_feedback_item'),
            'permission_callback' => array($this, 'check_admin_permission'),
        ));
        
        // Create feedback
        register_rest_route($this->namespace, '/feedback', array(
            'methods' => 'POST',
            'callback' => array($this, 'create_feedback'),
            'permission_callback' => '__return_true',
        ));
        
        // Update feedback
        register_rest_route($this->namespace, '/feedback/(?P<id>\d+)', array(
            'methods' => 'POST',
            'callback' => array($this, 'update_feedback'),
            'permission_callback' => array($this, 'check_admin_permission'),
        ));
        
        // Delete feedback
        register_rest_route($this->namespace, '/feedback/(?P<id>\d+)', array(
            'methods' => 'DELETE',
            'callback' => array($this, 'delete_feedback'),
            'permission_callback' => array($this, 'check_admin_permission'),
        ));
        
        // Get feedback summary
        register_rest_route($this->namespace, '/feedback/summary', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_feedback_summary'),
            'permission_callback' => array($this, 'check_admin_permission'),
        ));
        
        // Get feedback types
        register_rest_route($this->namespace, '/feedback/types', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_feedback_types'),
            'permission_callback' => array($this, 'check_admin_permission'),
        ));
        
        // Get feedback statuses
        register_rest_route($this->namespace, '/feedback/statuses', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_feedback_statuses'),
            'permission_callback' => array($this, 'check_admin_permission'),
        ));
    }
    
    /**
     * Handle AJAX requests for the API
     */
    public function handle_ajax_request() {
        // Check nonce
        check_ajax_referer('encompass_feedback_admin_nonce', 'nonce');
        
        // Check permissions
        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('You do not have permission to perform this action.', 'encompass-feedback')), 403);
        }
        
        // Get request method
        $method = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : 'GET';
        
        // Get route
        $route = isset($_REQUEST['route']) ? sanitize_text_field($_REQUEST['route']) : '';
        
        // Get request data
        $data = $_REQUEST;
        unset($data['action'], $data['route'], $data['nonce']);
        
        // Handle the request
        $response = $this->handle_request($method, $route, $data);
        
        // Send response
        if (is_wp_error($response)) {
            wp_send_json_error(array('message' => $response->get_error_message()), $response->get_error_code());
        } else {
            wp_send_json_success($response);
        }
    }
    
    /**
     * Handle REST API request
     */
    public function handle_rest_request($request) {
        $method = $request->get_method();
        $route = $request->get_route();
        
        // Remove namespace from route
        $route = str_replace('/' . $this->namespace, '', $route);
        
        // Get request data
        $data = $request->get_params();
        
        // Handle the request
        $response = $this->handle_request($method, $route, $data);
        
        // Return response
        if (is_wp_error($response)) {
            return $response;
        }
        
        return rest_ensure_response($response);
    }
    
    /**
     * Handle API request
     */
    private function handle_request($method, $route, $data) {
        global $encompass_feedback_db;
        
        if (empty($encompass_feedback_db)) {
            $encompass_feedback_db = new Encompass_Feedback_DB();
        }
        
        // Parse route to get endpoint and ID
        $route_parts = explode('/', trim($route, '/'));
        $endpoint = $route_parts[0] ?? '';
        $id = $route_parts[1] ?? 0;
        
        // Route the request
        switch ($method) {
            case 'GET':
                if ($endpoint === 'feedback') {
                    if ($id) {
                        return $this->get_feedback_item($id);
                    } else {
                        return $this->get_feedback($data);
                    }
                } elseif ($endpoint === 'summary') {
                    return $this->get_feedback_summary($data);
                } elseif ($endpoint === 'types') {
                    return $this->get_feedback_types();
                } elseif ($endpoint === 'statuses') {
                    return $this->get_feedback_statuses();
                }
                break;
                
            case 'POST':
                if ($endpoint === 'feedback') {
                    if ($id) {
                        return $this->update_feedback($id, $data);
                    } else {
                        return $this->create_feedback($data);
                    }
                }
                break;
                
            case 'DELETE':
                if ($endpoint === 'feedback' && $id) {
                    return $this->delete_feedback($id);
                }
                break;
        }
        
        return new WP_Error('invalid_endpoint', __('Invalid API endpoint.', 'encompass-feedback'), array('status' => 404));
    }
    
    /**
     * Get collection parameters for the API
     */
    public function get_collection_params() {
        return array(
            'page' => array(
                'description' => __('Current page of the collection.', 'encompass-feedback'),
                'type' => 'integer',
                'default' => 1,
                'sanitize_callback' => 'absint',
                'validate_callback' => 'rest_validate_request_arg',
                'minimum' => 1,
            ),
            'per_page' => array(
                'description' => __('Maximum number of items to be returned in result set.', 'encompass-feedback'),
                'type' => 'integer',
                'default' => 10,
                'minimum' => 1,
                'maximum' => 100,
                'sanitize_callback' => 'absint',
                'validate_callback' => 'rest_validate_request_arg',
            ),
            'search' => array(
                'description' => __('Limit results to those matching a string.', 'encompass-feedback'),
                'type' => 'string',
                'sanitize_callback' => 'sanitize_text_field',
                'validate_callback' => 'rest_validate_request_arg',
            ),
            'status' => array(
                'description' => __('Limit result set to feedback assigned specific statuses.', 'encompass-feedback'),
                'type' => 'array',
                'items' => array(
                    'type' => 'string',
                    'enum' => array_keys($this->get_feedback_statuses()),
                ),
                'default' => array('new'),
                'sanitize_callback' => array($this, 'sanitize_status'),
                'validate_callback' => 'rest_validate_request_arg',
            ),
            'type' => array(
                'description' => __('Limit result set to feedback assigned specific types.', 'encompass-feedback'),
                'type' => 'array',
                'items' => array(
                    'type' => 'string',
                ),
                'sanitize_callback' => 'wp_parse_list',
                'validate_callback' => 'rest_validate_request_arg',
            ),
            'user_id' => array(
                'description' => __('Limit result set to feedback from a specific user ID.', 'encompass-feedback'),
                'type' => 'integer',
                'sanitize_callback' => 'absint',
                'validate_callback' => 'rest_validate_request_arg',
            ),
            'date_after' => array(
                'description' => __('Limit response to resources published after a given ISO8601 compliant date.', 'encompass-feedback'),
                'type' => 'string',
                'format' => 'date-time',
                'validate_callback' => 'rest_validate_request_arg',
            ),
            'date_before' => array(
                'description' => __('Limit response to resources published before a given ISO8601 compliant date.', 'encompass-feedback'),
                'type' => 'string',
                'format' => 'date-time',
                'validate_callback' => 'rest_validate_request_arg',
            ),
            'orderby' => array(
                'description' => __('Sort collection by object attribute.', 'encompass-feedback'),
                'type' => 'string',
                'default' => 'date',
                'enum' => array(
                    'date',
                    'id',
                    'rating',
                    'status',
                    'type',
                ),
                'validate_callback' => 'rest_validate_request_arg',
            ),
            'order' => array(
                'description' => __('Order sort attribute ascending or descending.', 'encompass-feedback'),
                'type' => 'string',
                'default' => 'desc',
                'enum' => array(
                    'asc',
                    'desc',
                ),
                'validate_callback' => 'rest_validate_request_arg',
            ),
        );
    }
    
    /**
     * Sanitize status parameter
     */
    public function sanitize_status($value, $request, $param) {
        $statuses = array_keys($this->get_feedback_statuses());
        
        if (is_string($value)) {
            $value = explode(',', $value);
        }
        
        return array_intersect($value, $statuses);
    }
    
    /**
     * Check if the current user has admin permissions
     */
    public function check_admin_permission($request) {
        return current_user_can('manage_options');
    }
    
    /**
     * Get feedback items
     */
    public function get_feedback($request) {
        global $encompass_feedback_db;
        
        $args = array(
            'number' => $request->get_param('per_page') ?: 10,
            'offset' => ($request->get_param('page') ?: 1 - 1) * $request->get_param('per_page'),
            'orderby' => $request->get_param('orderby') ?: 'created_at',
            'order' => $request->get_param('order') ?: 'DESC',
            'status' => $request->get_param('status') ?: '',
            'feedback_type' => $request->get_param('type') ?: '',
            'user_id' => $request->get_param('user_id') ?: '',
            'date_from' => $request->get_param('date_after') ?: '',
            'date_to' => $request->get_param('date_before') ?: '',
            'search' => $request->get_param('search') ?: '',
        );
        
        // Get feedback items
        $feedback = $encompass_feedback_db->get_feedback_list($args);
        
        // Get total count for pagination
        $total = $encompass_feedback_db->get_feedback_count($args);
        
        // Prepare response
        $response = array(
            'data' => array(),
            'pagination' => array(
                'total' => $total,
                'pages' => ceil($total / $args['number']),
                'page' => (int) $request->get_param('page') ?: 1,
                'per_page' => (int) $args['number'],
            ),
        );
        
        // Format each feedback item
        foreach ($feedback as $item) {
            $response['data'][] = $this->prepare_feedback_for_response($item);
        }
        
        return $response;
    }
    
    /**
     * Get a single feedback item
     */
    public function get_feedback_item($request) {
        global $encompass_feedback_db;
        
        $id = is_object($request) ? $request->get_param('id') : $request;
        $feedback = $encompass_feedback_db->get_feedback($id);
        
        if (!$feedback) {
            return new WP_Error('rest_feedback_invalid_id', __('Invalid feedback ID.', 'encompass-feedback'), array('status' => 404));
        }
        
        return $this->prepare_feedback_for_response($feedback);
    }
    
    /**
     * Create a new feedback item
     */
    public function create_feedback($request) {
        global $encompass_feedback_db;
        
        $data = is_object($request) ? $request->get_params() : $request;
        
        // Validate required fields
        $required_fields = array(
            'feedback_type' => __('Feedback Type', 'encompass-feedback'),
            'comment' => __('Comment', 'encompass-feedback'),
        );
        
        $errors = array();
        
        foreach ($required_fields as $field => $label) {
            if (empty($data[$field])) {
                $errors[] = sprintf(__('%s is a required field.', 'encompass-feedback'), $label);
            }
        }
        
        // Return errors if any
        if (!empty($errors)) {
            return new WP_Error('missing_fields', implode(' ', $errors), array('status' => 400));
        }
        
        // Prepare feedback data
        $feedback_data = array(
            'user_id' => get_current_user_id() ?: null,
            'feedback_type' => sanitize_text_field($data['feedback_type']),
            'rating' => isset($data['rating']) ? absint($data['rating']) : null,
            'comment' => sanitize_textarea_field($data['comment']),
            'page_url' => isset($data['page_url']) ? esc_url_raw($data['page_url']) : '',
            'page_title' => isset($data['page_title']) ? sanitize_text_field($data['page_title']) : '',
            'status' => 'new',
        );
        
        // Add meta data
        $meta_data = array(
            'name' => isset($data['name']) ? sanitize_text_field($data['name']) : '',
            'email' => isset($data['email']) ? sanitize_email($data['email']) : '',
            'user_ip' => $this->get_client_ip(),
            'user_agent' => isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : '',
        );
        
        // Save feedback
        $feedback_id = $encompass_feedback_db->add_feedback($feedback_data);
        
        if (!$feedback_id) {
            return new WP_Error('db_error', __('Failed to save feedback.', 'encompass-feedback'), array('status' => 500));
        }
        
        // Save meta data
        foreach ($meta_data as $meta_key => $meta_value) {
            $encompass_feedback_db->add_meta($feedback_id, $meta_key, $meta_value);
        }
        
        // Trigger action
        do_action('encompass_feedback_created', $feedback_id, $feedback_data, $meta_data);
        
        // Get the created feedback
        $feedback = $encompass_feedback_db->get_feedback($feedback_id);
        
        return $this->prepare_feedback_for_response($feedback);
    }
    
    /**
     * Update a feedback item
     */
    public function update_feedback($id, $request) {
        global $encompass_feedback_db;
        
        $id = is_object($id) ? $id->get_param('id') : $id;
        $data = is_object($request) ? $request->get_params() : $request;
        
        // Get existing feedback
        $feedback = $encompass_feedback_db->get_feedback($id);
        
        if (!$feedback) {
            return new WP_Error('rest_feedback_invalid_id', __('Invalid feedback ID.', 'encompass-feedback'), array('status' => 404));
        }
        
        // Prepare update data
        $update_data = array();
        
        // Update status if provided
        if (isset($data['status'])) {
            $statuses = $this->get_feedback_statuses();
            
            if (array_key_exists($data['status'], $statuses)) {
                $update_data['status'] = $data['status'];
            }
        }
        
        // Update assigned_to if provided
        if (isset($data['assigned_to'])) {
            $update_data['assigned_to'] = absint($data['assigned_to']);
        }
        
        // Update priority if provided
        if (isset($data['priority'])) {
            $priorities = array('low', 'medium', 'high');
            
            if (in_array($data['priority'], $priorities)) {
                $update_data['priority'] = $data['priority'];
            }
        }
        
        // Update comment if provided
        if (isset($data['comment'])) {
            $update_data['comment'] = sanitize_textarea_field($data['comment']);
        }
        
        // Update the feedback if we have data to update
        if (!empty($update_data)) {
            $result = $wpdb->update(
                $encompass_feedback_db->table_feedback,
                $update_data,
                array('id' => $id),
                array_fill(0, count($update_data), '%s'),
                array('%d')
            );
            
            if ($result === false) {
                return new WP_Error('db_error', __('Failed to update feedback.', 'encompass-feedback'), array('status' => 500));
            }
            
            // Clear cache
            wp_cache_delete($id, 'encompass_feedback');
            
            // Trigger action
            do_action('encompass_feedback_updated', $id, $update_data);
        }
        
        // Update meta data if provided
        if (isset($data['meta']) && is_array($data['meta'])) {
            foreach ($data['meta'] as $meta_key => $meta_value) {
                $encompass_feedback_db->update_meta($id, $meta_key, $meta_value);
            }
        }
        
        // Get the updated feedback
        $feedback = $encompass_feedback_db->get_feedback($id);
        
        return $this->prepare_feedback_for_response($feedback);
    }
    
    /**
     * Delete a feedback item
     */
    public function delete_feedback($request) {
        global $encompass_feedback_db;
        
        $id = is_object($request) ? $request->get_param('id') : $request;
        
        // Check if feedback exists
        $feedback = $encompass_feedback_db->get_feedback($id);
        
        if (!$feedback) {
            return new WP_Error('rest_feedback_invalid_id', __('Invalid feedback ID.', 'encompass-feedback'), array('status' => 404));
        }
        
        // Delete the feedback
        $result = $encompass_feedback_db->delete_feedback($id);
        
        if (!$result) {
            return new WP_Error('db_error', __('Failed to delete feedback.', 'encompass-feedback'), array('status' => 500));
        }
        
        // Trigger action
        do_action('encompass_feedback_deleted', $id);
        
        return array(
            'deleted' => true,
            'previous' => $this->prepare_feedback_for_response($feedback),
        );
    }
    
    /**
     * Get feedback summary
     */
    public function get_feedback_summary($request = array()) {
        global $encompass_feedback_db;
        
        $args = array();
        
        if (is_object($request)) {
            $args = array(
                'date_from' => $request->get_param('date_after') ?: '',
                'date_to' => $request->get_param('date_before') ?: '',
                'feedback_type' => $request->get_param('type') ?: '',
                'status' => $request->get_param('status') ?: '',
            );
        } elseif (is_array($request)) {
            $args = $request;
        }
        
        // Get summary data
        $summary = $encompass_feedback_db->get_feedback_summary(
            $args['date_from'] ?? '',
            $args['date_to'] ?? ''
        );
        
        // Get counts by status
        $status_counts = $encompass_feedback_db->get_feedback_count_by_status();
        
        // Get counts by type
        $type_counts = $encompass_feedback_db->get_feedback_count_by_type();
        
        // Get average rating
        $average_rating = $encompass_feedback_db->get_average_rating();
        
        // Prepare response
        $response = array(
            'total' => array_sum(wp_list_pluck($status_counts, 'count')),
            'statuses' => $status_counts,
            'types' => $type_counts,
            'average_rating' => number_format($average_rating, 1),
            'summary' => $summary,
        );
        
        return $response;
    }
    
    /**
     * Get available feedback types
     */
    public function get_feedback_types() {
        return apply_filters('encompass_feedback_types', array(
            'general' => __('General Feedback', 'encompass-feedback'),
            'bug' => __('Bug Report', 'encompass-feedback'),
            'suggestion' => __('Suggestion', 'encompass-feedback'),
            'praise' => __('Praise', 'encompass-feedback'),
        ));
    }
    
    /**
     * Get available feedback statuses
     */
    public function get_feedback_statuses() {
        return apply_filters('encompass_feedback_statuses', array(
            'new' => __('New', 'encompass-feedback'),
            'in_progress' => __('In Progress', 'encompass-feedback'),
            'resolved' => __('Resolved', 'encompass-feedback'),
            'closed' => __('Closed', 'encompass-feedback'),
            'spam' => __('Spam', 'encompass-feedback'),
        ));
    }
    
    /**
     * Prepare feedback item for API response
     */
    private function prepare_feedback_for_response($feedback) {
        // Get user data
        $user = $feedback->user_id ? get_userdata($feedback->user_id) : null;
        
        // Get assigned user
        $assigned_to = $feedback->assigned_to ? get_userdata($feedback->assigned_to) : null;
        
        // Prepare response
        $response = array(
            'id' => (int) $feedback->id,
            'user' => $user ? array(
                'id' => $user->ID,
                'name' => $user->display_name,
                'email' => $user->user_email,
                'avatar' => get_avatar_url($user->ID, array('size' => 96)),
            ) : null,
            'feedback_type' => $feedback->feedback_type,
            'feedback_type_label' => $this->get_feedback_type_label($feedback->feedback_type),
            'rating' => $feedback->rating ? (int) $feedback->rating : null,
            'comment' => $feedback->comment,
            'page_url' => $feedback->page_url,
            'page_title' => $feedback->page_title,
            'status' => $feedback->status,
            'status_label' => $this->get_status_label($feedback->status),
            'assigned_to' => $assigned_to ? array(
                'id' => $assigned_to->ID,
                'name' => $assigned_to->display_name,
                'email' => $assigned_to->user_email,
                'avatar' => get_avatar_url($assigned_to->ID, array('size' => 96)),
            ) : null,
            'priority' => $feedback->priority ?: 'medium',
            'created_at' => mysql_to_rfc3339($feedback->created_at),
            'updated_at' => mysql_to_rfc3339($feedback->updated_at),
            'meta' => $feedback->meta ?? array(),
        );
        
        return apply_filters('encompass_prepare_feedback_for_response', $response, $feedback);
    }
    
    /**
     * Get feedback type label
     */
    private function get_feedback_type_label($type) {
        $types = $this->get_feedback_types();
        return isset($types[$type]) ? $types[$type] : ucfirst($type);
    }
    
    /**
     * Get status label
     */
    private function get_status_label($status) {
        $statuses = $this->get_feedback_statuses();
        return isset($statuses[$status]) ? $statuses[$status] : ucfirst(str_replace('_', ' ', $status));
    }
    
    /**
     * Get client IP address
     */
    private function get_client_ip() {
        $ip = '';
        
        if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
            $ip = $_SERVER['HTTP_CLIENT_IP'];
        } elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
            $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
        } elseif (!empty($_SERVER['REMOTE_ADDR'])) {
            $ip = $_SERVER['REMOTE_ADDR'];
        }
        
        // Handle multiple IPs in X-Forwarded-For
        if (strpos($ip, ',') !== false) {
            $ips = explode(',', $ip);
            $ip = trim($ips[0]);
        }
        
        return filter_var($ip, FILTER_VALIDATE_IP) ? $ip : '0.0.0.0';
    }
}
