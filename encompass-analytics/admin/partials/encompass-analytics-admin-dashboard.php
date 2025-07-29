<?php
/**
 * Admin dashboard template
 */

// Security check
if (!defined('ABSPATH')) {
    exit;
}

// Get current date range
$start_date = isset($_GET['start_date']) ? sanitize_text_field($_GET['start_date']) : date('Y-m-d', strtotime('-30 days'));
$end_date = isset($_GET['end_date']) ? sanitize_text_field($_GET['end_date']) : date('Y-m-d');
?>

<div class="wrap encompass-analytics-wrap">
    <div class="encompass-analytics-header">
        <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
        <p><?php esc_html_e('Track and analyze your website traffic and user behavior.', 'encompass-analytics'); ?></p>
    </div>

    <!-- Date Range Picker -->
    <div class="card">
        <div class="card-header">
            <h3><?php esc_html_e('Date Range', 'encompass-analytics'); ?></h3>
        </div>
        <div class="card-body">
            <form id="date-range-form" method="get" action="">
                <input type="hidden" name="page" value="encompass-analytics" />
                <div class="encompass-date-range-picker" style="display: flex; align-items: center; gap: 15px;">
                    <div>
                        <label for="start-date"><?php esc_html_e('From:', 'encompass-analytics'); ?></label>
                        <input type="date" id="start-date" name="start_date" value="<?php echo esc_attr($start_date); ?>" class="regular-text" />
                    </div>
                    <div>
                        <label for="end-date"><?php esc_html_e('To:', 'encompass-analytics'); ?></label>
                        <input type="date" id="end-date" name="end_date" value="<?php echo esc_attr($end_date); ?>" class="regular-text" />
                    </div>
                    <div>
                        <button type="submit" class="button button-primary"><?php esc_html_e('Apply', 'encompass-analytics'); ?></button>
                        <button type="button" id="reset-date-range" class="button"><?php esc_html_e('Reset', 'encompass-analytics'); ?></button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <!-- Stats Overview -->
    <div class="stats-grid">
        <div class="stat-card">
            <h3><?php esc_html_e('Total Visitors', 'encompass-analytics'); ?></h3>
            <div class="stat-number" id="total-visitors">--</div>
            <div class="stat-delta" id="visitors-delta">--</div>
        </div>
        <div class="stat-card">
            <h3><?php esc_html_e('Page Views', 'encompass-analytics'); ?></h3>
            <div class="stat-number" id="total-pageviews">--</div>
            <div class="stat-delta" id="pageviews-delta">--</div>
        </div>
        <div class="stat-card">
            <h3><?php esc_html_e('Avg. Session Duration', 'encompass-analytics'); ?></h3>
            <div class="stat-number" id="avg-session-duration">--</div>
            <div class="stat-delta" id="duration-delta">--</div>
        </div>
        <div class="stat-card">
            <h3><?php esc_html_e('Bounce Rate', 'encompass-analytics'); ?></h3>
            <div class="stat-number" id="bounce-rate">--</div>
            <div class="stat-delta" id="bounce-delta">--</div>
        </div>
    </div>

    <!-- Charts Row -->
    <div class="encompass-widgets">
        <div class="encompass-widget">
            <div class="encompass-widget-header">
                <h3><?php esc_html_e('Visitors & Page Views', 'encompass-analytics'); ?></h3>
            </div>
            <div class="encompass-widget-body">
                <div class="chart-container">
                    <canvas id="visitors-chart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="encompass-widget">
            <div class="encompass-widget-header">
                <h3><?php esc_html_e('Top Pages', 'encompass-analytics'); ?></h3>
            </div>
            <div class="encompass-widget-body">
                <div class="table-responsive">
                    <table class="encompass-table" id="top-pages-table">
                        <thead>
                            <tr>
                                <th><?php esc_html_e('Page', 'encompass-analytics'); ?></th>
                                <th><?php esc_html_e('Views', 'encompass-analytics'); ?></th>
                                <th><?php esc_html_e('Unique', 'encompass-analytics'); ?></th>
                                <th><?php esc_html_e('Avg. Time', 'encompass-analytics'); ?></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td colspan="4" class="encompass-loading"><?php esc_html_e('Loading...', 'encompass-analytics'); ?></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Second Row -->
    <div class="encompass-widgets">
        <div class="encompass-widget">
            <div class="encompass-widget-header">
                <h3><?php esc_html_e('Traffic Sources', 'encompass-analytics'); ?></h3>
            </div>
            <div class="encompass-widget-body">
                <div class="chart-container" style="height: 250px;">
                    <canvas id="sources-chart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="encompass-widget">
            <div class="encompass-widget-header">
                <h3><?php esc_html_e('Devices', 'encompass-analytics'); ?></h3>
            </div>
            <div class="encompass-widget-body">
                <div class="chart-container" style="height: 250px;">
                    <canvas id="devices-chart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- Third Row -->
    <div class="card">
        <div class="card-header">
            <h3><?php esc_html_e('Recent Activity', 'encompass-analytics'); ?></h3>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="encompass-table" id="recent-activity-table">
                    <thead>
                        <tr>
                            <th><?php esc_html_e('Time', 'encompass-analytics'); ?></th>
                            <th><?php esc_html_e('Event', 'encompass-analytics'); ?></th>
                            <th><?php esc_html_e('Page', 'encompass-analytics'); ?></th>
                            <th><?php esc_html_e('User', 'encompass-analytics'); ?></th>
                            <th><?php esc_html_e('Details', 'encompass-analytics'); ?></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="5" class="encompass-loading"><?php esc_html_e('Loading recent activity...', 'encompass-analytics'); ?></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- JavaScript for the dashboard -->
<script type="text/javascript">
jQuery(document).ready(function($) {
    // Initialize date range picker
    $('input[type="date"]').datepicker({
        dateFormat: 'yy-mm-dd'
    });

    // Reset date range
    $('#reset-date-range').on('click', function() {
        var today = new Date();
        var lastMonth = new Date();
        lastMonth.setMonth(today.getMonth() - 1);
        
        $('#start-date').val($.datepicker.formatDate('yy-mm-dd', lastMonth));
        $('#end-date').val($.datepicker.formatDate('yy-mm-dd', today));
        $('#date-range-form').submit();
    });

    // Load dashboard data
    function loadDashboardData() {
        var startDate = $('#start-date').val();
        var endDate = $('#end-date').val();
        
        // Show loading states
        $('.stat-number, .stat-delta').text('--');
        $('.encompass-loading').show();
        
        // Get overview data
        $.ajax({
            url: encompassAnalytics.rest_url + 'analytics/overview',
            type: 'GET',
            data: {
                start_date: startDate,
                end_date: endDate,
                _wpnonce: encompassAnalytics.nonce
            },
            success: function(response) {
                if (response.success) {
                    updateOverviewStats(response.data.overview);
                    updateTopPages(response.data.top_pages);
                }
            },
            error: function() {
                alert('Error loading overview data');
            }
        });

        // Get recent activity
        $.ajax({
            url: encompassAnalytics.rest_url + 'analytics/events',
            type: 'GET',
            data: {
                start_date: startDate,
                end_date: endDate,
                per_page: 10,
                _wpnonce: encompassAnalytics.nonce
            },
            success: function(response) {
                if (response.success) {
                    updateRecentActivity(response.data);
                }
            }
        });

        // Get charts data
        loadChartsData(startDate, endDate);
    }

    // Update overview statistics
    function updateOverviewStats(data) {
        $('#total-visitors').text(data.visitors || 0);
        $('#total-pageviews').text(data.pageviews || 0);
        $('#avg-session-duration').text(formatDuration(data.avg_session_duration) || '0:00');
        $('#bounce-rate').text((data.bounce_rate || 0) + '%');
        
        // Update deltas
        updateDelta('#visitors-delta', data.visitors_delta);
        updateDelta('#pageviews-delta', data.pageviews_delta);
        updateDelta('#duration-delta', data.duration_delta, true);
        updateDelta('#bounce-delta', data.bounce_delta);
    }

    // Update top pages table
    function updateTopPages(pages) {
        var $table = $('#top-pages-table tbody');
        $table.empty();
        
        if (!pages || pages.length === 0) {
            $table.append('<tr><td colspan="4"><?php esc_html_e('No data available', 'encompass-analytics'); ?></td></tr>');
            return;
        }
        
        pages.forEach(function(page) {
            var row = '<tr>' +
                '<td><a href="' + escapeHtml(page.url) + '" target="_blank">' + escapeHtml(page.title || page.url) + '</a></td>' +
                '<td>' + (page.views || 0) + '</td>' +
                '<td>' + (page.unique_views || 0) + '</td>' +
                '<td>' + formatDuration(page.avg_time_on_page || 0) + '</td>' +
                '</tr>';
            $table.append(row);
        });
    }

    // Update recent activity table
    function updateRecentActivity(activities) {
        var $table = $('#recent-activity-table tbody');
        $table.empty();
        
        if (!activities || activities.length === 0) {
            $table.append('<tr><td colspan="5"><?php esc_html_e('No recent activity', 'encompass-analytics'); ?></td></tr>');
            return;
        }
        
        activities.forEach(function(activity) {
            var time = new Date(activity.timestamp).toLocaleString();
            var details = '';
            
            if (activity.event_data) {
                try {
                    var eventData = typeof activity.event_data === 'string' ? JSON.parse(activity.event_data) : activity.event_data;
                    details = JSON.stringify(eventData, null, 2);
                } catch (e) {
                    details = activity.event_data;
                }
            }
            
            var row = '<tr>' +
                '<td>' + escapeHtml(time) + '</td>' +
                '<td>' + escapeHtml(activity.event_type) + '</td>' +
                '<td><a href="' + escapeHtml(activity.page_url || '#') + '" target="_blank">' + 
                escapeHtml(activity.page_title || 'N/A') + '</a></td>' +
                '<td>' + escapeHtml(activity.user_id || 'Guest') + '</td>' +
                '<td><button class="button button-small view-details" data-details="' + 
                escapeHtml(details) + '"><?php esc_html_e('View', 'encompass-analytics'); ?></button></td>' +
                '</tr>';
            $table.append(row);
        });
        
        // Add click handler for details buttons
        $('.view-details').on('click', function() {
            var details = $(this).data('details');
            alert(details);
        });
    }

    // Load charts data
    function loadChartsData(startDate, endDate) {
        // This would be populated with actual chart data loading logic
        // using Chart.js to render the charts
        
        // Example visitors chart
        var visitorsCtx = document.getElementById('visitors-chart').getContext('2d');
        if (window.visitorsChart) {
            window.visitorsChart.destroy();
        }
        
        window.visitorsChart = new Chart(visitorsCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                datasets: [
                    {
                        label: 'Visitors',
                        data: [65, 59, 80, 81, 56, 55, 40],
                        borderColor: '#2271b1',
                        backgroundColor: 'rgba(34, 113, 177, 0.1)',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Page Views',
                        data: [120, 98, 150, 140, 110, 125, 90],
                        borderColor: '#00a32a',
                        backgroundColor: 'rgba(0, 163, 42, 0.1)',
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // Example sources chart (doughnut)
        var sourcesCtx = document.getElementById('sources-chart').getContext('2d');
        if (window.sourcesChart) {
            window.sourcesChart.destroy();
        }
        
        window.sourcesChart = new Chart(sourcesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Direct', 'Search Engines', 'Social', 'Referral', 'Email'],
                datasets: [{
                    data: [45, 25, 15, 10, 5],
                    backgroundColor: [
                        '#2271b1',
                        '#00a32a',
                        '#dba617',
                        '#d63638',
                        '#826eb4'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
        
        // Example devices chart (pie)
        var devicesCtx = document.getElementById('devices-chart').getContext('2d');
        if (window.devicesChart) {
            window.devicesChart.destroy();
        }
        
        window.devicesChart = new Chart(devicesCtx, {
            type: 'pie',
            data: {
                labels: ['Desktop', 'Mobile', 'Tablet'],
                datasets: [{
                    data: [60, 30, 10],
                    backgroundColor: [
                        '#2271b1',
                        '#00a32a',
                        '#dba617'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
    }
    
    // Helper functions
    function updateDelta(element, value, isPositiveGood) {
        var $element = $(element);
        $element.removeClass('positive negative');
        
        if (value === undefined || value === null) {
            $element.text('--');
            return;
        }
        
        var prefix = value > 0 ? '+' : '';
        $element.text(prefix + value + '%');
        
        if (value > 0) {
            $element.addClass(isPositiveGood ? 'positive' : 'negative');
        } else if (value < 0) {
            $element.addClass(isPositiveGood ? 'negative' : 'positive');
        }
    }
    
    function formatDuration(seconds) {
        if (!seconds) return '0:00';
        
        var minutes = Math.floor(seconds / 60);
        var remainingSeconds = Math.floor(seconds % 60);
        return minutes + ':' + (remainingSeconds < 10 ? '0' : '') + remainingSeconds;
    }
    
    function escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) return '';
        return unsafe
            .toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    // Initial load
    loadDashboardData();
});
</script>
