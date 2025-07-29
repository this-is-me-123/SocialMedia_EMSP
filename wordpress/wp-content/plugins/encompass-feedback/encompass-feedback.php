<?php
/**
 * Plugin Name: Encompass Feedback System
 * Description: A comprehensive feedback collection and analysis system for Encompass MSP
 * Version: 1.0.0
 * Author: Encompass MSP
 * Text Domain: encompass-feedback
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('ENCOMPASS_FEEDBACK_VERSION', '1.0.0');
define('ENCOMPASS_FEEDBACK_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('ENCOMPASS_FEEDBACK_PLUGIN_URL', plugin_dir_url(__FILE__));

// Include required files
require_once ENCOMPASS_FEEDBACK_PLUGIN_DIR . 'includes/class-encompass-feedback-db.php';
require_once ENCOMPASS_FEEDBACK_PLUGIN_DIR . 'includes/class-encompass-feedback-widget.php';
require_once ENCOMPASS_FEEDBACK_PLUGIN_DIR . 'includes/class-encompass-feedback-api.php';

class Encompass_Feedback_System {
    private static $instance = null;
    private $db;
    private $widget;
    private $api;

    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        // Initialize database
        $this->db = new Encompass_Feedback_DB();
        
        // Initialize widget
        $this->widget = new Encompass_Feedback_Widget();
        
        // Initialize API
        $this->api = new Encompass_Feedback_API();
        
        // Register activation and deactivation hooks
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
        
        // Initialize admin menu
        add_action('admin_menu', array($this, 'add_admin_menu'));
        
        // Enqueue scripts and styles
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_scripts'));
    }

    public function activate() {
        // Create database tables
        $this->db->create_tables();
        
        // Set up default options
        update_option('encompass_feedback_version', ENCOMPASS_FEEDBACK_VERSION);
        
        // Schedule cron jobs
        if (!wp_next_scheduled('encompass_feedback_daily_tasks')) {
            wp_schedule_event(time(), 'daily', 'encompass_feedback_daily_tasks');
        }
    }

    public function deactivate() {
        // Clear scheduled tasks
        wp_clear_scheduled_hook('encompass_feedback_daily_tasks');
    }

    public function add_admin_menu() {
        add_menu_page(
            'Feedback Dashboard',
            'Feedback',
            'manage_options',
            'encompass-feedback',
            array($this, 'render_dashboard'),
            'dashicons-feedback',
            30
        );
        
        add_submenu_page(
            'encompass-feedback',
            'Feedback Settings',
            'Settings',
            'manage_options',
            'encompass-feedback-settings',
            array($this, 'render_settings_page')
        );
        
        add_submenu_page(
            'encompass-feedback',
            'Feedback Reports',
            'Reports',
            'manage_options',
            'encompass-feedback-reports',
            array($this, 'render_reports_page')
        );
    }

    public function enqueue_scripts() {
        // Only load on frontend
        if (is_admin()) {
            return;
        }
        
        // Enqueue feedback widget styles
        wp_enqueue_style(
            'encompass-feedback-widget',
            ENCOMPASS_FEEDBACK_PLUGIN_URL . 'assets/css/feedback-widget.css',
            array(),
            ENCOMPASS_FEEDBACK_VERSION
        );
        
        // Enqueue feedback widget script
        wp_enqueue_script(
            'encompass-feedback-widget',
            ENCOMPASS_FEEDBACK_PLUGIN_URL . 'assets/js/feedback-widget.js',
            array('jquery'),
            ENCOMPASS_FEEDBACK_VERSION,
            true
        );
        
        // Localize script with AJAX URL and nonce
        wp_localize_script(
            'encompass-feedback-widget',
            'encompassFeedback',
            array(
                'ajaxurl' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('encompass_feedback_nonce'),
                'currentPage' => get_the_ID(),
                'currentUrl' => home_url(add_query_arg(array(), $GLOBALS['wp']->request)),
            )
        );
    }

    public function enqueue_admin_scripts($hook) {
        // Only load on our plugin pages
        if (strpos($hook, 'encompass-feedback') === false) {
            return;
        }
        
        // Enqueue admin styles
        wp_enqueue_style(
            'encompass-feedback-admin',
            ENCOMPASS_FEEDBACK_PLUGIN_URL . 'assets/css/admin.css',
            array(),
            ENCOMPASS_FEEDBACK_VERSION
        );
        
        // Enqueue Chart.js for reports
        wp_enqueue_script(
            'chart-js',
            'https://cdn.jsdelivr.net/npm/chart.js',
            array(),
            '3.7.0',
            true
        );
        
        // Enqueue admin script
        wp_enqueue_script(
            'encompass-feedback-admin',
            ENCOMPASS_FEEDBACK_PLUGIN_URL . 'assets/js/admin.js',
            array('jquery', 'chart-js'),
            ENCOMPASS_FEEDBACK_VERSION,
            true
        );
        
        // Localize script with data for charts
        wp_localize_script(
            'encompass-feedback-admin',
            'encompassFeedbackAdmin',
            array(
                'ajaxurl' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('encompass_feedback_admin_nonce'),
                'feedbackData' => $this->get_chart_data(),
            )
        );
    }

    private function get_chart_data() {
        // Get feedback data for the last 30 days
        $start_date = date('Y-m-d', strtotime('-30 days'));
        $end_date = date('Y-m-d');
        
        $feedback_data = $this->db->get_feedback_summary($start_date, $end_date);
        
        // Format data for Chart.js
        $labels = array();
        $ratings = array();
        $counts = array(
            'positive' => array(),
            'neutral' => array(),
            'negative' => array()
        );
        
        foreach ($feedback_data as $data) {
            $labels[] = date('M j', strtotime($data->date));
            $ratings[] = $data->avg_rating;
            $counts['positive'][] = $data->positive_count;
            $counts['neutral'][] = $data->neutral_count;
            $counts['negative'][] = $data->negative_count;
        }
        
        return array(
            'labels' => $labels,
            'ratings' => $ratings,
            'counts' => $counts
        );
    }

    public function render_dashboard() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        // Get summary data
        $summary = $this->db->get_feedback_summary();
        $recent_feedback = $this->db->get_recent_feedback(5);
        
        include ENCOMPASS_FEEDBACK_PLUGIN_DIR . 'templates/dashboard.php';
    }
    
    public function render_settings_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        // Save settings if form was submitted
        if (isset($_POST['submit'])) {
            check_admin_referer('encompass_feedback_settings');
            
            $settings = array(
                'enable_nps' => isset($_POST['enable_nps']) ? 1 : 0,
                'nps_frequency' => sanitize_text_field($_POST['nps_frequency']),
                'feedback_email' => sanitize_email($_POST['feedback_email']),
                'enable_dashboard_widget' => isset($_POST['enable_dashboard_widget']) ? 1 : 0,
            );
            
            update_option('encompass_feedback_settings', $settings);
            
            echo '<div class="notice notice-success"><p>Settings saved successfully!</p></div>';
        }
        
        // Get current settings
        $settings = get_option('encompass_feedback_settings', array(
            'enable_nps' => 1,
            'nps_frequency' => '90',
            'feedback_email' => get_bloginfo('admin_email'),
            'enable_dashboard_widget' => 1,
        ));
        
        include ENCOMPASS_FEEDBACK_PLUGIN_DIR . 'templates/settings.php';
    }
    
    public function render_reports_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        // Get date range from request or use default (last 30 days)
        $start_date = isset($_GET['start_date']) ? sanitize_text_field($_GET['start_date']) : date('Y-m-d', strtotime('-30 days'));
        $end_date = isset($_GET['end_date']) ? sanitize_text_field($_GET['end_date']) : date('Y-m-d');
        
        // Get feedback data for the selected date range
        $feedback_data = $this->db->get_feedback_summary($start_date, $end_date);
        $feedback_by_type = $this->db->get_feedback_by_type($start_date, $end_date);
        $feedback_by_page = $this->db->get_feedback_by_page($start_date, $end_date, 10);
        
        include ENCOMPASS_FEEDBACK_PLUGIN_DIR . 'templates/reports.php';
    }
}

// Initialize the plugin
function encompass_feedback_init() {
    Encompass_Feedback_System::get_instance();
}
add_action('plugins_loaded', 'encompass_feedback_init');
