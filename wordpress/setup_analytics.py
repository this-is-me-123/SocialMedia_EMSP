#!/usr/bin/env python3
"""
WordPress Analytics Setup Script

This script automates the installation and configuration of analytics plugins
and settings for the Encompass MSP WordPress site.
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from requests.auth import HTTPBasicAuth

class WordPressConfig:
    """Configuration for WordPress site."""
    
    def __init__(self, wp_url: str, wp_user: str, wp_password: str, wp_path: str = None):
        """Initialize WordPress configuration."""
        self.wp_url = wp_url.rstrip('/')
        self.wp_user = wp_user
        self.wp_password = wp_password
        self.wp_path = wp_path or os.getcwd()
        self.rest_url = f"{self.wp_url}/wp-json/wp/v2"
        
        # Verify WordPress installation
        if not self.verify_wp_installation():
            print("Error: Could not connect to WordPress. Please check the URL and credentials.")
            sys.exit(1)
    
    def verify_wp_installation(self) -> bool:
        """Verify WordPress installation and credentials."""
        try:
            response = requests.get(
                f"{self.rest_url}/settings",
                auth=HTTPBasicAuth(self.wp_user, self.wp_password)
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def run_wp_cli(self, command: str) -> Tuple[bool, str]:
        """Run a WP-CLI command."""
        try:
            cmd = ["wp", "--path=\"" + self.wp_path + "\""] + command.split()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e.stderr}"


class AnalyticsInstaller:
    """Handles installation and configuration of analytics tools."""
    
    REQUIRED_PLUGINS = [
        "google-site-kit",
        "monsterinsights",
        "wordpress-seo",
        "wp-mail-smtp",
        "hotjar"
    ]
    
    def __init__(self, wp_config: WordPressConfig):
        """Initialize with WordPress configuration."""
        self.wp = wp_config
        self.plugins_installed = []
        self.plugins_activated = []
    
    def install_required_plugins(self) -> None:
        """Install required WordPress plugins."""
        print("\n=== Installing Required Plugins ===")
        
        # Get list of installed plugins
        success, output = self.wp.run_wp_cli("plugin list --format=json")
        if not success:
            print(f"Error getting plugin list: {output}")
            return
        
        installed_plugins = {p['name']: p for p in json.loads(output)}
        
        # Install and activate each required plugin
        for plugin_slug in self.REQUIRED_PLUGINS:
            if plugin_slug in installed_plugins:
                print(f"- {plugin_slug} is already installed")
                self.plugins_installed.append(plugin_slug)
                
                # Check if plugin is active
                if installed_plugins[plugin_slug]['status'] != 'active':
                    self.activate_plugin(plugin_slug)
                else:
                    self.plugins_activated.append(plugin_slug)
                    print(f"  ✓ {plugin_slug} is already active")
            else:
                self.install_plugin(plugin_slug)
    
    def install_plugin(self, plugin_slug: str) -> None:
        """Install a WordPress plugin."""
        print(f"- Installing {plugin_slug}...")
        success, output = self.wp.run_wp_cli(f"plugin install {plugin_slug} --activate")
        
        if success:
            print(f"  ✓ {plugin_slug} installed and activated")
            self.plugins_installed.append(plugin_slug)
            self.plugins_activated.append(plugin_slug)
        else:
            print(f"  ✗ Failed to install {plugin_slug}: {output}")
    
    def activate_plugin(self, plugin_slug: str) -> None:
        """Activate a WordPress plugin."""
        print(f"- Activating {plugin_slug}...")
        success, output = self.wp.run_wp_cli(f"plugin activate {plugin_slug}")
        
        if success:
            print(f"  ✓ {plugin_slug} activated")
            self.plugins_activated.append(plugin_slug)
        else:
            print(f"  ✗ Failed to activate {plugin_slug}: {output}")
    
    def configure_google_site_kit(self, ga4_property_id: str) -> None:
        """Configure Google Site Kit with GA4 property."""
        print("\n=== Configuring Google Site Kit ===")
        
        if "google-site-kit" not in self.plugins_activated:
            print("Google Site Kit is not activated. Please activate it first.")
            return
        
        # Note: This is a simplified example. Actual implementation would require
        # OAuth authentication with Google and proper API calls.
        print("Please complete the Google Site Kit setup in the WordPress admin:")
        print(f"1. Go to {self.wp.wp_url}/wp-admin/admin.php?page=googlesitekit-splash")
        print("2. Sign in with your Google account")
        print("3. Follow the setup wizard")
        print(f"4. When prompted, enter your GA4 Property ID: {ga4_property_id}")
    
    def configure_yoast_seo(self, site_name: str, site_description: str) -> None:
        """Configure Yoast SEO plugin."""
        print("\n=== Configuring Yoast SEO ===")
        
        if "wordpress-seo" not in self.plugins_activated:
            print("Yoast SEO is not activated. Please activate it first.")
            return
        
        # Set site title and description
        self.wp.run_wp_cli(f"option update blogname '{site_name}'")
        self.wp.run_wp_cli(f"option update blogdescription '{site_description}'")
        
        # Enable XML sitemaps
        self.wp.run_wp_cli("option update wpseo_xml '1'")
        
        # Disable author and search results sitemaps
        self.wp.run_wp_cli("option update wpseo_titles 'noindex-author-wpseo' '1'")
        self.wp.run_wp_cli("option update wpseo_titles 'noindex-search' '1'")
        
        print("✓ Basic SEO settings configured")
    
    def configure_hotjar(self, site_id: str) -> None:
        """Configure Hotjar tracking."""
        print("\n=== Configuring Hotjar ===")
        
        if "hotjar" not in self.plugins_activated:
            print("Hotjar plugin is not activated. Please activate it first.")
            return
        
        # Configure Hotjar site ID
        self.wp.run_wp_cli(f"option update hotjar_site_id '{site_id}'")
        self.wp.run_wp_cli("option update hotjar_snippet_version '6'")
        
        print(f"✓ Hotjar configured with Site ID: {site_id}")


def main():
    """Main function to run the analytics setup."""
    print("=== WordPress Analytics Setup ===\n")
    
    # Get WordPress credentials
    wp_url = input("Enter WordPress site URL (e.g., https://www.encompass-msp.com): ").strip()
    wp_user = input("Enter WordPress admin username: ").strip()
    wp_password = input("Enter WordPress admin password: ").strip()
    wp_path = input("Enter WordPress installation path (press Enter to use current directory): ").strip()
    
    # Initialize WordPress configuration
    try:
        wp_config = WordPressConfig(wp_url, wp_user, wp_password, wp_path or None)
        print("✓ Connected to WordPress successfully")
    except Exception as e:
        print(f"Error connecting to WordPress: {e}")
        sys.exit(1)
    
    # Initialize analytics installer
    installer = AnalyticsInstaller(wp_config)
    
    # Install and activate plugins
    installer.install_required_plugins()
    
    # Get GA4 property ID
    ga4_property_id = input("\nEnter your GA4 Property ID (starts with 'G-'): ").strip()
    if ga4_property_id:
        installer.configure_google_site_kit(ga4_property_id)
    
    # Configure SEO
    site_name = input("\nEnter site name for SEO (press Enter to skip): ").strip()
    site_description = input("Enter site description for SEO (press Enter to skip): ").strip()
    if site_name or site_description:
        installer.configure_yoast_seo(site_name, site_description)
    
    # Configure Hotjar
    hotjar_id = input("\nEnter Hotjar Site ID (press Enter to skip): ").strip()
    if hotjar_id:
        installer.configure_hotjar(hotjar_id)
    
    print("\n=== Setup Complete ===")
    print("\nNext steps:")
    print("1. Complete the Google Site Kit setup in the WordPress admin")
    print("2. Verify tracking is working using Google Tag Assistant")
    print("3. Set up custom events and goals in Google Analytics")
    print("4. Configure additional settings in the WordPress admin as needed")


if __name__ == "__main__":
    main()
