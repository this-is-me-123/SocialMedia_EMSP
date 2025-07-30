<?php
/**
 * The core plugin class.
 */
class Encompass_MSP_Analytics {
    protected $loader;
    protected $plugin_name;
    protected $version;

    public function __construct() {
        $this->plugin_name = 'encompass-analytics';
        $this->version = ENCOMPASS_ANALYTICS_VERSION;
        $this->load_dependencies();
        $this->set_locale();
        $this->define_admin_hooks();
        $this->define_public_hooks();
        $this->define_rest_api();
    }

    private function load_dependencies() {
        require_once plugin_dir_path(dirname(__FILE__)) . 'includes/class-encompass-analytics-loader.php';
        require_once plugin_dir_path(dirname(__FILE__)) . 'includes/class-encompass-analytics-i18n.php';
        require_once plugin_dir_path(dirname(__FILE__)) . 'admin/class-encompass-analytics-admin.php';
        require_once plugin_dir_path(dirname(__FILE__)) . 'public/class-encompass-analytics-public.php';
        require_once plugin_dir_path(dirname(__FILE__)) . 'includes/class-encompass-rest-api.php';
        
        $this->loader = new Encompass_MSP_Analytics_Loader();
    }

    private function set_locale() {
        $plugin_i18n = new Encompass_MSP_Analytics_i18n();
        $this->loader->add_action('plugins_loaded', $plugin_i18n, 'load_plugin_textdomain');
    }

    private function define_admin_hooks() {
        $plugin_admin = new Encompass_MSP_Analytics_Admin($this->get_plugin_name(), $this->get_version());
        
        $this->loader->add_action('admin_enqueue_scripts', $plugin_admin, 'enqueue_styles');
        $this->loader->add_action('admin_enqueue_scripts', $plugin_admin, 'enqueue_scripts');
        $this->loader->add_action('admin_menu', $plugin_admin, 'add_plugin_admin_menu');
        $this->loader->add_action('admin_init', $plugin_admin, 'register_settings');
        
        // Add settings link to plugins page
        $plugin_basename = plugin_basename(plugin_dir_path(dirname(__FILE__)) . $this->plugin_name . '.php');
        $this->loader->add_filter('plugin_action_links_' . $plugin_basename, $plugin_admin, 'add_action_links');
    }

    private function define_public_hooks() {
        $plugin_public = new Encompass_MSP_Analytics_Public($this->get_plugin_name(), $this->get_version());
        
        $this->loader->add_action('wp_enqueue_scripts', $plugin_public, 'enqueue_styles');
        $this->loader->add_action('wp_enqueue_scripts', $plugin_public, 'enqueue_scripts');
        
        // Add tracking code to footer
        $this->loader->add_action('wp_footer', $plugin_public, 'add_tracking_code');
    }
    
    private function define_rest_api() {
        $plugin_rest = new Encompass_MSP_REST_API();
        $this->loader->add_action('rest_api_init', $plugin_rest, 'register_routes');
    }

    public function run(): void {
        $this->loader->run();
    }

    public function get_plugin_name(): string {
        return $this->plugin_name;
    }

    public function get_loader() {
        return $this->loader;
    }

    public function get_version(): string {
        return $this->version;
    }
}
