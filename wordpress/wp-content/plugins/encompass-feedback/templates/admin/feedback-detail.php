<?php
/**
 * Feedback Detail template for Encompass Feedback
 *
 * @package Encompass_Feedback
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

// Get feedback ID from URL
$feedback_id = isset($_GET['feedback_id']) ? absint($_GET['feedback_id']) : 0;

// Get feedback data
$feedback = $this->db->get_feedback($feedback_id);

// Check if feedback exists
if (!$feedback) {
    wp_die(__('Feedback not found.', 'encompass-feedback'));
}

// Get user data
$user = $feedback->user_id ? get_user_by('id', $feedback->user_id) : null;
$user_display = $user ? $user->display_name : __('Guest', 'encompass-feedback');
$user_email = $user ? $user->user_email : '';
$user_roles = $user ? $user->roles : array();
$user_registered = $user ? $user->user_registered : '';
$user_profile_url = $user ? get_edit_user_link($user->ID) : '';

// Get available statuses and types
$statuses = $this->db->get_available_statuses();
$types = $this->db->get_available_types();

// Get feedback meta
$meta = $this->db->get_feedback_meta($feedback_id);

// Get feedback history
$history = $this->db->get_feedback_history($feedback_id);

// Get related feedback (same user, same page, etc.)
$related_feedback = $this->db->get_related_feedback($feedback_id, array(
    'user_id' => $feedback->user_id,
    'page_url' => $feedback->page_url,
    'limit' => 5
));

// Format dates
$created_date = date_i18n(get_option('date_format') . ' ' . get_option('time_format'), strtotime($feedback->created_at));
$updated_date = date_i18n(get_option('date_format') . ' ' . get_option('time_format'), strtotime($feedback->updated_at));

// Get next and previous feedback
$nav_feedback = $this->db->get_adjacent_feedback($feedback_id, array(
    'status' => isset($_GET['status']) ? sanitize_text_field($_GET['status']) : '',
    'type' => isset($_GET['type']) ? sanitize_text_field($_GET['type']) : '',
));
?>

<div class="wrap encompass-feedback-detail">
    <!-- Header with navigation -->
    <div class="encompass-feedback-header">
        <h1>
            <?php _e('Feedback #', 'encompass-feedback'); ?><?php echo esc_html($feedback->id); ?>
            
            <span class="feedback-status status-<?php echo esc_attr($feedback->status); ?>">
                <?php echo esc_html(ucfirst(isset($statuses[$feedback->status]) ? $statuses[$feedback->status] : $feedback->status)); ?>
            </span>
            
            <?php if (!empty($feedback->priority)) : ?>
                <span class="feedback-priority priority-<?php echo esc_attr($feedback->priority); ?>">
                    <?php echo esc_html(ucfirst($feedback->priority)); ?>
                </span>
            <?php endif; ?>
        </h1>
        
        <div class="feedback-navigation">
            <?php if (!empty($nav_feedback['prev'])) : ?>
                <a href="<?php echo esc_url(admin_url('admin.php?page=encompass-feedback-detail&feedback_id=' . $nav_feedback['prev']->id)); ?>" 
                   class="button" 
                   title="<?php echo esc_attr(sprintf(__('Previous: #%d', 'encompass-feedback'), $nav_feedback['prev']->id)); ?>">
                    &larr; <?php _e('Previous', 'encompass-feedback'); ?>
                </a>
            <?php endif; ?>
            
            <a href="<?php echo esc_url(admin_url('admin.php?page=encompass-feedback-all')); ?>" class="button">
                <?php _e('Back to All Feedback', 'encompass-feedback'); ?>
            </a>
            
            <?php if (!empty($nav_feedback['next'])) : ?>
                <a href="<?php echo esc_url(admin_url('admin.php?page=encompass-feedback-detail&feedback_id=' . $nav_feedback['next']->id)); ?>" 
                   class="button" 
                   title="<?php echo esc_attr(sprintf(__('Next: #%d', 'encompass-feedback'), $nav_feedback['next']->id)); ?>">
                    <?php _e('Next', 'encompass-feedback'); ?> &rarr;
                </a>
            <?php endif; ?>
        </div>
    </div>
    
    <div class="encompass-feedback-content">
        <!-- Main content area -->
        <div class="encompass-feedback-main">
            <!-- Feedback details -->
            <div class="encompass-feedback-card">
                <div class="encompass-feedback-card-header">
                    <h2><?php _e('Feedback Details', 'encompass-feedback'); ?></h2>
                    
                    <div class="feedback-actions">
                        <a href="#" class="button edit-feedback" data-id="<?php echo esc_attr($feedback->id); ?>">
                            <?php _e('Edit', 'encompass-feedback'); ?>
                        </a>
                        
                        <div class="feedback-status-selector">
                            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                                <input type="hidden" name="action" value="encompass_feedback_update_status">
                                <input type="hidden" name="feedback_id" value="<?php echo esc_attr($feedback->id); ?>">
                                <?php wp_nonce_field('encompass_feedback_update_status_' . $feedback->id); ?>
                                
                                <select name="status" class="status-select" data-feedback-id="<?php echo esc_attr($feedback->id); ?>">
                                    <?php foreach ($statuses as $status => $label) : ?>
                                        <option value="<?php echo esc_attr($status); ?>" <?php selected($feedback->status, $status); ?>>
                                            <?php echo esc_html(ucfirst($label)); ?>
                                        </option>
                                    <?php endforeach; ?>
                                </select>
                                
                                <button type="submit" class="button button-primary">
                                    <?php _e('Update', 'encompass-feedback'); ?>
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
                
                <div class="encompass-feedback-card-body">
                    <div class="feedback-meta">
                        <div class="feedback-meta-item">
                            <span class="feedback-meta-label"><?php _e('Type', 'encompass-feedback'); ?>:</span>
                            <span class="feedback-meta-value">
                                <?php 
                                $type_label = isset($types[$feedback->feedback_type]) ? 
                                    $types[$feedback->feedback_type] : 
                                    $feedback->feedback_type;
                                echo esc_html($type_label);
                                ?>
                            </span>
                        </div>
                        
                        <div class="feedback-meta-item">
                            <span class="feedback-meta-label"><?php _e('Submitted', 'encompass-feedback'); ?>:</span>
                            <span class="feedback-meta-value" title="<?php echo esc_attr($created_date); ?>">
                                <?php echo esc_html(human_time_diff(strtotime($feedback->created_at), current_time('timestamp'))) . ' ' . __('ago', 'encompass-feedback'); ?>
                            </span>
                        </div>
                        
                        <div class="feedback-meta-item">
                            <span class="feedback-meta-label"><?php _e('Last Updated', 'encompass-feedback'); ?>:</span>
                            <span class="feedback-meta-value" title="<?php echo esc_attr($updated_date); ?>">
                                <?php echo esc_html(human_time_diff(strtotime($feedback->updated_at), current_time('timestamp'))) . ' ' . __('ago', 'encompass-feedback'); ?>
                            </span>
                        </div>
                        
                        <?php if (!empty($feedback->assigned_to)) : 
                            $assigned_user = get_user_by('id', $feedback->assigned_to);
                            if ($assigned_user) : ?>
                                <div class="feedback-meta-item">
                                    <span class="feedback-meta-label"><?php _e('Assigned To', 'encompass-feedback'); ?>:</span>
                                    <span class="feedback-meta-value">
                                        <a href="<?php echo esc_url(get_edit_user_link($assigned_user->ID)); ?>">
                                            <?php echo esc_html($assigned_user->display_name); ?>
                                        </a>
                                    </span>
                                </div>
                            <?php endif;
                        endif; ?>
                    </div>
                    
                    <div class="feedback-content">
                        <h3><?php _e('Feedback', 'encompass-feedback'); ?></h3>
                        <div class="feedback-text">
                            <?php if (!empty($feedback->comment)) : ?>
                                <?php echo wpautop(esc_html($feedback->comment)); ?>
                            <?php elseif (!empty($feedback->rating)) : ?>
                                <div class="feedback-rating">
                                    <?php 
                                    for ($i = 1; $i <= 5; $i++) {
                                        echo $i <= $feedback->rating ? '★' : '☆';
                                    }
                                    ?>
                                    <span class="rating-value"><?php echo esc_html($feedback->rating); ?>/5</span>
                                </div>
                            <?php else : ?>
                                <p><?php _e('No comment provided.', 'encompass-feedback'); ?></p>
                            <?php endif; ?>
                        </div>
                        
                        <?php if (!empty($feedback->page_title)) : ?>
                            <div class="feedback-page">
                                <h4><?php _e('Page', 'encompass-feedback'); ?>:</h4>
                                <p>
                                    <a href="<?php echo esc_url($feedback->page_url); ?>" target="_blank">
                                        <?php echo esc_html($feedback->page_title); ?>
                                    </a>
                                    <br>
                                    <small><?php echo esc_url($feedback->page_url); ?></small>
                                </p>
                            </div>
                        <?php endif; ?>
                        
                        <?php if (!empty($feedback->user_agent)) : ?>
                            <div class="feedback-user-agent">
                                <h4><?php _e('User Agent', 'encompass-feedback'); ?>:</h4>
                                <p><?php echo esc_html($feedback->user_agent); ?></p>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
            
            <!-- Activity log -->
            <div class="encompass-feedback-card">
                <div class="encompass-feedback-card-header">
                    <h2><?php _e('Activity Log', 'encompass-feedback'); ?></h2>
                </div>
                
                <div class="encompass-feedback-card-body">
                    <?php if (!empty($history)) : ?>
                        <ul class="activity-log">
                            <?php foreach ($history as $item) : 
                                $user = get_user_by('id', $item->user_id);
                                $user_display = $user ? $user->display_name : __('System', 'encompass-feedback');
                                $date = date_i18n(get_option('date_format') . ' ' . get_option('time_format'), strtotime($item->created_at));
                                ?>
                                <li class="activity-log-item">
                                    <div class="activity-log-content">
                                        <div class="activity-log-message">
                                            <?php echo wp_kses_post($item->message); ?>
                                        </div>
                                        <div class="activity-log-meta">
                                            <span class="activity-log-user"><?php echo esc_html($user_display); ?></span>
                                            <span class="activity-log-date" title="<?php echo esc_attr($date); ?>">
                                                <?php echo esc_html(human_time_diff(strtotime($item->created_at), current_time('timestamp'))) . ' ' . __('ago', 'encompass-feedback'); ?>
                                            </span>
                                        </div>
                                    </div>
                                </li>
                            <?php endforeach; ?>
                        </ul>
                    <?php else : ?>
                        <p><?php _e('No activity yet.', 'encompass-feedback'); ?></p>
                    <?php endif; ?>
                    
                    <!-- Add note form -->
                    <div class="add-note">
                        <h3><?php _e('Add Note', 'encompass-feedback'); ?></h3>
                        <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" class="add-note-form">
                            <input type="hidden" name="action" value="encompass_feedback_add_note">
                            <input type="hidden" name="feedback_id" value="<?php echo esc_attr($feedback->id); ?>">
                            <?php wp_nonce_field('encompass_feedback_add_note_' . $feedback->id); ?>
                            
                            <p>
                                <textarea name="note" rows="3" class="large-text" placeholder="<?php esc_attr_e('Add a note about this feedback...', 'encompass-feedback'); ?>"></textarea>
                            </p>
                            
                            <p>
                                <label>
                                    <input type="checkbox" name="notify_user" value="1">
                                    <?php _e('Notify user via email', 'encompass-feedback'); ?>
                                </label>
                            </p>
                            
                            <p>
                                <button type="submit" class="button button-primary">
                                    <?php _e('Add Note', 'encompass-feedback'); ?>
                                </button>
                            </p>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Sidebar -->
        <div class="encompass-feedback-sidebar">
            <!-- User information -->
            <div class="encompass-feedback-card">
                <div class="encompass-feedback-card-header">
                    <h2><?php _e('User Information', 'encompass-feedback'); ?></h2>
                </div>
                
                <div class="encompass-feedback-card-body">
                    <div class="user-avatar">
                        <?php echo get_avatar($user ? $user->ID : $feedback->user_email, 80); ?>
                    </div>
                    
                    <h3>
                        <?php if ($user && $user_profile_url) : ?>
                            <a href="<?php echo esc_url($user_profile_url); ?>">
                                <?php echo esc_html($user_display); ?>
                            </a>
                        <?php else : ?>
                            <?php echo esc_html($user_display); ?>
                        <?php endif; ?>
                        
                        <?php if (!empty($user_roles)) : ?>
                            <span class="user-role">
                                <?php echo esc_html(ucfirst(implode(', ', $user_roles))); ?>
                            </span>
                        <?php endif; ?>
                    </h3>
                    
                    <?php if ($user_email) : ?>
                        <p class="user-email">
                            <a href="mailto:<?php echo esc_attr($user_email); ?>">
                                <?php echo esc_html($user_email); ?>
                            </a>
                        </p>
                    <?php endif; ?>
                    
                    <?php if ($user_registered) : ?>
                        <p class="user-registered">
                            <?php 
                            printf(
                                __('Member since %s', 'encompass-feedback'),
                                date_i18n(get_option('date_format'), strtotime($user_registered))
                            );
                            ?>
                        </p>
                    <?php endif; ?>
                    
                    <?php if ($feedback->user_ip) : ?>
                        <p class="user-ip">
                            <?php _e('IP Address:', 'encompass-feedback'); ?> 
                            <a href="https://whatismyipaddress.com/ip/<?php echo esc_attr($feedback->user_ip); ?>" target="_blank">
                                <?php echo esc_html($feedback->user_ip); ?>
                            </a>
                        </p>
                    <?php endif; ?>
                    
                    <div class="user-actions">
                        <?php if ($user) : ?>
                            <a href="<?php echo esc_url(get_edit_user_link($user->ID)); ?>" class="button">
                                <?php _e('View Profile', 'encompass-feedback'); ?>
                            </a>
                        <?php endif; ?>
                        
                        <?php if ($user_email) : ?>
                            <a href="mailto:<?php echo esc_attr($user_email); ?>" class="button">
                                <?php _e('Send Email', 'encompass-feedback'); ?>
                            </a>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
            
            <!-- Related feedback -->
            <?php if (!empty($related_feedback)) : ?>
                <div class="encompass-feedback-card">
                    <div class="encompass-feedback-card-header">
                        <h2><?php _e('Related Feedback', 'encompass-feedback'); ?></h2>
                    </div>
                    
                    <div class="encompass-feedback-card-body">
                        <ul class="related-feedback-list">
                            <?php foreach ($related_feedback as $related) : 
                                if ($related->id == $feedback->id) continue; // Skip current feedback
                                
                                $related_comment = !empty($related->comment) ? 
                                    wp_trim_words($related->comment, 10) : 
                                    sprintf(__('Rating: %d/5', 'encompass-feedback'), $related->rating);
                                ?>
                                <li class="related-feedback-item">
                                    <a href="<?php echo esc_url(admin_url('admin.php?page=encompass-feedback-detail&feedback_id=' . $related->id)); ?>">
                                        <span class="related-feedback-type">
                                            <?php 
                                            $type_label = isset($types[$related->feedback_type]) ? 
                                                $types[$related->feedback_type] : 
                                                $related->feedback_type;
                                            echo esc_html($type_label);
                                            ?>
                                        </span>
                                        <span class="related-feedback-comment">
                                            <?php echo esc_html($related_comment); ?>
                                        </span>
                                        <span class="related-feedback-date">
                                            <?php echo esc_html(human_time_diff(strtotime($related->created_at), current_time('timestamp'))) . ' ' . __('ago', 'encompass-feedback'); ?>
                                        </span>
                                    </a>
                                </li>
                            <?php endforeach; ?>
                        </ul>
                    </div>
                </div>
            <?php endif; ?>
            
            <!-- System information -->
            <div class="encompass-feedback-card">
                <div class="encompass-feedback-card-header">
                    <h2><?php _e('System Information', 'encompass-feedback'); ?></h2>
                </div>
                
                <div class="encompass-feedback-card-body">
                    <div class="system-info-item">
                        <span class="system-info-label"><?php _e('Feedback ID', 'encompass-feedback'); ?>:</span>
                        <span class="system-info-value">#<?php echo esc_html($feedback->id); ?></span>
                    </div>
                    
                    <div class="system-info-item">
                        <span class="system-info-label"><?php _e('Created', 'encompass-feedback'); ?>:</span>
                        <span class="system-info-value" title="<?php echo esc_attr($created_date); ?>">
                            <?php echo esc_html($created_date); ?>
                        </span>
                    </div>
                    
                    <div class="system-info-item">
                        <span class="system-info-label"><?php _e('Last Updated', 'encompass-feedback'); ?>:</span>
                        <span class="system-info-value" title="<?php echo esc_attr($updated_date); ?>">
                            <?php echo esc_html($updated_date); ?>
                        </span>
                    </div>
                    
                    <?php if (!empty($meta)) : ?>
                        <div class="system-info-meta">
                            <h4><?php _e('Additional Metadata', 'encompass-feedback'); ?>:</h4>
                            <dl>
                                <?php foreach ($meta as $key => $value) : ?>
                                    <dt><?php echo esc_html(ucwords(str_replace('_', ' ', $key))); ?>:</dt>
                                    <dd>
                                        <?php 
                                        if (is_array($value) || is_object($value)) {
                                            echo '<pre>' . esc_html(print_r($value, true)) . '</pre>';
                                        } else {
                                            echo esc_html($value);
                                        }
                                        ?>
                                    </dd>
                                <?php endforeach; ?>
                            </dl>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Edit Feedback Modal -->
<div id="edit-feedback-modal" class="encompass-feedback-modal" style="display: none;">
    <div class="encompass-feedback-modal-content">
        <div class="encompass-feedback-modal-header">
            <h2><?php _e('Edit Feedback', 'encompass-feedback'); ?></h2>
            <button type="button" class="encompass-feedback-modal-close">
                <span class="screen-reader-text"><?php _e('Close', 'encompass-feedback'); ?></span>
                <span class="dashicons dashicons-no-alt"></span>
            </button>
        </div>
        <div class="encompass-feedback-modal-body">
            <div id="edit-feedback-form">
                <!-- Form will be loaded via AJAX -->
                <p class="spinner is-active"></p>
            </div>
        </div>
        <div class="encompass-feedback-modal-footer">
            <button type="button" class="button button-secondary encompass-feedback-modal-cancel">
                <?php _e('Cancel', 'encompass-feedback'); ?>
            </button>
            <button type="button" class="button button-primary encompass-feedback-modal-update">
                <?php _e('Update', 'encompass-feedback'); ?>
            </button>
        </div>
    </div>
</div>
