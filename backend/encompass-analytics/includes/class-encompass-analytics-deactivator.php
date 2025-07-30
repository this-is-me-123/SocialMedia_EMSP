<?php
/**
 * Fired during plugin deactivation
 */
class Encompass_MSP_Analytics_Deactivator {
    public static function deactivate(): void {
        // Clear any scheduled hooks
        wp_clear_scheduled_hook('encompass_analytics_cleanup');
        
        // Note: We're not dropping tables on deactivation to prevent data loss
        // If you want to remove all plugin data, use the uninstall.php file
    }
}
