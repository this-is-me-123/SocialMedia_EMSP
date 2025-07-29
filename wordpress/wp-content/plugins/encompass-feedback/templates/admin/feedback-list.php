<?php
/**
 * Feedback List template for Encompass Feedback
 *
 * @package Encompass_Feedback
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

// Get current filters
$current_status = isset($_GET['status']) ? sanitize_text_field($_GET['status']) : '';
$current_type = isset($_GET['type']) ? sanitize_text_field($_GET['type']) : '';
$current_search = isset($_GET['s']) ? sanitize_text_field($_GET['s']) : '';
$current_page = isset($_GET['paged']) ? absint($_GET['paged']) : 1;

// Prepare query args
$args = array(
    'status' => $current_status,
    'type' => $current_type,
    'search' => $current_search,
    'paged' => $current_page,
    'per_page' => 20,
);

// Get feedback list
$feedback_list = $this->db->get_feedback_list($args);
$total_items = $this->db->get_feedback_count($args);

// Get available statuses and types for filters
$statuses = $this->db->get_available_statuses();
$types = $this->db->get_available_types();

// Calculate pagination
$per_page = 20;
$total_pages = ceil($total_items / $per_page);

// Base URL for pagination
$base_url = admin_url('admin.php?page=encompass-feedback-all');
?>

<div class="wrap">
    <h1 class="wp-heading-inline"><?php _e('All Feedback', 'encompass-feedback'); ?></h1>
    
    <a href="<?php echo esc_url(admin_url('admin.php?page=encompass-feedback')); ?>" class="page-title-action">
        <?php _e('Back to Dashboard', 'encompass-feedback'); ?>
    </a>
    
    <hr class="wp-header-end">
    
    <!-- Filters -->
    <div class="encompass-feedback-filters">
        <form method="get" action="<?php echo esc_url(admin_url('admin.php')); ?>">
            <input type="hidden" name="page" value="encompass-feedback-all">
            
            <div class="tablenav top">
                <div class="alignleft actions">
                    <!-- Status filter -->
                    <label for="filter-by-status" class="screen-reader-text">
                        <?php _e('Filter by status', 'encompass-feedback'); ?>
                    </label>
                    <select name="status" id="filter-by-status">
                        <option value=""><?php _e('All Statuses', 'encompass-feedback'); ?></option>
                        <?php foreach ($statuses as $status => $label) : ?>
                            <option value="<?php echo esc_attr($status); ?>" <?php selected($current_status, $status); ?>>
                                <?php echo esc_html(ucfirst($label)); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    
                    <!-- Type filter -->
                    <label for="filter-by-type" class="screen-reader-text">
                        <?php _e('Filter by type', 'encompass-feedback'); ?>
                    </label>
                    <select name="type" id="filter-by-type">
                        <option value=""><?php _e('All Types', 'encompass-feedback'); ?></option>
                        <?php foreach ($types as $type => $label) : ?>
                            <option value="<?php echo esc_attr($type); ?>" <?php selected($current_type, $type); ?>>
                                <?php echo esc_html($label); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    
                    <!-- Search -->
                    <label for="feedback-search-input" class="screen-reader-text">
                        <?php _e('Search feedback', 'encompass-feedback'); ?>
                    </label>
                    <input type="search" 
                           id="feedback-search-input" 
                           name="s" 
                           value="<?php echo esc_attr($current_search); ?>" 
                           placeholder="<?php esc_attr_e('Search feedback...', 'encompass-feedback'); ?>" />
                    
                    <input type="submit" class="button" value="<?php esc_attr_e('Filter', 'encompass-feedback'); ?>">
                    
                    <?php if ($current_status || $current_type || $current_search) : ?>
                        <a href="<?php echo esc_url($base_url); ?>" class="button">
                            <?php _e('Reset Filters', 'encompass-feedback'); ?>
                        </a>
                    <?php endif; ?>
                </div>
                
                <!-- Bulk actions -->
                <div class="tablenav-pages">
                    <span class="displaying-num">
                        <?php 
                        printf(
                            _n('%s item', '%s items', $total_items, 'encompass-feedback'),
                            number_format_i18n($total_items)
                        );
                        ?>
                    </span>
                    
                    <?php if ($total_pages > 1) : ?>
                        <span class="pagination-links">
                            <?php
                            $page_links = paginate_links(array(
                                'base' => add_query_arg('paged', '%#%', $base_url),
                                'format' => '',
                                'prev_text' => '&laquo;',
                                'next_text' => '&raquo;',
                                'total' => $total_pages,
                                'current' => $current_page,
                                'show_all' => false,
                                'end_size' => 1,
                                'mid_size' => 2,
                                'type' => 'array',
                                'add_args' => array(
                                    'status' => $current_status,
                                    'type' => $current_type,
                                    's' => $current_search,
                                ),
                            ));
                            
                            if ($page_links) {
                                echo '<span class="pagination-links">' . implode("\n", $page_links) . '</span>';
                            }
                            ?>
                        </span>
                    <?php endif; ?>
                </div>
            </div>
        </form>
    </div>
    
    <!-- Feedback table -->
    <table class="wp-list-table widefat fixed striped feedback">
        <thead>
            <tr>
                <td id="cb" class="manage-column column-cb check-column">
                    <input type="checkbox" id="cb-select-all-1">
                </td>
                <th scope="col" class="column-id"><?php _e('ID', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-type"><?php _e('Type', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-user"><?php _e('User', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-comment"><?php _e('Comment', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-status"><?php _e('Status', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-date"><?php _e('Date', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-actions"><?php _e('Actions', 'encompass-feedback'); ?></th>
            </tr>
        </thead>
        <tbody>
            <?php if (!empty($feedback_list)) : ?>
                <?php foreach ($feedback_list as $feedback) : 
                    $user = $feedback->user_id ? get_user_by('id', $feedback->user_id) : null;
                    $user_display = $user ? $user->display_name : __('Guest', 'encompass-feedback');
                    $user_email = $user ? $user->user_email : '';
                    $user_avatar = $user ? get_avatar_url($user->ID, array('size' => 32)) : '';
                    
                    // Truncate comment for display
                    $comment = wp_trim_words($feedback->comment, 10);
                    if (empty($comment) && !empty($feedback->rating)) {
                        $comment = sprintf(
                            _n('%d star', '%d stars', $feedback->rating, 'encompass-feedback'),
                            $feedback->rating
                        );
                    }
                    
                    // Get status label
                    $status_label = isset($statuses[$feedback->status]) ? $statuses[$feedback->status] : $feedback->status;
                    ?>
                    <tr>
                        <th scope="row" class="check-column">
                            <input type="checkbox" name="feedback[]" value="<?php echo esc_attr($feedback->id); ?>">
                        </th>
                        <td class="column-id">#<?php echo esc_html($feedback->id); ?></td>
                        <td class="column-type">
                            <?php 
                            $type_label = isset($types[$feedback->feedback_type]) ? 
                                $types[$feedback->feedback_type] : 
                                $feedback->feedback_type;
                            echo esc_html($type_label);
                            ?>
                        </td>
                        <td class="column-user">
                            <div class="user-info">
                                <?php if ($user_avatar) : ?>
                                    <img src="<?php echo esc_url($user_avatar); ?>" class="avatar avatar-32 photo" width="32" height="32">
                                <?php endif; ?>
                                <div class="user-details">
                                    <strong><?php echo esc_html($user_display); ?></strong>
                                    <?php if ($user_email) : ?>
                                        <br>
                                        <a href="mailto:<?php echo esc_attr($user_email); ?>">
                                            <?php echo esc_html($user_email); ?>
                                        </a>
                                    <?php endif; ?>
                                    <?php if ($feedback->user_ip) : ?>
                                        <br>
                                        <small>IP: <?php echo esc_html($feedback->user_ip); ?></small>
                                    <?php endif; ?>
                                </div>
                            </div>
                        </td>
                        <td class="column-comment">
                            <div class="comment-content">
                                <?php echo esc_html($comment); ?>
                                <?php if (!empty($feedback->page_title)) : ?>
                                    <div class="page-info">
                                        <a href="<?php echo esc_url($feedback->page_url); ?>" target="_blank">
                                            <?php echo esc_html($feedback->page_title); ?>
                                        </a>
                                    </div>
                                <?php endif; ?>
                            </div>
                        </td>
                        <td class="column-status">
                            <span class="status-badge status-<?php echo esc_attr($feedback->status); ?>">
                                <?php echo esc_html(ucfirst($status_label)); ?>
                            </span>
                        </td>
                        <td class="column-date">
                            <abbr title="<?php echo esc_attr(date_i18n('Y/m/d g:i a', strtotime($feedback->created_at))); ?>">
                                <?php echo esc_html(human_time_diff(strtotime($feedback->created_at), current_time('timestamp'))) . ' ' . __('ago', 'encompass-feedback'); ?>
                            </abbr>
                        </td>
                        <td class="column-actions">
                            <div class="row-actions">
                                <span class="view">
                                    <a href="<?php echo esc_url(admin_url('admin.php?page=encompass-feedback-detail&feedback_id=' . $feedback->id)); ?>">
                                        <?php _e('View', 'encompass-feedback'); ?>
                                    </a>
                                </span>
                                <span class="edit">
                                    <a href="#" class="edit-feedback" data-id="<?php echo esc_attr($feedback->id); ?>">
                                        <?php _e('Edit', 'encompass-feedback'); ?>
                                    </a>
                                </span>
                                <span class="trash">
                                    <a href="#" class="delete-feedback" data-id="<?php echo esc_attr($feedback->id); ?>">
                                        <?php _e('Delete', 'encompass-feedback'); ?>
                                    </a>
                                </span>
                            </div>
                        </td>
                    </tr>
                <?php endforeach; ?>
            <?php else : ?>
                <tr>
                    <td colspan="8" class="no-items">
                        <?php _e('No feedback found.', 'encompass-feedback'); ?>
                        <?php if ($current_status || $current_type || $current_search) : ?>
                            <a href="<?php echo esc_url($base_url); ?>">
                                <?php _e('Clear filters', 'encompass-feedback'); ?>
                            </a>
                        <?php endif; ?>
                    </td>
                </tr>
            <?php endif; ?>
        </tbody>
        <tfoot>
            <tr>
                <td class="manage-column column-cb check-column">
                    <input type="checkbox" id="cb-select-all-2">
                </td>
                <th scope="col" class="column-id"><?php _e('ID', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-type"><?php _e('Type', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-user"><?php _e('User', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-comment"><?php _e('Comment', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-status"><?php _e('Status', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-date"><?php _e('Date', 'encompass-feedback'); ?></th>
                <th scope="col" class="column-actions"><?php _e('Actions', 'encompass-feedback'); ?></th>
            </tr>
        </tfoot>
    </table>
    
    <!-- Bottom pagination -->
    <?php if ($total_pages > 1) : ?>
        <div class="tablenav bottom">
            <div class="tablenav-pages">
                <span class="displaying-num">
                    <?php 
                    printf(
                        _n('%s item', '%s items', $total_items, 'encompass-feedback'),
                        number_format_i18n($total_items)
                    );
                    ?>
                </span>
                <span class="pagination-links">
                    <?php
                    if ($page_links) {
                        echo implode("\n", $page_links);
                    }
                    ?>
                </span>
            </div>
        </div>
    <?php endif; ?>
    
    <!-- Bulk actions -->
    <div class="tablenav bottom">
        <div class="alignleft actions bulkactions">
            <label for="bulk-action-selector-bottom" class="screen-reader-text">
                <?php _e('Select bulk action', 'encompass-feedback'); ?>
            </label>
            <select name="action2" id="bulk-action-selector-bottom">
                <option value="-1"><?php _e('Bulk Actions', 'encompass-feedback'); ?></option>
                <option value="mark_new"><?php _e('Mark as New', 'encompass-feedback'); ?></option>
                <option value="mark_in_progress"><?php _e('Mark as In Progress', 'encompass-feedback'); ?></option>
                <option value="mark_resolved"><?php _e('Mark as Resolved', 'encompass-feedback'); ?></option>
                <option value="delete"><?php _e('Delete', 'encompass-feedback'); ?></option>
            </select>
            <input type="submit" class="button action" value="<?php esc_attr_e('Apply', 'encompass-feedback'); ?>">
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

<!-- Delete Confirmation Modal -->
<div id="delete-feedback-modal" class="encompass-feedback-modal" style="display: none;">
    <div class="encompass-feedback-modal-content">
        <div class="encompass-feedback-modal-header">
            <h2><?php _e('Delete Feedback', 'encompass-feedback'); ?></h2>
            <button type="button" class="encompass-feedback-modal-close">
                <span class="screen-reader-text"><?php _e('Close', 'encompass-feedback'); ?></span>
                <span class="dashicons dashicons-no-alt"></span>
            </button>
        </div>
        <div class="encompass-feedback-modal-body">
            <p><?php _e('Are you sure you want to delete this feedback? This action cannot be undone.', 'encompass-feedback'); ?></p>
        </div>
        <div class="encompass-feedback-modal-footer">
            <button type="button" class="button button-secondary encompass-feedback-modal-cancel">
                <?php _e('Cancel', 'encompass-feedback'); ?>
            </button>
            <button type="button" class="button button-danger encompass-feedback-modal-confirm-delete">
                <?php _e('Delete Permanently', 'encompass-feedback'); ?>
            </button>
        </div>
    </div>
</div>
