<?php
/**
 * The admin-specific functionality of the plugin.
 */
class Encompass_MSP_Analytics_Admin {
    private $plugin_name;
    private $version;
    private $api;

    public function __construct(string $plugin_name, string $version) {
        $this->plugin_name = $plugin_name;
        $this->version = $version;
        $this->api = new Encompass_MSP_REST_API();
        
        // Add admin menu items
        add_action('admin_menu', array($this, 'add_plugin_admin_menu'));
        
        // Register settings
        add_action('admin_init', array($this, 'register_settings'));
        
        // Add settings link to plugins page
        add_filter('plugin_action_links_' . plugin_basename(ENCOMPASS_ANALYTICS_PLUGIN_DIR . 'encompass-analytics.php'), 
                  array($this, 'add_action_links'));
    }

    public function enqueue_styles(string $hook): void {
        // Only load on our plugin pages
        if (strpos($hook, 'encompass-analytics') === false) {
            return;
        }
        
        // Enqueue the main admin styles
        wp_enqueue_style(
            $this->plugin_name . '-admin',
            ENCOMPASS_ANALYTICS_PLUGIN_URL . 'admin/css/encompass-analytics-admin.css',
            array(),
            $this->version,
            'all'
        );
        
        // Enqueue datepicker styles
        wp_enqueue_style(
            $this->plugin_name . '-datepicker',
            'https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.css',
            array(),
            '3.1.0',
            'all'
        );
        
        // Enqueue Chart.js
        wp_enqueue_style(
            $this->plugin_name . '-chartjs',
            'https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.css',
            array(),
            '3.7.0',
            'all'
        );
    }

    public function enqueue_scripts(string $hook): void {
        // Only load on our plugin pages
        if (strpos($hook, 'encompass-analytics') === false) {
            return;
        }
        
        // Enqueue the main admin script
        wp_enqueue_script(
            $this->plugin_name . '-admin',
            ENCOMPASS_ANALYTICS_PLUGIN_URL . 'admin/js/encompass-analytics-admin.js',
            array('jquery', 'moment', 'jquery-ui-datepicker'),
            $this->version,
            true
        );
        
        // Enqueue datepicker
        wp_enqueue_script(
            $this->plugin_name . '-datepicker',
            'https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.min.js',
            array('jquery', 'moment'),
            '3.1.0',
            true
        );
        
        // Enqueue Chart.js
        wp_enqueue_script(
            $this->plugin_name . '-chartjs',
            'https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js',
            array(),
            '3.7.0',
            true
        );
        
        // Localize script with data
        wp_localize_script(
            $this->plugin_name . '-admin',
            'encompassAnalytics',
            array(
                'ajax_url' => admin_url('admin-ajax.php'),
                'rest_url' => esc_url_raw(rest_url('encompass/v1/')),
                'nonce' => wp_create_nonce('wp_rest'),
                'api_key' => get_option('encompass_msp_api_key'),
                'i18n' => array(
                    'today' => __('Today', 'encompass-analytics'),
                    'yesterday' => __('Yesterday', 'encompass-analytics'),
                    'last7days' => __('Last 7 Days', 'encompass-analytics'),
                    'last30days' => __('Last 30 Days', 'encompass-analytics'),
                    'thismonth' => __('This Month', 'encompass-analytics'),
                    'lastmonth' => __('Last Month', 'encompass-analytics'),
                    'custom' => __('Custom Range', 'encompass-analytics'),
                    'apply' => __('Apply', 'encompass-analytics'),
                    'cancel' => __('Cancel', 'encompass-analytics'),
                    'from' => __('From', 'encompass-analytics'),
                    'to' => __('To', 'encompass-analytics'),
                    'january' => __('January', 'encompass-analytics'),
                    'february' => __('February', 'encompass-analytics'),
                    'march' => __('March', 'encompass-analytics'),
                    'april' => __('April', 'encompass-analytics'),
                    'may' => __('May', 'encompass-analytics'),
                    'june' => __('June', 'encompass-analytics'),
                    'july' => __('July', 'encompass-analytics'),
                    'august' => __('August', 'encompass-analytics'),
                    'september' => __('September', 'encompass-analytics'),
                    'october' => __('October', 'encompass-analytics'),
                    'november' => __('November', 'encompass-analytics'),
                    'december' => __('December', 'encompass-analytics'),
                    'su' => __('Su', 'encompass-analytics'),
                    'mo' => __('Mo', 'encompass-analytics'),
                    'tu' => __('Tu', 'encompass-analytics'),
                    'we' => __('We', 'encompass-analytics'),
                    'th' => __('Th', 'encompass-analytics'),
                    'fr' => __('Fr', 'encompass-analytics'),
                    'sa' => __('Sa', 'encompass-analytics'),
                )
            )
        );
    }

    public function add_plugin_admin_menu(): void {
        // Main menu item
        add_menu_page(
            __('Encompass Analytics', 'encompass-analytics'),
            __('Analytics', 'encompass-analytics'),
            'manage_options',
            'encompass-analytics',
            array($this, 'display_plugin_dashboard_page'),
            'dashicons-chart-bar',
            30
        );
        
        // Dashboard submenu
        add_submenu_page(
            'encompass-analytics',
            __('Dashboard', 'encompass-analytics'),
            __('Dashboard', 'encompass-analytics'),
            'manage_options',
            'encompass-analytics',
            array($this, 'display_plugin_dashboard_page')
        );
        
        // Reports submenu
        add_submenu_page(
            'encompass-analytics',
            __('Reports', 'encompass-analytics'),
            __('Reports', 'encompass-analytics'),
            'manage_options',
            'encompass-analytics-reports',
            array($this, 'display_plugin_reports_page')
        );
        
        // Settings submenu
        add_submenu_page(
            'encompass-analytics',
            __('Settings', 'encompass-analytics'),
            __('Settings', 'encompass-analytics'),
            'manage_options',
            'encompass-analytics-settings',
            array($this, 'display_plugin_settings_page')
        );
    }

    public function display_plugin_dashboard_page(): void {
        include_once 'partials/encompass-analytics-admin-dashboard.php';
    }
    
    public function display_plugin_reports_page(): void {
        include_once 'partials/encompass-analytics-admin-reports.php';
    }
    
    public function display_plugin_settings_page(): void {
        include_once 'partials/encompass-analytics-admin-settings.php';
    }

    public function register_settings(): void {
        // Register settings
        register_setting('encompass_analytics_general', 'encompass_msp_tracking_enabled');
        register_setting('encompass_analytics_general', 'encompass_msp_track_admin_users');
        register_setting('encompass_analytics_general', 'encompass_msp_anonymize_ip');
        register_setting('encompass_analytics_general', 'encompass_msp_api_key', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => ''
        ));
        
        // Event tracking settings
        register_setting('encompass_analytics_events', 'encompass_msp_track_outbound_links');
        register_setting('encompass_analytics_events', 'encompass_msp_track_downloads');
        register_setting('encompass_analytics_events', 'encompass_msp_track_forms');
        register_setting('encompass_analytics_events', 'encompass_msp_track_videos');
        register_setting('encompass_analytics_events', 'encompass_msp_track_clicks');
        register_setting('encompass_analytics_events', 'encompass_msp_track_scroll');
        register_setting('encompass_analytics_events', 'encompass_msp_track_time_on_page');
        
        // Custom tracking code
        register_setting('encompass_analytics_advanced', 'encompass_msp_custom_tracking_code', array(
            'type' => 'string',
            'sanitize_callback' => array($this, 'sanitize_custom_code'),
            'default' => ''
        ));
        
        // Add settings sections
        add_settings_section(
            'encompass_analytics_general_section',
            __('General Settings', 'encompass-analytics'),
            array($this, 'general_section_callback'),
            'encompass_analytics_general'
        );
        
        add_settings_section(
            'encompass_analytics_events_section',
            __('Event Tracking', 'encompass-analytics'),
            array($this, 'events_section_callback'),
            'encompass_analytics_events'
        );
        
        add_settings_section(
            'encompass_analytics_advanced_section',
            __('Advanced Settings', 'encompass-analytics'),
            array($this, 'advanced_section_callback'),
            'encompass_analytics_advanced'
        );
        
        // Add settings fields
        add_settings_field(
            'encompass_msp_tracking_enabled',
            __('Enable Tracking', 'encompass-analytics'),
            array($this, 'checkbox_field_callback'),
            'encompass_analytics_general',
            'encompass_analytics_general_section',
            array(
                'id' => 'encompass_msp_tracking_enabled',
                'description' => __('Enable or disable all tracking', 'encompass-analytics')
            )
        );
        
        add_settings_field(
            'encompass_msp_track_admin_users',
            __('Track Admin Users', 'encompass-analytics'),
            array($this, 'checkbox_field_callback'),
            'encompass_analytics_general',
            'encompass_analytics_general_section',
            array(
                'id' => 'encompass_msp_track_admin_users',
                'description' => __('Track activity of admin users', 'encompass-analytics')
            )
        );
        
        add_settings_field(
            'encompass_msp_anonymize_ip',
            __('Anonymize IP Addresses', 'encompass-analytics'),
            array($this, 'checkbox_field_callback'),
            'encompass_analytics_general',
            'encompass_analytics_general_section',
            array(
                'id' => 'encompass_msp_anonymize_ip',
                'description' => __('Anonymize the last octet of IP addresses', 'encompass-analytics')
            )
        );
        
        add_settings_field(
            'encompass_msp_api_key',
            __('API Key', 'encompass-analytics'),
            array($this, 'text_field_callback'),
            'encompass_analytics_general',
            'encompass_analytics_general_section',
            array(
                'id' => 'encompass_msp_api_key',
                'description' => __('API key for REST API authentication', 'encompass-analytics'),
                'readonly' => true,
                'class' => 'regular-text code'
            )
        );
        
        // Event tracking fields
        $event_fields = array(
            'track_outbound_links' => __('Track Outbound Links', 'encompass-analytics'),
            'track_downloads' => __('Track File Downloads', 'encompass-analytics'),
            'track_forms' => __('Track Form Submissions', 'encompass-analytics'),
            'track_videos' => __('Track Video Engagement', 'encompass-analytics'),
            'track_clicks' => __('Track All Clicks', 'encompass-analytics'),
            'track_scroll' => __('Track Page Scrolling', 'encompass-analytics'),
            'track_time_on_page' => __('Track Time on Page', 'encompass-analytics')
        );
        
        foreach ($event_fields as $field => $label) {
            add_settings_field(
                'encompass_msp_' . $field,
                $label,
                array($this, 'checkbox_field_callback'),
                'encompass_analytics_events',
                'encompass_analytics_events_section',
                array(
                    'id' => 'encompass_msp_' . $field,
                    'description' => sprintf(__('Enable %s tracking', 'encompass-analytics'), strtolower($label))
                )
            );
        }
        
        // Advanced settings fields
        add_settings_field(
            'encompass_msp_custom_tracking_code',
            __('Custom Tracking Code', 'encompass-analytics'),
            array($this, 'textarea_field_callback'),
            'encompass_analytics_advanced',
            'encompass_analytics_advanced_section',
            array(
                'id' => 'encompass_msp_custom_tracking_code',
                'description' => __('Add custom JavaScript tracking code that will be added to every page', 'encompass-analytics'),
                'rows' => 10,
                'cols' => 50
            )
        );
    }
    
    // Section callbacks
    public function general_section_callback(): void {
        echo '<p>' . __('Configure general settings for Encompass Analytics.', 'encompass-analytics') . '</p>';
    }
    
    public function events_section_callback(): void {
        echo '<p>' . __('Configure which events to track on your website.', 'encompass-analytics') . '</p>';
    }
    
    public function advanced_section_callback(): void {
        echo '<p>' . __('Advanced configuration options for Encompass Analytics.', 'encompass-analytics') . '</p>';
    }
    
    // Field callbacks
    public function checkbox_field_callback(array $args): void {
        $option = get_option($args['id']);
        $checked = checked(1, $option, false);
        
        echo '<label for="' . esc_attr($args['id']) . '">';
        echo '<input type="checkbox" id="' . esc_attr($args['id']) . '" name="' . esc_attr($args['id']) . '" value="1" ' . $checked . ' />';
        echo ' <span class="description">' . esc_html($args['description']) . '</span>';
        echo '</label>';
    }
    
    public function text_field_callback(array $args): void {
        $value = get_option($args['id'], '');
        $class = isset($args['class']) ? $args['class'] : 'regular-text';
        $readonly = isset($args['readonly']) && $args['readonly'] ? 'readonly' : '';
        
        echo '<input type="text" id="' . esc_attr($args['id']) . '" name="' . esc_attr($args['id']) . '" value="' . esc_attr($value) . '" class="' . esc_attr($class) . '" ' . $readonly . ' />';
        
        if (isset($args['description'])) {
            echo '<p class="description">' . esc_html($args['description']) . '</p>';
        }
    }
    
    public function textarea_field_callback(array $args): void {
        $value = get_option($args['id'], '');
        $rows = isset($args['rows']) ? $args['rows'] : 5;
        $cols = isset($args['cols']) ? $args['cols'] : 40;
        
        echo '<textarea id="' . esc_attr($args['id']) . '" name="' . esc_attr($args['id']) . '" rows="' . esc_attr($rows) . '" cols="' . esc_attr($cols) . '" class="large-text code">' . esc_textarea($value) . '</textarea>';
        
        if (isset($args['description'])) {
            echo '<p class="description">' . esc_html($args['description']) . '</p>';
        }
    }
    
    // Sanitization callbacks
    public function sanitize_custom_code(string $input): string {
        // Allow script tags and other common HTML in custom tracking code
        $allowed_html = array(
            'script' => array(
                'type' => array(),
                'src' => array(),
                'async' => array(),
                'defer' => array(),
            ),
            'noscript' => array(),
            'img' => array(
                'src' => array(),
                'alt' => array(),
                'height' => array(),
                'width' => array(),
                'style' => array(),
            ),
            'style' => array(
                'type' => array(),
            ),
            'link' => array(
                'rel' => array(),
                'href' => array(),
                'type' => array(),
            ),
            'meta' => array(
                'name' => array(),
                'content' => array(),
                'property' => array(),
            ),
        );
        
        return wp_kses($input, $allowed_html);
    }
    
    // Add settings link to plugins page
    public function add_action_links(array $links): array {
        $settings_link = array(
            '<a href="' . admin_url('admin.php?page=encompass-analytics-settings') . '">' . __('Settings', 'encompass-analytics') . '</a>',
        );
        return array_merge($settings_link, $links);
    }
    
    // Helper to generate API key
    public function generate_api_key(): void {
        if (!current_user_can('manage_options')) {
            wp_die(__('You do not have sufficient permissions to access this page.'));
        }
        
        $new_key = wp_generate_password(32, false, false);
        update_option('encompass_msp_api_key', $new_key);
        
        wp_send_json_success(array(
            'api_key' => $new_key
        ));
    }
}
