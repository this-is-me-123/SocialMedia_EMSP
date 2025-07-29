<?php
/**
 * Dashboard template for Encompass Feedback
 *
 * @package Encompass_Feedback
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

// Enqueue dashboard scripts
wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.7.0', true);
wp_enqueue_script('encompass-feedback-dashboard', ENCOMPASS_FEEDBACK_PLUGIN_URL . 'assets/js/dashboard.js', array('jquery', 'chart-js'), ENCOMPASS_FEEDBACK_VERSION, true);

// Get feedback statistics
$stats = array(
    'total' => $this->db->get_feedback_count(),
    'new' => $this->db->get_feedback_count(array('status' => 'new')),
    'in_progress' => $this->db->get_feedback_count(array('status' => 'in_progress')),
    'resolved' => $this->db->get_feedback_count(array('status' => 'resolved')),
);

// Get recent feedback
$recent_feedback = $this->db->get_feedback_list(array(
    'number' => 5,
    'orderby' => 'created_at',
    'order' => 'DESC',
));

// Get feedback by type
$feedback_by_type = $this->db->get_feedback_by_type();

// Get feedback by status
$feedback_by_status = $this->db->get_feedback_by_status();
?>

<div class="wrap encompass-feedback-dashboard">
    <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
    
    <!-- Stats Overview -->
    <div class="encompass-feedback-stats">
        <div class="stat-card total">
            <h3><?php _e('Total Feedback', 'encompass-feedback'); ?></h3>
            <div class="stat-number"><?php echo esc_html($stats['total']); ?></div>
        </div>
        
        <div class="stat-card new">
            <h3><?php _e('New', 'encompass-feedback'); ?></h3>
            <div class="stat-number"><?php echo esc_html($stats['new']); ?></div>
        </div>
        
        <div class="stat-card in-progress">
            <h3><?php _e('In Progress', 'encompass-feedback'); ?></h3>
            <div class="stat-number"><?php echo esc_html($stats['in_progress']); ?></div>
        </div>
        
        <div class="stat-card resolved">
            <h3><?php _e('Resolved', 'encompass-feedback'); ?></h3>
            <div class="stat-number"><?php echo esc_html($stats['resolved']); ?></div>
        </div>
    </div>
    
    <div class="encompass-feedback-charts">
        <div class="chart-container">
            <h3><?php _e('Feedback by Type', 'encompass-feedback'); ?></h3>
            <canvas id="feedbackByTypeChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h3><?php _e('Feedback by Status', 'encompass-feedback'); ?></h3>
            <canvas id="feedbackByStatusChart"></canvas>
        </div>
    </div>
    
    <div class="encompass-feedback-recent">
        <h2><?php _e('Recent Feedback', 'encompass-feedback'); ?></h2>
        
        <?php if (!empty($recent_feedback)) : ?>
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th><?php _e('ID', 'encompass-feedback'); ?></th>
                        <th><?php _e('Type', 'encompass-feedback'); ?></th>
                        <th><?php _e('User', 'encompass-feedback'); ?></th>
                        <th><?php _e('Comment', 'encompass-feedback'); ?></th>
                        <th><?php _e('Status', 'encompass-feedback'); ?></th>
                        <th><?php _e('Date', 'encompass-feedback'); ?></th>
                        <th><?php _e('Actions', 'encompass-feedback'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($recent_feedback as $feedback) : ?>
                        <tr>
                            <td>#<?php echo esc_html($feedback->id); ?></td>
                            <td><?php echo esc_html($feedback->feedback_type); ?></td>
                            <td>
                                <?php 
                                if ($feedback->user_id) {
                                    $user = get_user_by('id', $feedback->user_id);
                                    if ($user) {
                                        echo esc_html($user->display_name);
                                    }
                                } else {
                                    _e('Guest', 'encompass-feedback');
                                }
                                ?>
                            </td>
                            <td><?php echo esc_html(wp_trim_words($feedback->comment, 10)); ?></td>
                            <td>
                                <span class="status-badge status-<?php echo esc_attr($feedback->status); ?>">
                                    <?php echo esc_html(ucfirst(str_replace('_', ' ', $feedback->status))); ?>
                                </span>
                            </td>
                            <td><?php echo esc_html(date_i18n(get_option('date_format'), strtotime($feedback->created_at))); ?></td>
                            <td>
                                <a href="<?php echo esc_url(admin_url('admin.php?page=encompass-feedback-detail&feedback_id=' . $feedback->id)); ?>" class="button button-small">
                                    <?php _e('View', 'encompass-feedback'); ?>
                                </a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            
            <p class="view-all-link">
                <a href="<?php echo esc_url(admin_url('admin.php?page=encompass-feedback-all')); ?>">
                    <?php _e('View All Feedback', 'encompass-feedback'); ?> &rarr;
                </a>
            </p>
        <?php else : ?>
            <p><?php _e('No feedback found.', 'encompass-feedback'); ?></p>
        <?php endif; ?>
    </div>
</div>

<script type="text/javascript">
// Pass data to JavaScript
jQuery(document).ready(function($) {
    // Feedback by Type chart
    const typeCtx = document.getElementById('feedbackByTypeChart').getContext('2d');
    new Chart(typeCtx, {
        type: 'doughnut',
        data: {
            labels: <?php echo json_encode(array_column($feedback_by_type, 'type')); ?>,
            datasets: [{
                data: <?php echo json_encode(array_column($feedback_by_type, 'count')); ?>,
                backgroundColor: [
                    '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
                    '#5a5c69', '#858796', '#3a3b45', '#1cc88a', '#36b9cc'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });

    // Feedback by Status chart
    const statusCtx = document.getElementById('feedbackByStatusChart').getContext('2d');
    new Chart(statusCtx, {
        type: 'bar',
        data: {
            labels: <?php echo json_encode(array_column($feedback_by_status, 'status')); ?>,
            datasets: [{
                label: '<?php _e('Number of Feedback', 'encompass-feedback'); ?>',
                data: <?php echo json_encode(array_column($feedback_by_status, 'count')); ?>,
                backgroundColor: [
                    '#4e73df', // New
                    '#f6c23e', // In Progress
                    '#1cc88a', // Resolved
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
});
</script>
