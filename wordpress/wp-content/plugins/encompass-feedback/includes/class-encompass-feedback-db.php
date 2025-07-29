<?php
/**
 * Database handler for the Encompass Feedback System
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class Encompass_Feedback_DB {
    private $table_feedback;
    private $table_feedback_meta;
    private $charset_collate;

    public function __construct() {
        global $wpdb;
        
        $this->table_feedback = $wpdb->prefix . 'encompass_feedback';
        $this->table_feedback_meta = $wpdb->prefix . 'encompass_feedback_meta';
        $this->charset_collate = $wpdb->get_charset_collate();
    }

    /**
     * Create the necessary database tables
     */
    public function create_tables() {
        global $wpdb;
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        
        // Main feedback table
        $sql = "CREATE TABLE {$this->table_feedback} (
            id bigint(20) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) DEFAULT NULL,
            feedback_type varchar(50) NOT NULL,
            rating int(2) DEFAULT NULL,
            comment text,
            page_url varchar(255) DEFAULT NULL,
            page_title varchar(255) DEFAULT NULL,
            user_agent text,
            user_ip varchar(100) DEFAULT NULL,
            status varchar(20) DEFAULT 'new',
            assigned_to bigint(20) DEFAULT NULL,
            priority varchar(10) DEFAULT 'medium',
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY  (id),
            KEY user_id (user_id),
            KEY feedback_type (feedback_type),
            KEY status (status),
            KEY created_at (created_at)
        ) {$this->charset_collate};";
        
        dbDelta($sql);
        
        // Feedback meta table for additional fields
        $sql = "CREATE TABLE {$this->table_feedback_meta} (
            meta_id bigint(20) NOT NULL AUTO_INCREMENT,
            feedback_id bigint(20) NOT NULL,
            meta_key varchar(255) NOT NULL,
            meta_value longtext,
            PRIMARY KEY  (meta_id),
            KEY feedback_id (feedback_id),
            KEY meta_key (meta_key(191))
        ) {$this->charset_collate};";
        
        dbDelta($sql);
    }
    
    /**
     * Add new feedback
     * 
     * @param array $data Feedback data
     * @return int|false Feedback ID on success, false on failure
     */
    public function add_feedback($data) {
        global $wpdb;
        
        $defaults = array(
            'user_id' => get_current_user_id() ?: null,
            'feedback_type' => 'general',
            'rating' => null,
            'comment' => '',
            'page_url' => isset($_SERVER['HTTP_REFERER']) ? esc_url_raw($_SERVER['HTTP_REFERER']) : '',
            'page_title' => '',
            'user_agent' => isset($_SERVER['HTTP_USER_AGENT']) ? sanitize_text_field($_SERVER['HTTP_USER_AGENT']) : '',
            'user_ip' => $this->get_client_ip(),
            'status' => 'new',
            'assigned_to' => null,
            'priority' => 'medium',
            'created_at' => current_time('mysql'),
            'meta' => array()
        );
        
        $data = wp_parse_args($data, $defaults);
        
        // Extract meta data
        $meta = $data['meta'];
        unset($data['meta']);
        
        // Insert feedback
        $result = $wpdb->insert(
            $this->table_feedback,
            $data,
            array(
                '%d', // user_id
                '%s', // feedback_type
                '%d', // rating
                '%s', // comment
                '%s', // page_url
                '%s', // page_title
                '%s', // user_agent
                '%s', // user_ip
                '%s', // status
                '%d', // assigned_to
                '%s', // priority
                '%s', // created_at
            )
        );
        
        if (!$result) {
            return false;
        }
        
        $feedback_id = $wpdb->insert_id;
        
        // Add meta data
        if (!empty($meta) && is_array($meta)) {
            foreach ($meta as $key => $value) {
                $this->add_meta($feedback_id, $key, $value);
            }
        }
        
        // Trigger action
        do_action('encompass_feedback_added', $feedback_id, $data, $meta);
        
        return $feedback_id;
    }
    
    /**
     * Get feedback by ID
     * 
     * @param int $feedback_id Feedback ID
     * @return object|false Feedback object or false if not found
     */
    public function get_feedback($feedback_id) {
        global $wpdb;
        
        $feedback_id = absint($feedback_id);
        $feedback = $wpdb->get_row(
            $wpdb->prepare("SELECT * FROM {$this->table_feedback} WHERE id = %d", $feedback_id)
        );
        
        if (!$feedback) {
            return false;
        }
        
        // Get meta data
        $feedback->meta = $this->get_meta($feedback_id);
        
        return $feedback;
    }
    
    /**
     * Get feedback list
     * 
     * @param array $args Query arguments
     * @return array Array of feedback objects
     */
    public function get_feedback_list($args = array()) {
        global $wpdb;
        
        $defaults = array(
            'number' => 20,
            'offset' => 0,
            'orderby' => 'created_at',
            'order' => 'DESC',
            'status' => '',
            'feedback_type' => '',
            'user_id' => '',
            'date_from' => '',
            'date_to' => '',
            'search' => '',
        );
        
        $args = wp_parse_args($args, $defaults);
        
        // Build the query
        $where = array('1=1');
        $values = array();
        
        // Status filter
        if (!empty($args['status'])) {
            $where[] = 'status = %s';
            $values[] = $args['status'];
        }
        
        // Feedback type filter
        if (!empty($args['feedback_type'])) {
            $where[] = 'feedback_type = %s';
            $values[] = $args['feedback_type'];
        }
        
        // User ID filter
        if (!empty($args['user_id'])) {
            $where[] = 'user_id = %d';
            $values[] = absint($args['user_id']);
        }
        
        // Date range filter
        if (!empty($args['date_from'])) {
            $where[] = 'created_at >= %s';
            $values[] = $args['date_from'];
        }
        
        if (!empty($args['date_to'])) {
            $where[] = 'created_at <= %s';
            $values[] = $args['date_to'] . ' 23:59:59';
        }
        
        // Search
        if (!empty($args['search'])) {
            $search = '%' . $wpdb->esc_like($args['search']) . '%';
            $where[] = '(comment LIKE %s OR page_title LIKE %s)';
            $values[] = $search;
            $values[] = $search;
        }
        
        // Build the query
        $where_clause = implode(' AND ', $where);
        $orderby = sanitize_sql_orderby($args['orderby'] . ' ' . $args['order']);
        
        // Get feedback
        $query = $wpdb->prepare(
            "SELECT * FROM {$this->table_feedback} WHERE {$where_clause} ORDER BY {$orderby} LIMIT %d, %d",
            array_merge($values, array($args['offset'], $args['number']))
        );
        
        $feedback = $wpdb->get_results($query);
        
        // Get meta data for each feedback
        foreach ($feedback as $item) {
            $item->meta = $this->get_meta($item->id);
        }
        
        return $feedback;
    }
    
    /**
     * Get feedback summary for charts
     * 
     * @param string $start_date Start date (YYYY-MM-DD)
     * @param string $end_date End date (YYYY-MM-DD)
     * @return array Summary data
     */
    public function get_feedback_summary($start_date = '', $end_date = '') {
        global $wpdb;
        
        $where = array('1=1');
        $values = array();
        
        // Date range
        if (!empty($start_date)) {
            $where[] = 'DATE(created_at) >= %s';
            $values[] = $start_date;
        }
        
        if (!empty($end_date)) {
            $where[] = 'DATE(created_at) <= %s';
            $values[] = $end_date;
        }
        
        $where_clause = implode(' AND ', $where);
        
        // Get summary by date
        $query = $wpdb->prepare(
            "SELECT 
                DATE(created_at) as date,
                COUNT(*) as total,
                AVG(rating) as avg_rating,
                SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as neutral_count,
                SUM(CASE WHEN rating < 3 AND rating > 0 THEN 1 ELSE 0 END) as negative_count
             FROM {$this->table_feedback}
             WHERE {$where_clause}
             GROUP BY DATE(created_at)
             ORDER BY date ASC",
            $values
        );
        
        return $wpdb->get_results($query);
    }
    
    /**
     * Get feedback grouped by type
     * 
     * @param string $start_date Start date (YYYY-MM-DD)
     * @param string $end_date End date (YYYY-MM-DD)
     * @return array Feedback by type
     */
    public function get_feedback_by_type($start_date = '', $end_date = '') {
        global $wpdb;
        
        $where = array('1=1');
        $values = array();
        
        // Date range
        if (!empty($start_date)) {
            $where[] = 'DATE(created_at) >= %s';
            $values[] = $start_date;
        }
        
        if (!empty($end_date)) {
            $where[] = 'DATE(created_at) <= %s';
            $values[] = $end_date;
        }
        
        $where_clause = implode(' AND ', $where);
        
        $query = $wpdb->prepare(
            "SELECT 
                feedback_type,
                COUNT(*) as count,
                AVG(rating) as avg_rating
             FROM {$this->table_feedback}
             WHERE {$where_clause}
             GROUP BY feedback_type
             ORDER BY count DESC",
            $values
        );
        
        return $wpdb->get_results($query);
    }
    
    /**
     * Get feedback by page
     * 
     * @param string $start_date Start date (YYYY-MM-DD)
     * @param string $end_date End date (YYYY-MM-DD)
     * @param int $limit Number of results to return
     * @return array Feedback by page
     */
    public function get_feedback_by_page($start_date = '', $end_date = '', $limit = 10) {
        global $wpdb;
        
        $where = array('page_url IS NOT NULL', "page_url != ''");
        $values = array();
        
        // Date range
        if (!empty($start_date)) {
            $where[] = 'DATE(created_at) >= %s';
            $values[] = $start_date;
        }
        
        if (!empty($end_date)) {
            $where[] = 'DATE(created_at) <= %s';
            $values[] = $end_date;
        }
        
        $where_clause = implode(' AND ', $where);
        
        $query = $wpdb->prepare(
            "SELECT 
                page_url,
                page_title,
                COUNT(*) as count,
                AVG(rating) as avg_rating
             FROM {$this->table_feedback}
             WHERE {$where_clause}
             GROUP BY page_url, page_title
             ORDER BY count DESC
             LIMIT %d",
            array_merge($values, array($limit))
        );
        
        return $wpdb->get_results($query);
    }
    
    /**
     * Get recent feedback
     * 
     * @param int $limit Number of feedback items to return
     * @return array Recent feedback
     */
    public function get_recent_feedback($limit = 5) {
        global $wpdb;
        
        $query = $wpdb->prepare(
            "SELECT * FROM {$this->table_feedback}
             ORDER BY created_at DESC
             LIMIT %d",
            $limit
        );
        
        $feedback = $wpdb->get_results($query);
        
        // Get meta data for each feedback
        foreach ($feedback as $item) {
            $item->meta = $this->get_meta($item->id);
        }
        
        return $feedback;
    }
    
    /**
     * Update feedback status
     * 
     * @param int $feedback_id Feedback ID
     * @param string $status New status
     * @return bool True on success, false on failure
     */
    public function update_status($feedback_id, $status) {
        global $wpdb;
        
        $result = $wpdb->update(
            $this->table_feedback,
            array('status' => $status),
            array('id' => $feedback_id),
            array('%s'),
            array('%d')
        );
        
        if ($result !== false) {
            do_action('encompass_feedback_status_changed', $feedback_id, $status);
            return true;
        }
        
        return false;
    }
    
    /**
     * Delete feedback
     * 
     * @param int $feedback_id Feedback ID
     * @return bool True on success, false on failure
     */
    public function delete_feedback($feedback_id) {
        global $wpdb;
        
        // Delete meta first
        $this->delete_meta($feedback_id);
        
        // Delete feedback
        $result = $wpdb->delete(
            $this->table_feedback,
            array('id' => $feedback_id),
            array('%d')
        );
        
        if ($result) {
            do_action('encompass_feedback_deleted', $feedback_id);
            return true;
        }
        
        return false;
    }
    
    /**
     * Add meta data to feedback
     * 
     * @param int $feedback_id Feedback ID
     * @param string $meta_key Meta key
     * @param mixed $meta_value Meta value
     * @return int|false Meta ID on success, false on failure
     */
    public function add_meta($feedback_id, $meta_key, $meta_value) {
        global $wpdb;
        
        $feedback_id = absint($feedback_id);
        
        // Serialize if array or object
        $meta_value = maybe_serialize($meta_value);
        
        $result = $wpdb->insert(
            $this->table_feedback_meta,
            array(
                'feedback_id' => $feedback_id,
                'meta_key' => $meta_key,
                'meta_value' => $meta_value,
            ),
            array('%d', '%s', '%s')
        );
        
        if ($result) {
            $mid = (int) $wpdb->insert_id;
            
            // Clear cache
            wp_cache_delete($feedback_id, 'encompass_feedback_meta');
            
            do_action('added_encompass_feedback_meta', $mid, $feedback_id, $meta_key, $meta_value);
            
            return $mid;
        }
        
        return false;
    }
    
    /**
     * Get feedback meta data
     * 
     * @param int $feedback_id Feedback ID
     * @param string $meta_key Optional. Meta key
     * @param bool $single Optional. Return single value or array. Default false.
     * @return mixed Meta value(s)
     */
    public function get_meta($feedback_id, $meta_key = '', $single = false) {
        global $wpdb;
        
        $feedback_id = absint($feedback_id);
        
        // Try to get from cache first
        $cache_key = $feedback_id . ($meta_key ? '_' . $meta_key : '');
        $cached = wp_cache_get($cache_key, 'encompass_feedback_meta');
        
        if (false !== $cached) {
            if ($single && is_array($cached)) {
                return $cached[0];
            }
            return $cached;
        }
        
        // Build the query
        if (!empty($meta_key)) {
            $meta = $wpdb->get_col(
                $wpdb->prepare(
                    "SELECT meta_value FROM {$this->table_feedback_meta} WHERE feedback_id = %d AND meta_key = %s",
                    $feedback_id,
                    $meta_key
                )
            );
        } else {
            $meta = $wpdb->get_results(
                $wpdb->prepare(
                    "SELECT meta_key, meta_value FROM {$this->table_feedback_meta} WHERE feedback_id = %d",
                    $feedback_id
                ),
                ARRAY_A
            );
            
            // Format as key => value pairs
            $formatted_meta = array();
            foreach ($meta as $row) {
                $key = $row['meta_key'];
                $value = maybe_unserialize($row['meta_value']);
                
                if (isset($formatted_meta[$key])) {
                    if (!is_array($formatted_meta[$key])) {
                        $formatted_meta[$key] = array($formatted_meta[$key]);
                    }
                    $formatted_meta[$key][] = $value;
                } else {
                    $formatted_meta[$key] = $value;
                }
            }
            
            $meta = $formatted_meta;
        }
        
        // Cache the results
        wp_cache_set($cache_key, $meta, 'encompass_feedback_meta');
        
        if ($single && is_array($meta)) {
            return $meta[0];
        }
        
        return $meta;
    }
    
    /**
     * Update feedback meta data
     * 
     * @param int $feedback_id Feedback ID
     * @param string $meta_key Meta key
     * @param mixed $meta_value Meta value
     * @param mixed $prev_value Optional. Previous value to update.
     * @return int|bool Meta ID if new row, true if updated, false on failure
     */
    public function update_meta($feedback_id, $meta_key, $meta_value, $prev_value = '') {
        global $wpdb;
        
        $feedback_id = absint($feedback_id);
        
        // Check if meta exists
        $meta = $this->get_meta($feedback_id, $meta_key, false);
        
        // Serialize if array or object
        $meta_value = maybe_serialize($meta_value);
        
        if (empty($meta)) {
            // Add new meta
            return $this->add_meta($feedback_id, $meta_key, $meta_value);
        } else {
            // Update existing meta
            $where = array(
                'feedback_id' => $feedback_id,
                'meta_key' => $meta_key,
            );
            
            if (!empty($prev_value)) {
                $where['meta_value'] = maybe_serialize($prev_value);
            }
            
            $result = $wpdb->update(
                $this->table_feedback_meta,
                array('meta_value' => $meta_value),
                $where,
                array('%s'),
                array('%d', '%s')
            );
            
            if ($result !== false) {
                // Clear cache
                wp_cache_delete($feedback_id, 'encompass_feedback_meta');
                wp_cache_delete($feedback_id . '_' . $meta_key, 'encompass_feedback_meta');
                
                do_action('updated_encompass_feedback_meta', 0, $feedback_id, $meta_key, $meta_value);
                
                return true;
            }
            
            return false;
        }
    }
    
    /**
     * Delete feedback meta data
     * 
     * @param int $feedback_id Feedback ID
     * @param string $meta_key Optional. Meta key to delete.
     * @param mixed $meta_value Optional. Meta value to delete.
     * @return bool True on success, false on failure
     */
    public function delete_meta($feedback_id, $meta_key = '', $meta_value = '') {
        global $wpdb;
        
        $feedback_id = absint($feedback_id);
        
        $where = array('feedback_id' => $feedback_id);
        $where_format = array('%d');
        
        if (!empty($meta_key)) {
            $where['meta_key'] = $meta_key;
            $where_format[] = '%s';
            
            if ('' !== $meta_value) {
                $where['meta_value'] = maybe_serialize($meta_value);
                $where_format[] = '%s';
            }
        }
        
        $result = $wpdb->delete(
            $this->table_feedback_meta,
            $where,
            $where_format
        );
        
        if ($result) {
            // Clear cache
            wp_cache_delete($feedback_id, 'encompass_feedback_meta');
            
            if (!empty($meta_key)) {
                wp_cache_delete($feedback_id . '_' . $meta_key, 'encompass_feedback_meta');
            }
            
            do_action('deleted_encompass_feedback_meta', 0, $feedback_id, $meta_key, $meta_value);
            
            return true;
        }
        
        return false;
    }
    
    /**
     * Get client IP address
     * 
     * @return string IP address
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
