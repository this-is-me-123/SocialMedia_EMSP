<?php
/**
 * Feedback Widget for the Encompass Feedback System
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class Encompass_Feedback_Widget {
    private $feedback_types = array(
        'general' => 'General Feedback',
        'bug' => 'Report a Bug',
        'suggestion' => 'Suggestion',
        'praise' => 'Praise',
    );
    
    public function __construct() {
        // Add widget to frontend
        add_action('wp_footer', array($this, 'render_widget'));
        
        // Handle AJAX submission
        add_action('wp_ajax_submit_feedback', array($this, 'handle_feedback_submission'));
        add_action('wp_ajax_nopriv_submit_feedback', array($this, 'handle_feedback_submission'));
    }
    
    /**
     * Render the feedback widget
     */
    public function render_widget() {
        // Don't show on admin pages
        if (is_admin()) {
            return;
        }
        
        // Get current user info
        $current_user = wp_get_current_user();
        $user_name = $current_user->exists() ? $current_user->display_name : '';
        $user_email = $current_user->exists() ? $current_user->user_email : '';
        
        // Get current page info
        $page_title = wp_title('', false);
        $page_url = home_url(add_query_arg(array(), $GLOBALS['wp']->request));
        
        // Output the widget HTML
        ?>
        <div id="encompass-feedback-widget" class="encompass-feedback-widget">
            <button id="encompass-feedback-trigger" class="encompass-feedback-trigger" aria-label="<?php esc_attr_e('Give Feedback', 'encompass-feedback'); ?>">
                <span class="dashicons dashicons-feedback"></span>
                <span class="encompass-feedback-trigger-text"><?php _e('Feedback', 'encompass-feedback'); ?></span>
            </button>
            
            <div id="encompass-feedback-modal" class="encompass-feedback-modal" style="display: none;">
                <div class="encompass-feedback-modal-content">
                    <div class="encompass-feedback-modal-header">
                        <h3><?php _e('Send Us Your Feedback', 'encompass-feedback'); ?></h3>
                        <button type="button" class="encompass-feedback-close" aria-label="<?php esc_attr_e('Close', 'encompass-feedback'); ?>">
                            &times;
                        </button>
                    </div>
                    
                    <form id="encompass-feedback-form" class="encompass-feedback-form">
                        <?php wp_nonce_field('encompass_feedback_nonce', 'feedback_nonce'); ?>
                        
                        <input type="hidden" name="action" value="submit_feedback">
                        <input type="hidden" name="page_title" value="<?php echo esc_attr($page_title); ?>">
                        <input type="hidden" name="page_url" value="<?php echo esc_url($page_url); ?>">
                        
                        <div class="encompass-feedback-form-group">
                            <label for="feedback-type"><?php _e('Type of Feedback', 'encompass-feedback'); ?></label>
                            <select id="feedback-type" name="feedback_type" class="encompass-feedback-select" required>
                                <option value=""><?php _e('-- Select --', 'encompass-feedback'); ?></option>
                                <?php foreach ($this->feedback_types as $key => $label) : ?>
                                    <option value="<?php echo esc_attr($key); ?>"><?php echo esc_html($label); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                        
                        <div class="encompass-feedback-form-group rating-container">
                            <label><?php _e('How would you rate your experience?', 'encompass-feedback'); ?></label>
                            <div class="encompass-feedback-rating">
                                <?php for ($i = 1; $i <= 5; $i++) : ?>
                                    <input type="radio" id="rating-<?php echo $i; ?>" name="rating" value="<?php echo $i; ?>" class="encompass-feedback-rating-input">
                                    <label for="rating-<?php echo $i; ?>" class="encompass-feedback-rating-label" title="<?php echo $i; ?> stars">
                                        <span class="dashicons dashicons-star-empty"></span>
                                    </label>
                                <?php endfor; ?>
                            </div>
                        </div>
                        
                        <div class="encompass-feedback-form-group">
                            <label for="feedback-comment"><?php _e('Your Feedback', 'encompass-feedback'); ?> <span class="required">*</span></label>
                            <textarea id="feedback-comment" name="comment" rows="4" class="encompass-feedback-textarea" required></textarea>
                        </div>
                        
                        <div class="encompass-feedback-form-group">
                            <label for="feedback-name"><?php _e('Your Name', 'encompass-feedback'); ?></label>
                            <input type="text" id="feedback-name" name="name" value="<?php echo esc_attr($user_name); ?>" class="encompass-feedback-input">
                        </div>
                        
                        <div class="encompass-feedback-form-group">
                            <label for="feedback-email"><?php _e('Email Address', 'encompass-feedback'); ?> <span class="required">*</span></label>
                            <input type="email" id="feedback-email" name="email" value="<?php echo esc_attr($user_email); ?>" required class="encompass-feedback-input">
                        </div>
                        
                        <div class="encompass-feedback-form-group encompass-feedback-consent">
                            <label class="encompass-feedback-checkbox-label">
                                <input type="checkbox" name="consent" value="1" required>
                                <?php 
                                    printf(
                                        /* translators: %s: Privacy policy page link */
                                        __('I consent to having this website store my submitted information so they can respond to my inquiry. %s', 'encompass-feedback'),
                                        sprintf(
                                            '<a href="%s" target="_blank">%s</a>',
                                            esc_url(get_privacy_policy_url()),
                                            __('View Privacy Policy', 'encompass-feedback')
                                        )
                                    );
                                ?>
                            </label>
                        </div>
                        
                        <div class="encompass-feedback-form-actions">
                            <button type="submit" class="encompass-feedback-submit">
                                <span class="dashicons dashicons-email"></span>
                                <?php _e('Send Feedback', 'encompass-feedback'); ?>
                            </button>
                        </div>
                    </form>
                    
                    <div id="encompass-feedback-thankyou" class="encompass-feedback-thankyou" style="display: none;">
                        <div class="encompass-feedback-thankyou-icon">
                            <span class="dashicons dashicons-yes-alt"></span>
                        </div>
                        <h3><?php _e('Thank You!', 'encompass-feedback'); ?></h3>
                        <p><?php _e('We appreciate your feedback. Our team will review it shortly.', 'encompass-feedback'); ?></p>
                        <button type="button" class="encompass-feedback-close encompass-feedback-close-btn">
                            <?php _e('Close', 'encompass-feedback'); ?>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <?php
    }
    
    /**
     * Handle feedback form submission via AJAX
     */
    public function handle_feedback_submission() {
        // Verify nonce
        if (!isset($_POST['feedback_nonce']) || !wp_verify_nonce($_POST['feedback_nonce'], 'encompass_feedback_nonce')) {
            wp_send_json_error(array('message' => __('Security check failed. Please try again.', 'encompass-feedback')), 403);
        }
        
        // Validate required fields
        $required_fields = array(
            'feedback_type' => __('Feedback Type', 'encompass-feedback'),
            'comment' => __('Feedback', 'encompass-feedback'),
            'email' => __('Email Address', 'encompass-feedback'),
        );
        
        $errors = array();
        $data = array();
        
        foreach ($required_fields as $field => $label) {
            if (empty($_POST[$field])) {
                $errors[] = sprintf(__('%s is a required field.', 'encompass-feedback'), $label);
            } else {
                $data[$field] = sanitize_text_field(wp_unslash($_POST[$field]));
            }
        }
        
        // Validate email
        if (!empty($data['email']) && !is_email($data['email'])) {
            $errors[] = __('Please enter a valid email address.', 'encompass-feedback');
        }
        
        // If there are validation errors, return them
        if (!empty($errors)) {
            wp_send_json_error(array('message' => implode('<br>', $errors)), 400);
        }
        
        // Get additional data
        $data['rating'] = isset($_POST['rating']) ? absint($_POST['rating']) : 0;
        $data['name'] = !empty($_POST['name']) ? sanitize_text_field(wp_unslash($_POST['name'])) : '';
        $data['page_title'] = !empty($_POST['page_title']) ? sanitize_text_field(wp_unslash($_POST['page_title'])) : '';
        $data['page_url'] = !empty($_POST['page_url']) ? esc_url_raw(wp_unslash($_POST['page_url'])) : '';
        
        // Get user ID if logged in
        $user_id = get_current_user_id();
        
        // Prepare feedback data
        $feedback_data = array(
            'user_id' => $user_id ?: null,
            'feedback_type' => $data['feedback_type'],
            'rating' => $data['rating'],
            'comment' => $data['comment'],
            'page_url' => $data['page_url'],
            'page_title' => $data['page_title'],
            'status' => 'new',
        );
        
        // Add meta data
        $meta_data = array(
            'name' => $data['name'],
            'email' => $data['email'],
            'user_ip' => $this->get_client_ip(),
            'user_agent' => isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : '',
        );
        
        // Get the database handler
        global $encompass_feedback_db;
        
        if (empty($encompass_feedback_db)) {
            $encompass_feedback_db = new Encompass_Feedback_DB();
        }
        
        // Save feedback
        $feedback_id = $encompass_feedback_db->add_feedback($feedback_data);
        
        if (!$feedback_id) {
            wp_send_json_error(array('message' => __('Failed to save feedback. Please try again.', 'encompass-feedback')), 500);
        }
        
        // Save meta data
        foreach ($meta_data as $meta_key => $meta_value) {
            $encompass_feedback_db->add_meta($feedback_id, $meta_key, $meta_value);
        }
        
        // Send email notification
        $this->send_notification_email($feedback_id, $feedback_data, $meta_data);
        
        // Trigger action for other plugins
        do_action('encompass_feedback_submitted', $feedback_id, $feedback_data, $meta_data);
        
        // Return success response
        wp_send_json_success(array(
            'message' => __('Thank you for your feedback!', 'encompass-feedback'),
            'feedback_id' => $feedback_id,
        ));
    }
    
    /**
     * Send email notification about new feedback
     * 
     * @param int $feedback_id Feedback ID
     * @param array $feedback_data Feedback data
     * @param array $meta_data Meta data
     * @return bool True if email was sent, false otherwise
     */
    private function send_notification_email($feedback_id, $feedback_data, $meta_data) {
        // Get admin email
        $to = get_option('admin_email');
        
        // Get site name
        $site_name = get_bloginfo('name');
        
        // Build email subject
        $subject = sprintf(
            /* translators: %1$s: Site name, %2$s: Feedback type */
            __('[%1$s] New %2$s Feedback Received', 'encompass-feedback'),
            $site_name,
            ucfirst($feedback_data['feedback_type'])
        );
        
        // Build email message
        $message = '<!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title>' . esc_html($subject) . '</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
                <h1 style="color: #0073aa; margin-top: 0;">' . __('New Feedback Received', 'encompass-feedback') . '</h1>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; width: 30%;">' . __('Feedback ID', 'encompass-feedback') . '</td>
                        <td style="padding: 8px; border: 1px solid #ddd; width: 70%;">#' . $feedback_id . '</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">' . __('Type', 'encompass-feedback') . '</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">' . esc_html(ucfirst($feedback_data['feedback_type'])) . '</td>
                    </tr>';
        
        if (!empty($feedback_data['rating'])) {
            $message .= '
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">' . __('Rating', 'encompass-feedback') . '</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">' . $this->get_star_rating($feedback_data['rating']) . '</td>
                    </tr>';
        }
        
        $message .= '
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">' . __('From', 'encompass-feedback') . '</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">';
        
        if (!empty($meta_data['name'])) {
            $message .= esc_html($meta_data['name']);
            if (!empty($meta_data['email'])) {
                $message .= ' &lt;' . esc_html($meta_data['email']) . '&gt;';
            }
        } elseif (!empty($meta_data['email'])) {
            $message .= esc_html($meta_data['email']);
        } else {
            $message .= __('Anonymous', 'encompass-feedback');
        }
        
        $message .= '
                        </td>
                    </tr>';
        
        if (!empty($feedback_data['page_title']) || !empty($feedback_data['page_url'])) {
            $message .= '
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">' . __('Page', 'encompass-feedback') . '</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">';
            
            if (!empty($feedback_data['page_title'])) {
                $message .= esc_html($feedback_data['page_title']) . '<br>';
            }
            
            if (!empty($feedback_data['page_url'])) {
                $message .= '<a href="' . esc_url($feedback_data['page_url']) . '" style="color: #0073aa; text-decoration: none;">' . esc_html($feedback_data['page_url']) . '</a>';
            }
            
            $message .= '
                        </td>
                    </tr>';
        }
        
        $message .= '
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; vertical-align: top;">' . __('Comment', 'encompass-feedback') . '</td>
                        <td style="padding: 8px; border: 1px solid #ddd; white-space: pre-line;">' . wp_kses_post(wpautop($feedback_data['comment'])) . '</td>
                    </tr>
                </table>
                
                <div style="margin-top: 20px; text-align: center;">
                    <a href="' . esc_url(admin_url('admin.php?page=encompass-feedback&feedback_id=' . $feedback_id)) . '" style="display: inline-block; padding: 10px 20px; background-color: #0073aa; color: #fff; text-decoration: none; border-radius: 4px; font-weight: bold;">' . __('View Feedback', 'encompass-feedback') . '</a>
                </div>
            </div>
            
            <div style="margin-top: 20px; font-size: 12px; color: #777; text-align: center;">
                ' . sprintf(
                    /* translators: %s: Site name */
                    __('This email was sent from %s', 'encompass-feedback'),
                    '<a href="' . esc_url(home_url()) . '" style="color: #0073aa; text-decoration: none;">' . esc_html($site_name) . '</a>'
                ) . '
            </div>
        </body>
        </html>';
        
        // Set email headers
        $headers = array(
            'Content-Type: text/html; charset=UTF-8',
            'From: ' . $site_name . ' <' . $to . '>',
            'Reply-To: ' . (!empty($meta_data['name']) ? $meta_data['name'] . ' <' . $meta_data['email'] . '>' : $meta_data['email']),
        );
        
        // Send email
        return wp_mail($to, $subject, $message, $headers);
    }
    
    /**
     * Get star rating HTML
     * 
     * @param int $rating Rating (1-5)
     * @return string HTML for star rating
     */
    private function get_star_rating($rating) {
        $output = '';
        $full_stars = floor($rating);
        $has_half_star = ($rating - $full_stars) >= 0.5;
        
        // Full stars
        for ($i = 0; $i < $full_stars; $i++) {
            $output .= '★';
        }
        
        // Half star
        if ($has_half_star) {
            $output .= '½';
        }
        
        // Empty stars
        $empty_stars = 5 - $full_stars - ($has_half_star ? 1 : 0);
        for ($i = 0; $i < $empty_stars; $i++) {
            $output .= '☆';
        }
        
        return $output . ' (' . $rating . '/5)';
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
