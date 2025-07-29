<?php if (!defined('ABSPATH')) exit; ?>

<div class="wrap encompass-feedback-dashboard">
    <h1 class="wp-heading-inline"><?php _e('Feedback Dashboard', 'encompass-feedback'); ?></h1>
    
    <div class="encompass-feedback-dashboard-header">
        <div class="encompass-feedback-stats-container">
            <div class="encompass-feedback-stat-card">
                <div class="encompass-feedback-stat-card-icon">
                    <span class="dashicons dashicons-feedback"></span>
                </div>
                <div class="encompass-feedback-stat-card-content">
                    <h3><?php _e('Total Feedback', 'encompass-feedback'); ?></h3>
                    <div class="encompass-feedback-stat-card-value" id="total-feedback-count">-</div>
                    <div class="encompass-feedback-stat-card-diff" id="feedback-trend">
                        <span class="dashicons dashicons-arrow-up-alt"></span>
                        <span>0%</span> from last period
                    </div>
                </div>
            </div>
            
            <div class="encompass-feedback-stat-card">
                <div class="encompass-feedback-stat-card-icon">
                    <span class="dashicons dashicons-star-filled"></span>
                </div>
                <div class="encompass-feedback-stat-card-content">
                    <h3><?php _e('Average Rating', 'encompass-feedback'); ?></h3>
                    <div class="encompass-feedback-stat-card-value" id="average-rating">-</div>
                    <div class="encompass-feedback-rating-stars">
                        <?php for ($i = 1; $i <= 5; $i++) : ?>
                            <span class="dashicons dashicons-star-filled"></span>
                        <?php endfor; ?>
                    </div>
                </div>
            </div>
            
            <div class="encompass-feedback-stat-card">
                <div class="encompass-feedback-stat-card-icon">
                    <span class="dashicons dashicons-email"></span>
                </div>
                <div class="encompass-feedback-stat-card-content">
                    <h3><?php _e('New This Week', 'encompass-feedback'); ?></h3>
                    <div class="encompass-feedback-stat-card-value" id="new-this-week">-</div>
                    <div class="encompass-feedback-stat-card-desc">
                        <?php _e('Feedback items received this week', 'encompass-feedback'); ?>
                    </div>
                </div>
            </div>
            
            <div class="encompass-feedback-stat-card">
                <div class="encompass-feedback-stat-card-icon">
                    <span class="dashicons dashicons-chart-bar"></span>
                </div>
                <div class="encompass-feedback-stat-card-content">
                    <h3><?php _e('Response Rate', 'encompass-feedback'); ?></h3>
                    <div class="encompass-feedback-stat-card-value" id="response-rate">-</div>
                    <div class="encompass-feedback-stat-card-desc">
                        <?php _e('Of feedback has been responded to', 'encompass-feedback'); ?>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="encompass-feedback-dashboard-content">
        <div class="encompass-feedback-row">
            <div class="encompass-feedback-col-2-3">
                <div class="encompass-feedback-card">
                    <div class="encompass-feedback-card-header">
                        <h2><?php _e('Feedback Over Time', 'encompass-feedback'); ?></h2>
                        <div class="encompass-feedback-card-actions">
                            <select id="feedback-time-range" class="encompass-feedback-select">
                                <option value="7"><?php _e('Last 7 Days', 'encompass-feedback'); ?></option>
                                <option value="30" selected><?php _e('Last 30 Days', 'encompass-feedback'); ?></option>
                                <option value="90"><?php _e('Last 90 Days', 'encompass-feedback'); ?></option>
                                <option value="365"><?php _e('Last Year', 'encompass-feedback'); ?></option>
                            </select>
                        </div>
                    </div>
                    <div class="encompass-feedback-card-body">
                        <canvas id="feedback-trend-chart" height="300"></canvas>
                    </div>
                </div>
                
                <div class="encompass-feedback-card encompass-feedback-mt-3">
                    <div class="encompass-feedback-card-header">
                        <h2><?php _e('Recent Feedback', 'encompass-feedback'); ?></h2>
                        <a href="<?php echo admin_url('admin.php?page=encompass-feedback-all'); ?>" class="button">
                            <?php _e('View All', 'encompass-feedback'); ?>
                        </a>
                    </div>
                    <div class="encompass-feedback-card-body">
                        <?php if (!empty($recent_feedback)) : ?>
                            <div class="encompass-feedback-list">
                                <?php foreach ($recent_feedback as $feedback) : 
                                    $user = $feedback->user_id ? get_userdata($feedback->user_id) : null;
                                    $rating = $feedback->rating ? $feedback->rating : 0;
                                    $status_class = 'encompass-feedback-status-' . $feedback->status;
                                ?>
                                    <div class="encompass-feedback-list-item <?php echo esc_attr($status_class); ?>">
                                        <div class="encompass-feedback-list-item-header">
                                            <div class="encompass-feedback-list-item-avatar">
                                                <?php if ($user) : ?>
                                                    <?php echo get_avatar($user->ID, 40); ?>
                                                <?php else : ?>
                                                    <div class="encompass-feedback-avatar-placeholder">
                                                        <span class="dashicons dashicons-admin-users"></span>
                                                    </div>
                                                <?php endif; ?>
                                            </div>
                                            <div class="encompass-feedback-list-item-info">
                                                <h3 class="encompass-feedback-list-item-title">
                                                    <?php if ($user) : ?>
                                                        <?php echo esc_html($user->display_name); ?>
                                                    <?php else : ?>
                                                        <?php echo !empty($feedback->meta['name']) ? esc_html($feedback->meta['name']) : __('Anonymous', 'encompass-feedback'); ?>
                                                    <?php endif; ?>
                                                    <span class="encompass-feedback-list-item-meta">
                                                        <?php 
                                                            printf(
                                                                /* translators: %s: Time ago */
                                                                __('%s ago', 'encompass-feedback'), 
                                                                human_time_diff(strtotime($feedback->created_at), current_time('timestamp'))
                                                            );
                                                        ?>
                                                        <?php if (!empty($feedback->page_title)) : ?>
                                                            &middot; 
                                                            <a href="<?php echo esc_url($feedback->page_url); ?>" target="_blank">
                                                                <?php echo esc_html($feedback->page_title); ?>
                                                            </a>
                                                        <?php endif; ?>
                                                    </span>
                                                </h3>
                                                <div class="encompass-feedback-list-item-rating">
                                                    <?php for ($i = 1; $i <= 5; $i++) : ?>
                                                        <span class="dashicons dashicons-star-filled <?php echo $i <= $rating ? 'encompass-feedback-rating-filled' : ''; ?>"></span>
                                                    <?php endfor; ?>
                                                    <span class="encompass-feedback-list-item-type">
                                                        <?php 
                                                            $feedback_types = $this->get_feedback_types();
                                                            echo isset($feedback_types[$feedback->feedback_type]) ? 
                                                                esc_html($feedback_types[$feedback->feedback_type]) : 
                                                                esc_html(ucfirst($feedback->feedback_type));
                                                        ?>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="encompass-feedback-list-item-actions">
                                                <span class="encompass-feedback-status-badge encompass-feedback-status-<?php echo esc_attr($feedback->status); ?>">
                                                    <?php 
                                                        $statuses = $this->get_feedback_statuses();
                                                        echo isset($statuses[$feedback->status]) ? 
                                                            esc_html($statuses[$feedback->status]) : 
                                                            esc_html(ucfirst($feedback->status));
                                                    ?>
                                                </span>
                                                <a href="<?php echo admin_url('admin.php?page=encompass-feedback&feedback_id=' . $feedback->id); ?>" class="button button-small">
                                                    <?php _e('View', 'encompass-feedback'); ?>
                                                </a>
                                            </div>
                                        </div>
                                        <div class="encompass-feedback-list-item-content">
                                            <p><?php echo esc_html(wp_trim_words($feedback->comment, 30, '...')); ?></p>
                                        </div>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        <?php else : ?>
                            <div class="encompass-feedback-empty">
                                <div class="encompass-feedback-empty-icon">
                                    <span class="dashicons dashicons-format-chat"></span>
                                </div>
                                <h3><?php _e('No feedback yet', 'encompass-feedback'); ?></h3>
                                <p><?php _e('Your feedback will appear here once users start submitting it.', 'encompass-feedback'); ?></p>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
            
            <div class="encompass-feedback-col-1-3">
                <div class="encompass-feedback-card">
                    <div class="encompass-feedback-card-header">
                        <h2><?php _e('Feedback by Type', 'encompass-feedback'); ?></h2>
                    </div>
                    <div class="encompass-feedback-card-body">
                        <canvas id="feedback-type-chart" height="250"></canvas>
                        <div id="feedback-type-legend" class="encompass-feedback-chart-legend"></div>
                    </div>
                </div>
                
                <div class="encompass-feedback-card encompass-feedback-mt-3">
                    <div class="encompass-feedback-card-header">
                        <h2><?php _e('Feedback by Status', 'encompass-feedback'); ?></h2>
                    </div>
                    <div class="encompass-feedback-card-body">
                        <canvas id="feedback-status-chart" height="250"></canvas>
                        <div id="feedback-status-legend" class="encompass-feedback-chart-legend"></div>
                    </div>
                </div>
                
                <div class="encompass-feedback-card encompass-feedback-mt-3">
                    <div class="encompass-feedback-card-header">
                        <h2><?php _e('Top Pages', 'encompass-feedback'); ?></h2>
                        <a href="#" class="button button-link"><?php _e('View All', 'encompass-feedback'); ?></a>
                    </div>
                    <div class="encompass-feedback-card-body">
                        <div class="encompass-feedback-pages-list">
                            <?php 
                            $top_pages = $encompass_feedback_db->get_feedback_by_pages(5); 
                            if (!empty($top_pages)) : 
                                foreach ($top_pages as $page) : 
                            ?>
                                <div class="encompass-feedback-page-item">
                                    <div class="encompass-feedback-page-title">
                                        <a href="<?php echo esc_url($page->page_url); ?>" target="_blank">
                                            <?php echo !empty($page->page_title) ? esc_html($page->page_title) : esc_html($page->page_url); ?>
                                        </a>
                                    </div>
                                    <div class="encompass-feedback-page-meta">
                                        <span class="encompass-feedback-page-count">
                                            <?php 
                                                printf(
                                                    /* translators: %d: Feedback count */
                                                    _n('%d feedback', '%d feedback', $page->count, 'encompass-feedback'), 
                                                    $page->count
                                                );
                                            ?>
                                        </span>
                                        <span class="encompass-feedback-page-rating">
                                            <?php 
                                                $avg_rating = $page->avg_rating ? round($page->avg_rating, 1) : 0;
                                                for ($i = 1; $i <= 5; $i++) : 
                                            ?>
                                                <span class="dashicons dashicons-star-filled <?php echo $i <= $avg_rating ? 'encompass-feedback-rating-filled' : ''; ?>"></span>
                                            <?php endfor; ?>
                                            <span class="encompass-feedback-rating-value"><?php echo number_format($avg_rating, 1); ?></span>
                                        </span>
                                    </div>
                                </div>
                            <?php 
                                endforeach; 
                            else : 
                            ?>
                                <div class="encompass-feedback-empty">
                                    <p><?php _e('No page feedback data available yet.', 'encompass-feedback'); ?></p>
                                </div>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Feedback Detail Modal -->
<div id="encompass-feedback-detail-modal" class="encompass-feedback-modal" style="display: none;">
    <div class="encompass-feedback-modal-content">
        <div class="encompass-feedback-modal-header">
            <h3><?php _e('Feedback Details', 'encompass-feedback'); ?></h3>
            <button type="button" class="encompass-feedback-close" aria-label="<?php esc_attr_e('Close', 'encompass-feedback'); ?>">
                &times;
            </button>
        </div>
        <div class="encompass-feedback-modal-body" id="feedback-detail-content">
            <!-- Content will be loaded via AJAX -->
            <div class="encompass-feedback-loading">
                <span class="spinner is-active"></span>
                <?php _e('Loading...', 'encompass-feedback'); ?>
            </div>
        </div>
    </div>
</div>

<script type="text/template" id="tmpl-encompass-feedback-detail">
    <div class="encompass-feedback-detail">
        <div class="encompass-feedback-detail-header">
            <div class="encompass-feedback-detail-avatar">
                <# if (data.user) { #>
                    <img src="{{ data.user.avatar }}" alt="{{ data.user.name }}" width="80" height="80">
                <# } else { #>
                    <div class="encompass-feedback-avatar-placeholder">
                        <span class="dashicons dashicons-admin-users"></span>
                    </div>
                <# } #>
            </div>
            <div class="encompass-feedback-detail-info">
                <h2>
                    <# if (data.user) { #>
                        {{ data.user.name }}
                    <# } else { #>
                        {{ data.meta.name || '<?php esc_attr_e('Anonymous', 'encompass-feedback'); ?>' }}
                    <# } #>
                </h2>
                <div class="encompass-feedback-detail-meta">
                    <span class="encompass-feedback-detail-date">
                        <?php 
                            /* translators: %s: Human-readable time difference */
                            printf(
                                __('Submitted %s', 'encompass-feedback'),
                                '{{ data.human_time_diff }}'
                            );
                        ?>
                    </span>
                    <span class="encompass-feedback-detail-type">
                        {{ data.feedback_type_label }}
                    </span>
                    <span class="encompass-feedback-status-badge encompass-feedback-status-{{ data.status }}">
                        {{ data.status_label }}
                    </span>
                </div>
                <# if (data.rating) { #>
                    <div class="encompass-feedback-detail-rating">
                        <# for (var i = 1; i <= 5; i++) { #>
                            <span class="dashicons dashicons-star-filled <# if (i <= data.rating) { #>encompass-feedback-rating-filled<# } #>"></span>
                        <# } #>
                        <span class="encompass-feedback-rating-value">{{ data.rating }}/5</span>
                    </div>
                <# } #>
            </div>
        </div>
        
        <div class="encompass-feedback-detail-content">
            <h3><?php _e('Feedback', 'encompass-feedback'); ?></h3>
            <div class="encompass-feedback-detail-comment">
                {{{ data.comment }}}
            </div>
            
            <# if (data.page_url) { #>
                <div class="encompass-feedback-detail-page">
                    <h3><?php _e('Page', 'encompass-feedback'); ?></h3>
                    <p>
                        <a href="{{ data.page_url }}" target="_blank">
                            {{ data.page_title || data.page_url }}
                        </a>
                    </p>
                </div>
            <# } #>
            
            <div class="encompass-feedback-detail-actions">
                <div class="encompass-feedback-detail-actions-left">
                    <button type="button" class="button button-primary encompass-feedback-action-reply" data-feedback-id="{{ data.id }}">
                        <span class="dashicons dashicons-email-alt"></span>
                        <?php _e('Reply', 'encompass-feedback'); ?>
                    </button>
                    <button type="button" class="button encompass-feedback-action-edit" data-feedback-id="{{ data.id }}">
                        <span class="dashicons dashicons-edit"></span>
                        <?php _e('Edit', 'encompass-feedback'); ?>
                    </button>
                </div>
                <div class="encompass-feedback-detail-actions-right">
                    <button type="button" class="button button-link button-link-delete encompass-feedback-action-delete" data-feedback-id="{{ data.id }}">
                        <span class="dashicons dashicons-trash"></span>
                        <?php _e('Delete', 'encompass-feedback'); ?>
                    </button>
                </div>
            </div>
        </div>
        
        <# if (data.meta) { #>
            <div class="encompass-feedback-detail-meta-container">
                <h3><?php _e('Additional Information', 'encompass-feedback'); ?></h3>
                <table class="encompass-feedback-detail-meta-table">
                    <# 
                    var metaLabels = {
                        'user_ip': '<?php esc_attr_e('IP Address', 'encompass-feedback'); ?>',
                        'user_agent': '<?php esc_attr_e('User Agent', 'encompass-feedback'); ?>',
                        'browser': '<?php esc_attr_e('Browser', 'encompass-feedback'); ?>',
                        'os': '<?php esc_attr_e('Operating System', 'encompass-feedback'); ?>',
                        'device': '<?php esc_attr_e('Device', 'encompass-feedback'); ?>',
                        'screen_resolution': '<?php esc_attr_e('Screen Resolution', 'encompass-feedback'); ?>',
                        'referrer': '<?php esc_attr_e('Referrer', 'encompass-feedback'); ?>',
                        'email': '<?php esc_attr_e('Email', 'encompass-feedback'); ?>',
                        'name': '<?php esc_attr_e('Name', 'encompass-feedback'); ?>'
                    };
                    
                    // Only show specific meta fields
                    var allowedMeta = ['email', 'name', 'user_ip', 'user_agent', 'browser', 'os', 'device', 'screen_resolution', 'referrer'];
                    
                    // Check each meta field
                    allowedMeta.forEach(function(metaKey) {
                        if (data.meta[metaKey]) {
                            var label = metaLabels[metaKey] || metaKey.replace(/_/g, ' ').replace(/\b\w/g, function(l) { return l.toUpperCase(); });
                            var value = data.meta[metaKey];
                            
                            // Format specific fields
                            if (metaKey === 'user_agent') {
                                value = '<code>' + value + '</code>';
                            } else if (metaKey === 'user_ip') {
                                value = value + ' <a href="https://whois.domaintools.com/' + value + '" target="_blank" class="button button-small button-link" style="margin-left: 5px;"><?php esc_attr_e('Whois', 'encompass-feedback'); ?></a>';
                            } else if (metaKey === 'email' && data.meta.email) {
                                value = '<a href="mailto:' + data.meta.email + '">' + data.meta.email + '</a>';
                            }
                            #>
                            <tr>
                                <th>{{ label }}:</th>
                                <td>{{{ value }}}</td>
                            </tr>
                            <#
                        }
                    });
                    #>
                </table>
            </div>
        <# } #>
    </div>
</script>
