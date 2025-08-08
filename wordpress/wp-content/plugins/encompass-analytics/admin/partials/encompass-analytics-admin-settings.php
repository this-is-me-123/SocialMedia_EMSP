<div class="wrap">
    <h2><?php esc_html_e('Encompass Analytics Admin Settings', 'encompass-analytics'); ?></h2>
    <form method="post" action="options.php">
        <?php
        settings_fields('encompass_analytics_general');
        do_settings_sections('encompass_analytics_general');
        submit_button();
        ?>
    </form>
    <form method="post" action="options.php">
        <?php
        settings_fields('encompass_analytics_events');
        do_settings_sections('encompass_analytics_events');
        submit_button();
        ?>
    </form>
    <form method="post" action="options.php">
        <?php
        settings_fields('encompass_analytics_advanced');
        do_settings_sections('encompass_analytics_advanced');
        submit_button();
        ?>
    </form>
</div>
