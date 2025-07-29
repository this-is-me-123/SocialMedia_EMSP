<?php
/**
 * Settings handler for Encompass Feedback
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class Encompass_Feedback_Settings {
    /**
     * @var array Plugin settings
     */
    private $settings;
    
    /**
     * Constructor
     */
    public function __construct() {
        $this->settings = $this->get_settings();
        $this->init_hooks();
    }
    
    /**
     * Initialize hooks
     */
    private function init_hooks() {
        // Register settings
        add_action('admin_init', array($this, 'register_settings'));
        
        // Add settings sections and fields
        add_action('admin_init', array($this, 'add_settings_sections'));
        add_action('admin_init', array($this, 'add_settings_fields'));
    }
    
    /**
     * Register settings
     */
    public function register_settings() {
        register_setting(
            'encompass_feedback_settings',
            'encompass_feedback_settings',
            array($this, 'sanitize_settings')
        );
    }
    
    /**
     * Add settings sections
     */
    public function add_settings_sections() {
        // General section
        add_settings_section(
            'encompass_feedback_general',
            __('General Settings', 'encompass-feedback'),
            array($this, 'render_section_general'),
            'encompass-feedback-settings'
        );
        
        // Email section
        add_settings_section(
            'encompass_feedback_email',
            __('Email Notifications', 'encompass-feedback'),
            array($this, 'render_section_email'),
            'encompass-feedback-settings'
        );
        
        // Display section
        add_settings_section(
            'encompass_feedback_display',
            __('Display Settings', 'encompass-feedback'),
            array($this, 'render_section_display'),
            'encompass-feedback-settings'
        );
    }
    
    /**
     * Add settings fields
     */
    public function add_settings_fields() {
        // General fields
        add_settings_field(
            'feedback_types',
            __('Feedback Types', 'encompass-feedback'),
            array($this, 'render_field_feedback_types'),
            'encompass-feedback-settings',
            'encompass_feedback_general'
        );
        
        add_settings_field(
            'statuses',
            __('Statuses', 'encompass-feedback'),
            array($this, 'render_field_statuses'),
            'encompass-feedback-settings',
            'encompass_feedback_general'
        );
        
        // Email fields
        add_settings_field(
            'notification_email',
            __('Notification Email', 'encompass-feedback'),
            array($this, 'render_field_notification_email'),
            'encompass-feedback-settings',
            'encompass_feedback_email'
        );
        
        add_settings_field(
            'email_subject',
            __('Email Subject', 'encompass-feedback'),
            array($this, 'render_field_email_subject'),
            'encompass-feedback-settings',
            'encompass_feedback_email'
        );
        
        add_settings_field(
            'email_template',
            __('Email Template', 'encompass-feedback'),
            array($this, 'render_field_email_template'),
            'encompass-feedback-settings',
            'encompass_feedback_email'
        );
        
        // Display fields
        add_settings_field(
            'show_in_admin_bar',
            __('Show in Admin Bar', 'encompass-feedback'),
            array($this, 'render_field_show_in_admin_bar'),
            'encompass-feedback-settings',
            'encompass_feedback_display'
        );
        
        add_settings_field(
            'dashboard_widget',
            __('Dashboard Widget', 'encompass-feedback'),
            array($this, 'render_field_dashboard_widget'),
            'encompass-feedback-settings',
            'encompass_feedback_display'
        );
    }
    
    /**
     * Sanitize settings
     */
    public function sanitize_settings($input) {
        $output = array();
        
        // Sanitize general settings
        if (isset($input['general'])) {
            $output['general'] = array();
            
            // Sanitize feedback types
            if (isset($input['general']['feedback_types']) && is_array($input['general']['feedback_types'])) {
                $output['general']['feedback_types'] = array();
                
                foreach ($input['general']['feedback_types'] as $type => $label) {
                    $type = sanitize_key($type);
                    $output['general']['feedback_types'][$type] = sanitize_text_field($label);
                }
            }
            
            // Sanitize statuses
            if (isset($input['general']['statuses']) && is_array($input['general']['statuses'])) {
                $output['general']['statuses'] = array();
                
                foreach ($input['general']['statuses'] as $status => $label) {
                    $status = sanitize_key($status);
                    $output['general']['statuses'][$status] = sanitize_text_field($label);
                }
            }
        }
        
        // Sanitize email settings
        if (isset($input['email'])) {
            $output['email'] = array();
            
            // Sanitize notification email
            if (isset($input['email']['notification_email'])) {
                $emails = array_map('trim', explode(',', $input['email']['notification_email']));
                $valid_emails = array();
                
                foreach ($emails as $email) {
                    if (is_email($email)) {
                        $valid_emails[] = sanitize_email($email);
                    }
                }
                
                $output['email']['notification_email'] = implode(', ', $valid_emails);
            }
            
            // Sanitize email subject
            if (isset($input['email']['subject'])) {
                $output['email']['subject'] = sanitize_text_field($input['email']['subject']);
            }
            
            // Sanitize email template
            if (isset($input['email']['template'])) {
                $output['email']['template'] = wp_kses_post($input['email']['template']);
            }
        }
        
        // Sanitize display settings
        if (isset($input['display'])) {
            $output['display'] = array(
                'show_in_admin_bar' => !empty($input['display']['show_in_admin_bar']) ? 1 : 0,
                'dashboard_widget' => !empty($input['display']['dashboard_widget']) ? 1 : 0,
            );
        }
        
        return $output;
    }
    
    /**
     * Get plugin settings with defaults
     */
    public function get_settings() {
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
            'email' => array(
                'notification_email' => get_option('admin_email'),
                'subject' => __('New Feedback: #{id}', 'encompass-feedback'),
                'template' => $this->get_default_email_template(),
            ),
            'display' => array(
                'show_in_admin_bar' => 1,
                'dashboard_widget' => 1,
            ),
        );
        
        return wp_parse_args(get_option('encompass_feedback_settings', array()), $defaults);
    }
    
    /**
     * Get default email template
     */
    private function get_default_email_template() {
        return "<p>" . __('A new feedback has been submitted:', 'encompass-feedback') . "</p>\n" .
            "<p>\n" .
            "<strong>" . __('Type', 'encompass-feedback') . ":</strong> {feedback_type}<br>\n" .
            "<strong>" . __('Page', 'encompass-feedback') . ":</strong> {page_title}<br>\n" .
            "<strong>" . __('User', 'encompass-feedback') . ":</strong> {user_name} ({user_email})<br>\n" .
            "<strong>" . __('Date', 'encompass-feedback') . ":</strong> {date}<br>\n" .
            "</p>\n" .
            "<p><strong>" . __('Feedback', 'encompass-feedback') . ":</strong></p>\n" .
            "<blockquote>{comment}</blockquote>\n" .
            "<p>" . __('View in admin:', 'encompass-feedback') . " <a href=\"{admin_url}\">{admin_url}</a></p>";
    }
    
    /**
     * Section callbacks
     */
    public function render_section_general() {
        echo '<p>' . __('Configure general feedback settings.', 'encompass-feedback') . '</p>';
    }
    
    public function render_section_email() {
        echo '<p>' . __('Configure email notifications for new feedback.', 'encompass-feedback') . '</p>';
    }
    
    public function render_section_display() {
        echo '<p>' . __('Configure display settings.', 'encompass-feedback') . '</p>';
    }
    
    /**
     * Field callbacks
     */
    public function render_field_feedback_types() {
        $types = $this->settings['general']['feedback_types'];
        ?>
        <div id="encompass-feedback-types">
            <?php foreach ($types as $type => $label) : ?>
                <div class="feedback-type">
                    <input type="text" 
                           name="encompass_feedback_settings[general][feedback_types][<?php echo esc_attr($type); ?>]" 
                           value="<?php echo esc_attr($label); ?>" 
                           class="regular-text" />
                    <button type="button" class="button button-secondary remove-feedback-type">
                        <?php _e('Remove', 'encompass-feedback'); ?>
                    </button>
                </div>
            <?php endforeach; ?>
        </div>
        <button type="button" id="add-feedback-type" class="button button-secondary">
            <?php _e('Add Type', 'encompass-feedback'); ?>
        </button>
        <script type="text/template" id="tmpl-feedback-type">
            <div class="feedback-type">
                <input type="text" 
                       name="encompass_feedback_settings[general][feedback_types][{{data.type}}]" 
                       value="" 
                       class="regular-text" 
                       placeholder="<?php esc_attr_e('Type name', 'encompass-feedback'); ?>" />
                <button type="button" class="button button-secondary remove-feedback-type">
                    <?php _e('Remove', 'encompass-feedback'); ?>
                </button>
            </div>
        </script>
        <?php
    }
    
    public function render_field_statuses() {
        $statuses = $this->settings['general']['statuses'];
        ?>
        <div id="encompass-feedback-statuses">
            <?php foreach ($statuses as $status => $label) : ?>
                <div class="feedback-status">
                    <input type="text" 
                           name="encompass_feedback_settings[general][statuses][<?php echo esc_attr($status); ?>]" 
                           value="<?php echo esc_attr($label); ?>" 
                           class="regular-text" />
                    <button type="button" class="button button-secondary remove-feedback-status">
                        <?php _e('Remove', 'encompass-feedback'); ?>
                    </button>
                </div>
            <?php endforeach; ?>
        </div>
        <button type="button" id="add-feedback-status" class="button button-secondary">
            <?php _e('Add Status', 'encompass-feedback'); ?>
        </button>
        <script type="text/template" id="tmpl-feedback-status">
            <div class="feedback-status">
                <input type="text" 
                       name="encompass_feedback_settings[general][statuses][{{data.status}}]" 
                       value="" 
                       class="regular-text" 
                       placeholder="<?php esc_attr_e('Status name', 'encompass-feedback'); ?>" />
                <button type="button" class="button button-secondary remove-feedback-status">
                    <?php _e('Remove', 'encompass-feedback'); ?>
                </button>
            </div>
        </script>
        <?php
    }
    
    public function render_field_notification_email() {
        ?>
        <input type="text" 
               name="encompass_feedback_settings[email][notification_email]" 
               value="<?php echo esc_attr($this->settings['email']['notification_email']); ?>" 
               class="regular-text" />
        <p class="description">
            <?php _e('Comma-separated list of email addresses to notify.', 'encompass-feedback'); ?>
        </p>
        <?php
    }
    
    public function render_field_email_subject() {
        ?>
        <input type="text" 
               name="encompass_feedback_settings[email][subject]" 
               value="<?php echo esc_attr($this->settings['email']['subject']); ?>" 
               class="large-text" />
        <p class="description">
            <?php _e('Available placeholders: {id}, {feedback_type}, {page_title}', 'encompass-feedback'); ?>
        </p>
        <?php
    }
    
    public function render_field_email_template() {
        wp_editor(
            $this->settings['email']['template'],
            'encompass_feedback_email_template',
            array(
                'textarea_name' => 'encompass_feedback_settings[email][template]',
                'textarea_rows' => 10,
                'media_buttons' => false,
                'teeny' => true,
            )
        );
        ?>
        <p class="description">
            <?php _e('Available placeholders:', 'encompass-feedback'); ?>
            {id}, {feedback_type}, {page_title}, {page_url}, {user_name}, {user_email}, {user_ip}, {date}, {comment}, {admin_url}
        </p>
        <?php
    }
    
    public function render_field_show_in_admin_bar() {
        ?>
        <label>
            <input type="checkbox" 
                   name="encompass_feedback_settings[display][show_in_admin_bar]" 
                   value="1" 
                   <?php checked($this->settings['display']['show_in_admin_bar'], 1); ?> />
            <?php _e('Show feedback counter in the admin bar', 'encompass-feedback'); ?>
        </label>
        <?php
    }
    
    public function render_field_dashboard_widget() {
        ?>
        <label>
            <input type="checkbox" 
                   name="encompass_feedback_settings[display][dashboard_widget]" 
                   value="1" 
                   <?php checked($this->settings['display']['dashboard_widget'], 1); ?> />
            <?php _e('Show recent feedback in the dashboard', 'encompass-feedback'); ?>
        </label>
        <?php
    }
}
