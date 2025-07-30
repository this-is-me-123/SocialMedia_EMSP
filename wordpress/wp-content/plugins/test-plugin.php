<?php
/**
 * Test script for Encompass Analytics plugin
 * 
 * This script tests the plugin activation and database table creation.
 * Run this after setting up the Docker environment and before activating the plugin in WordPress.
 */

define('WP_DEBUG', true);

echo "=== Encompass Analytics Plugin Tester ===\n\n";

// Simulate WordPress environment
function add_action() {}
function add_filter() {}
function register_activation_hook() {}
function register_deactivation_hook() {}
function plugin_dir_path() { return __DIR__ . '/encompass-analytics/'; }
function plugin_dir_url() { return 'http://localhost:8000/wp-content/plugins/encompass-analytics/'; }
function current_time($type) { return date('Y-m-d H:i:s'); }
function add_option($name, $value) {
    echo "[INFO] Added option: $name = " . (is_array($value) ? print_r($value, true) : $value) . "\n";
    return true;
}
function update_option($name, $value) {
    echo "[INFO] Updated option: $name = " . (is_array($value) ? print_r($value, true) : $value) . "\n";
    return true;
}

// Mock WordPress database functions
class wpdb {
    public $prefix = 'wp_';
    
    public function get_charset_collate() {
        return 'DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci';
    }
}

// Include the plugin files
require_once __DIR__ . '/encompass-analytics/includes/class-encompass-analytics-activator.php';

// Run the activation
function test_plugin_activation() {
    global $wpdb;
    
    echo "[TEST] Starting plugin activation test...\n";
    
    // Test table creation
    echo "[TEST] Testing table creation...\n";
    Encompass_MSP_Analytics_Activator::create_tables();
    
    // Test default options
    echo "\n[TEST] Testing default options...\n";
    Encompass_MSP_Analytics_Activator::set_default_options();
    
    echo "\n[TEST] Plugin activation test completed.\n";
}

// Run the tests
$wpdb = new wpdb();
test_plugin_activation();

echo "\n=== Test Complete ===\n";
echo "1. Start the Docker environment with: docker-compose up -d\n";
echo "2. Access WordPress at: http://localhost:8000\n";
echo "3. Log in to WordPress admin (admin/password)\n";
echo "4. Activate the Encompass Analytics plugin\n";
echo "5. Check the plugin settings page to verify everything is working\n\n";
