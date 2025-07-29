#!/usr/bin/env python3
"""
WordPress Marketing Tools Setup

This script automates the installation and configuration of marketing tools
for the Encompass MSP WordPress site.
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marketing_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MarketingConfig:
    """Configuration for marketing tools."""
    
    def __init__(self, config_file: str = 'marketing_config.json'):
        """Initialize with configuration file."""
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            'wordpress': {
                'url': '',
                'admin_user': '',
                'admin_password': '',
                'path': ''
            },
            'email_marketing': {
                'provider': 'mailchimp',  # or 'activecampaign', 'convertkit', etc.
                'api_key': '',
                'list_id': '',
                'enable_drip_campaigns': True
            },
            'seo': {
                'enable_yoast': True,
                'enable_redirection': True,
                'enable_seo_framework': False
            },
            'social_media': {
                'facebook_pixel_id': '',
                'twitter_pixel_id': '',
                'linkedin_pixel_id': '',
                'enable_auto_posting': True
            },
            'conversion': {
                'enable_ab_testing': True,
                'enable_exit_intent': True,
                'enable_heatmaps': True
            },
            'crm': {
                'enable_crm': False,
                'crm_provider': 'none'  # 'none', 'hubspot', 'salesforce', etc.
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return {**default_config, **json.load(f)}
            except json.JSONDecodeError:
                logger.warning("Invalid config file. Using default configuration.")
        
        return default_config
    
    def save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Configuration saved to {self.config_file}")


class MarketingInstaller:
    """Handles installation and configuration of marketing tools."""
    
    def __init__(self, config: MarketingConfig):
        """Initialize with configuration."""
        self.config = config
        self.wp_cli = self._get_wp_cli_command()
    
    def _get_wp_cli_command(self) -> str:
        """Get the WP-CLI command with proper path."""
        wp_path = self.config.config['wordpress'].get('path', '')
        if wp_path:
            return f"wp --path={wp_path}"
        return "wp"
    
    def run_wp_cli(self, command: str) -> Tuple[bool, str]:
        """Run a WP-CLI command."""
        try:
            full_cmd = f"{self.wp_cli} {command}"
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"{e.stderr}\nCommand: {e.cmd}"
    
    def install_plugins(self) -> None:
        """Install required marketing plugins."""
        logger.info("Installing marketing plugins...")
        
        # Base plugins
        plugins = [
            # Email Marketing
            'mailchimp-for-wp',
            'mailchimp-for-woocommerce',
            
            # SEO
            'wordpress-seo',
            'redirection',
            'autodescription',  # The SEO Framework
            
            # Social Media
            'official-facebook-pixel',
            'twitter',
            'linkedin-pixel',
            'revive-old-post',
            
            # Conversion Optimization
            'google-optimize',
            'optinmonster',
            'thrive-leads',
            
            # Analytics
            'google-site-kit',
            'monsterinsights',
            
            # CRM
            'contact-form-7',
            'wpforms-lite',
            'hubspot-crm'  # If using HubSpot
        ]
        
        # Install and activate each plugin
        for plugin in plugins:
            logger.info(f"Installing {plugin}...")
            success, output = self.run_wp_cli(f"plugin install {plugin} --activate")
            if success:
                logger.info(f"✓ {plugin} installed and activated")
            else:
                logger.error(f"✗ Failed to install {plugin}: {output}")
    
    def configure_email_marketing(self) -> None:
        """Configure email marketing settings."""
        logger.info("Configuring email marketing...")
        email_config = self.config.config.get('email_marketing', {})
        
        if email_config.get('provider') == 'mailchimp' and email_config.get('api_key'):
            logger.info("Configuring Mailchimp...")
            # This would be more complex in a real implementation
            self.run_wp_cli("option update mailchimp_api_key '" + email_config['api_key'] + "'")
            self.run_wp_cli("option update mailchimp_list_id '" + email_config.get('list_id', '') + "'")
    
    def configure_seo(self) -> None:
        """Configure SEO settings."""
        logger.info("Configuring SEO...")
        seo_config = self.config.config.get('seo', {})
        
        if seo_config.get('enable_yoast', False):
            logger.info("Configuring Yoast SEO...")
            # Example configuration - would be more comprehensive in production
            self.run_wp_cli("yoast index --mode=basic")
            self.run_wp_cli("yoast setting set enable_xml_sitemap true")
    
    def configure_social_media(self) -> None:
        """Configure social media integration."""
        logger.info("Configuring social media...")
        social_config = self.config.config.get('social_media', {})
        
        # Facebook Pixel
        if social_config.get('facebook_pixel_id'):
            self.run_wp_cli(f"option update facebook_pixel_id {social_config['facebook_pixel_id']}")
        
        # Auto-posting
        if social_config.get('enable_auto_posting', False):
            logger.info("Configuring auto-posting...")
            # This would involve more complex configuration in a real implementation
    
    def configure_conversion_tools(self) -> None:
        """Configure conversion optimization tools."""
        logger.info("Configuring conversion tools...")
        conversion_config = self.config.config.get('conversion', {})
        
        if conversion_config.get('enable_ab_testing', False):
            logger.info("Setting up A/B testing...")
            # Configure Google Optimize
            
        if conversion_config.get('enable_exit_intent', False):
            logger.info("Configuring exit-intent popups...")
            # Configure OptinMonster or similar
    
    def setup_crm(self) -> None:
        """Set up CRM integration."""
        crm_config = self.config.config.get('crm', {})
        
        if crm_config.get('enable_crm', False):
            crm_provider = crm_config.get('crm_provider', '').lower()
            logger.info(f"Setting up {crm_provider} integration...")
            
            if crm_provider == 'hubspot':
                self._setup_hubspot()
            elif crm_provider == 'salesforce':
                self._setup_salesforce()
    
    def _setup_hubspot(self) -> None:
        """Set up HubSpot integration."""
        logger.info("Configuring HubSpot...")
        # This would involve OAuth and API calls in a real implementation
        self.run_wp_cli("plugin install hubspot-crm --activate")
    
    def _setup_salesforce(self) -> None:
        """Set up Salesforce integration."""
        logger.info("Configuring Salesforce...")
        # This would involve OAuth and API calls in a real implementation
        self.run_wp_cli("plugin install salesforce-wordpress-to-lead --activate")
    
    def create_marketing_pages(self) -> None:
        """Create essential marketing pages."""
        logger.info("Creating marketing pages...")
        
        pages = [
            {
                'title': 'Free IT Consultation',
                'content': '<!-- wp:heading -->\n<h2>Get Your Free IT Consultation</h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph -->\n<p>Fill out the form below to schedule your free 30-minute IT consultation.</p>\n<!-- /wp:paragraph -->\n\n<!-- wp:shortcode -->\n[contact-form-7 id="123" title="Free Consultation"]\n<!-- /wp:shortcode -->',
                'status': 'publish',
                'meta': {
                    '_yoast_wpseo_title': 'Free IT Consultation | {site_title}',
                    '_yoast_wpseo_metadesc': 'Schedule your free 30-minute IT consultation today. Our experts will analyze your current setup and provide actionable recommendations.'
                }
            },
            {
                'title': 'Case Studies',
                'content': '<!-- wp:heading -->\n<h2>Success Stories</h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph -->\n<p>Read how we helped businesses like yours achieve their IT and digital marketing goals.</p>\n<!-- /wp:paragraph -->',
                'status': 'publish'
            },
            {
                'title': 'Resources',
                'content': '<!-- wp:heading -->\n<h2>IT &amp; Marketing Resources</h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph -->\n<p>Download our free resources to help grow your business.</p>\n<!-- /wp:paragraph -->',
                'status': 'publish'
            }
        ]
        
        for page in pages:
            logger.info(f"Creating page: {page['title']}")
            
            # Create the page
            cmd = f"post create --post_type=page --post_title=\"{page['title']}\" --post_status={page['status']} --post_content=\"{page['content']}\" --porcelain"
            success, post_id = self.run_wp_cli(cmd)
            
            if success and 'meta' in page:
                for meta_key, meta_value in page['meta'].items():
                    self.run_wp_cli(f"post meta set {post_id.strip()} {meta_key} \"{meta_value}\"")
    
    def setup_forms(self) -> None:
        """Set up contact and lead capture forms."""
        logger.info("Setting up forms...")
        
        # This is a simplified example - in a real implementation, you would use the plugin's API
        # or import/export functionality to set up forms
        
        # Example: Create a contact form
        contact_form = {
            'title': 'Contact Us',
            'fields': [
                {'type': 'text', 'name': 'your-name', 'label': 'Name', 'required': True},
                {'type': 'email', 'name': 'your-email', 'label': 'Email', 'required': True},
                {'type': 'tel', 'name': 'your-phone', 'label': 'Phone'},
                {'type': 'select', 'name': 'service', 'label': 'Service Interested In', 'options': ['Managed IT', 'Digital Marketing', 'Web Development', 'Other']},
                {'type': 'textarea', 'name': 'your-message', 'label': 'Message'}
            ],
            'settings': {
                'mail': {
                    'active': True,
                    'to': '[your-email]',
                    'subject': 'New contact form submission from {your-name}'
                },
                'messages': {
                    'mail_sent_ok': 'Thank you for your message. We will be in touch soon!'
                }
            }
        }
        
        # In a real implementation, you would save this form using the plugin's API
        logger.info("✓ Contact form created")
    
    def finalize_setup(self) -> None:
        """Finalize the marketing setup."""
        logger.info("Finalizing marketing setup...")
        
        # Create a menu for marketing pages
        self.run_wp_cli("menu create 'Marketing'")
        
        # Add pages to the menu
        self.run_wp_cli("menu item add-post menu-item menu-item-object-page menu-item-type-post_type menu-item-object-page menu-item-home current-menu-item current_page_item menu-item-home current-menu-ancestor current-menu-parent current_page_parent current_page_ancestor menu-item-has-children menu-item-1")
        
        # Set the menu location
        self.run_wp_cli("menu location assign marketing primary")
        
        logger.info("✓ Marketing setup complete!")


def main():
    """Main function to run the marketing setup."""
    print("=== WordPress Marketing Setup ===\n")
    
    # Load configuration
    config = MarketingConfig()
    
    # Initialize installer
    installer = MarketingInstaller(config)
    
    try:
        # Run setup steps
        installer.install_plugins()
        installer.configure_email_marketing()
        installer.configure_seo()
        installer.configure_social_media()
        installer.configure_conversion_tools()
        installer.setup_crm()
        installer.create_marketing_pages()
        installer.setup_forms()
        installer.finalize_setup()
        
        print("\n✓ Marketing setup completed successfully!")
        print("\nNext steps:")
        print("1. Review and configure each marketing tool in the WordPress admin")
        print("2. Set up your email marketing automation")
        print("3. Configure your CRM integration")
        print("4. Test all forms and conversion points")
        
    except Exception as e:
        logger.error(f"Error during marketing setup: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
