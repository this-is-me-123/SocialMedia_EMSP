<?php
/**
 * Main admin class for Encompass Feedback
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class Encompass_Feedback_Admin {
    /**
     * @var Encompass_Feedback_API
     */
    private $api;
    
    /**
     * @var Encompass_Feedback_DB
     */
    private $db;
    
    /**
     * @var array Plugin settings
     */
    private $settings;
    
    /**
     * @var Encompass_Feedback_Settings
     */
    private $settings_page;
    
    /**
     * Constructor
     */
    public function __construct() {
        $this->api = new Encompass_Feedback_API();
        $this->db = new Encompass_Feedback_DB();
        $this->settings = $this->get_settings();
        
        $this->init_hooks();
    }
    
    /**
     * Initialize hooks
     */
    private function init_hooks() {
        // Admin menu
        add_action('admin_menu', array($this, 'add_admin_menu'));
        
        // Admin assets
        add_action('admin_enqueue_scripts', array($this, 'enqueue_assets'));
        
        // Admin bar
        add_action('admin_bar_menu', array($this, 'add_admin_bar_menu'), 100);
        
        // Dashboard widget
        add_action('wp_dashboard_setup', array($this, 'add_dashboard_widget'));
        
        // AJAX handlers
        add_action('wp_ajax_encompass_feedback_get_feedback', array($this, 'ajax_get_feedback'));
        add_action('wp_ajax_encompass_feedback_update_status', array($this, 'ajax_update_status'));
        add_action('wp_ajax_encompass_feedback_delete', array($this, 'ajax_delete_feedback'));
        
        // Plugin action links
        add_filter('plugin_action_links_' . ENCOMPASS_FEEDBACK_BASENAME, array($this, 'add_plugin_action_links'));
    }
    
    /**
     * Add admin menu items
     */
    public function add_admin_menu() {
        // Main menu
        $hook = add_menu_page(
            __('Feedback', 'encompass-feedback'),
            __('Feedback', 'encompass-feedback'),
            'manage_options',
            'encompass-feedback',
            array($this, 'render_dashboard_page'),
            'dashicons-feedback',
            30
        );
        
        // Dashboard submenu
        add_submenu_page(
            'encompass-feedback',
            __('Dashboard', 'encompass-feedback'),
            __('Dashboard', 'encompass-feedback'),
            'manage_options',
            'encompass-feedback',
            array($this, 'render_dashboard_page')
        );
        
        // All Feedback
        add_submenu_page(
            'encompass-feedback',
            __('All Feedback', 'encompass-feedback'),
            __('All Feedback', 'encompass-feedback'),
            'manage_options',
            'encompass-feedback-all',
            array($this, 'render_feedback_list_page')
        );
        
        // Settings
        add_submenu_page(
            'encompass-feedback',
            __('Feedback Settings', 'encompass-feedback'),
            __('Settings', 'encompass-feedback'),
            'manage_options',
            'encompass-feedback-settings',
            array($this, 'render_settings_page')
        );
        
        // Hidden detail page
        add_submenu_page(
            null,
            __('Feedback Details', 'encompass-feedback'),
            '',
            'manage_options',
            'encompass-feedback-detail',
            array($this, 'render_feedback_detail_page')
        );
    }
    
    /**
     * Enqueue admin assets
     */
    public function enqueue_assets($hook) {
        if (strpos($hook, 'encompass-feedback') === false && get_current_screen()->id !== 'dashboard') {
            return;
        }
        
        // Styles
        wp_enqueue_style(
            'encompass-feedback-admin',
            ENCOMPASS_FEEDBACK_URL . 'assets/css/admin.css',
            array(),
            ENCOMPASS_FEEDBACK_VERSION
        );
        
        // Scripts
        wp_enqueue_script(
            'encompass-feedback-admin',
            ENCOMPASS_FEEDBACK_URL . 'assets/js/admin.js',
            array('jquery', 'wp-util'),
            ENCOMPASS_FEEDBACK_VERSION,
            true
        );
        
        // Localize script
        wp_localize_script('encompass-feedback-admin', 'encompassFeedback', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('encompass_feedback_admin_nonce'),
            'strings' => array(
                'confirm_delete' => __('Are you sure you want to delete this feedback?', 'encompass-feedback'),
                'error_occurred' => __('An error occurred. Please try again.', 'encompass-feedback'),
            )
        ));
    }
    
    /**
     * Render dashboard page
     */
    public function render_dashboard_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        $recent_feedback = $this->db->get_feedback_list(array(
            'number' => 5,
            'orderby' => 'created_at',
            'order' => 'DESC',
        ));
        
        include ENCOMPASS_FEEDBACK_PATH . 'templates/admin/dashboard.php';
    }
    
    /**
     * Render feedback list page
     */
    public function render_feedback_list_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        $filters = array(
            'type' => isset($_GET['type']) ? sanitize_text_field($_GET['type']) : '',
            'status' => isset($_GET['status']) ? sanitize_text_field($_GET['status']) : '',
            'search' => isset($_GET['s']) ? sanitize_text_field($_GET['s']) : '',
            'paged' => isset($_GET['paged']) ? absint($_GET['paged']) : 1,
            'per_page' => 20,
        );
        
        $feedback_list = $this->db->get_feedback_list($filters);
        $total_items = $this->db->get_feedback_count($filters);
        
        include ENCOMPASS_FEEDBACK_PATH . 'templates/admin/feedback-list.php';
    }
    
    /**
     * Render feedback detail page
     */
    public function render_feedback_detail_page() {
        if (!current_user_can('manage_options')) {
            wp_die(__('You do not have sufficient permissions.', 'encompass-feedback'));
        }
        
        $feedback_id = isset($_GET['feedback_id']) ? absint($_GET['feedback_id']) : 0;
        $feedback = $this->db->get_feedback($feedback_id);
        
        if (!$feedback) {
            wp_die(__('Feedback not found.', 'encompass-feedback'));
        }
        
        include ENCOMPASS_FEEDBACK_PATH . 'templates/admin/feedback-detail.php';
    }
    
    /**
     * Render settings page
     */
    public function render_settings_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        include ENCOMPASS_FEEDBACK_PATH . 'templates/admin/settings.php';
    }
    
    /**
     * Add dashboard widget
     */
    public function add_dashboard_widget() {
        if (!current_user_can('manage_options') || empty($this->settings['display']['dashboard_widget'])) {
            return;
        }
        
        wp_add_dashboard_widget(
            'encompass_feedback_dashboard_widget',
            __('Recent Feedback', 'encompass-feedback'),
            array($this, 'render_dashboard_widget')
        );
    }
    
    /**
     * Render dashboard widget
     */
    public function render_dashboard_widget() {
        $feedback = $this->db->get_feedback_list(array(
            'number' => 5,
            'orderby' => 'created_at',
            'order' => 'DESC',
        ));
        
        include ENCOMPASS_FEEDBACK_PATH . 'templates/admin/dashboard-widget.php';
    }
    
    /**
     * Add admin bar menu
     */
    public function add_admin_bar_menu($wp_admin_bar) {
        if (!current_user_can('manage_options') || is_admin() || empty($this->settings['display']['show_in_admin_bar'])) {
            return;
        }
        
        $count = $this->db->get_feedback_count(array('status' => 'new'));
        $count_html = $count > 0 ? ' <span class="pending-count">' . number_format_i18n($count) . '</span>' : '';
        
        $wp_admin_bar->add_node(array(
            'id' => 'encompass-feedback',
            'title' => '<span class="ab-icon dashicons dashicons-feedback"></span><span class="ab-label">' . __('Feedback', 'encompass-feedback') . $count_html . '</span>',
            'href' => admin_url('admin.php?page=encompass-feedback'),
        ));
    }
    
    /**
     * Add plugin action links
     */
    public function add_plugin_action_links($links) {
        $action_links = array(
            'settings' => sprintf(
                '<a href="%s">%s</a>',
                admin_url('admin.php?page=encompass-feedback-settings'),
                __('Settings', 'encompass-feedback')
            ),
        );
        
        return array_merge($action_links, $links);
    }
    
    /**
     * AJAX: Get feedback details
     */
    public function ajax_get_feedback() {
        check_ajax_referer('encompass_feedback_admin_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('Permission denied.', 'encompass-feedback')), 403);
        }
        
        $feedback_id = isset($_POST['feedback_id']) ? absint($_POST['feedback_id']) : 0;
        $feedback = $this->db->get_feedback($feedback_id);
        
        if (!$feedback) {
            wp_send_json_error(array('message' => __('Feedback not found.', 'encompass-feedback')), 404);
        }
        
        wp_send_json_success($this->api->prepare_feedback_for_response($feedback));
    }
    
    /**
     * AJAX: Update feedback status
     */
    public function ajax_update_status() {
        check_ajax_referer('encompass_feedback_admin_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('Permission denied.', 'encompass-feedback')), 403);
        }
        
        $feedback_id = isset($_POST['feedback_id']) ? absint($_POST['feedback_id']) : 0;
        $status = isset($_POST['status']) ? sanitize_text_field($_POST['status']) : '';
        
        if (!$feedback_id || !$status) {
            wp_send_json_error(array('message' => __('Invalid data.', 'encompass-feedback')), 400);
        }
        
        $result = $this->db->update_feedback($feedback_id, array('status' => $status));
        
        if ($result === false) {
            wp_send_json_error(array('message' => __('Update failed.', 'encompass-feedback')), 500);
        }
        
        $feedback = $this->db->get_feedback($feedback_id);
        wp_send_json_success($this->api->prepare_feedback_for_response($feedback));
    }
    
    /**
     * AJAX: Delete feedback
     */
    public function ajax_delete_feedback() {
        check_ajax_referer('encompass_feedback_admin_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('Permission denied.', 'encompass-feedback')), 403);
        }
        
        $feedback_id = isset($_POST['feedback_id']) ? absint($_POST['feedback_id']) : 0;
        
        if (!$feedback_id) {
            wp_send_json_error(array('message' => __('Invalid feedback ID.', 'encompass-feedback')), 400);
        }
        
        $result = $this->db->delete_feedback($feedback_id);
        
        if (!$result) {
            wp_send_json_error(array('message' => __('Deletion failed.', 'encompass-feedback')), 500);
        }
        
        wp_send_json_success();
    }
    
    /**
     * Get plugin settings
     */
    private function get_settings() {
        $defaults = array(
            'general' => array(
                'feedback_types' => array(
                    'general' => __('General', 'encompass-feedback'),
                    'bug' => __('Bug Report', 'encompass-feedback'),
                    'suggestion' => __('Suggestion', 'encompass-feedback'),
                ),
                'statuses' => array(
                    'new' => __('New', 'encompass-feedback'),
                    'in_progress' => __('In Progress', 'encompass-feedback'),
                    'resolved' => __('Resolved', 'encompass-feedback'),
                ),
            ),
            'display' => array(
                'show_in_admin_bar' => 1,
                'dashboard_widget' => 1,
            ),
        );
        
        return wp_parse_args(get_option('encompass_feedback_settings', array()), $defaults);
    }
}
