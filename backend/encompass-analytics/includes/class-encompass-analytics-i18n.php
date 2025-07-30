<?php
/**
 * Define the internationalization functionality.
 */
class Encompass_MSP_Analytics_i18n {
    public function load_plugin_textdomain(): void {
        load_plugin_textdomain(
            'encompass-analytics',
            false,
            dirname(dirname(plugin_basename(__FILE__))) . '/languages/'
        );
    }
}
