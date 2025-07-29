#!/usr/bin/env python3
"""
Rollback utility for the Social Media Automation System.
Handles rolling back to previous versions in case of deployment issues.
"""
import os
import sys
import shutil
import logging
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rollback.log')
    ]
)
logger = logging.getLogger(__name__)

class RollbackManager:
    """Manages rollback operations for the application."""
    
    def __init__(self, backup_dir: str = '/var/backups/socialmedia'):
        """Initialize with backup directory."""
        load_dotenv()
        self.backup_dir = Path(backup_dir)
        self.app_dir = Path('/opt/socialmedia')
        self.config = self.load_config()
        self.rollback_dir = self.backup_dir / 'rollback'
        self.rollback_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            'database': {
                'dbname': os.getenv('DB_NAME', 'socialmedia'),
                'user': os.getenv('DB_USER', 'socialmedia'),
                'password': os.getenv('DB_PASSWORD', ''),
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432')
            },
            'services': ['socialmedia', 'socialmedia-scheduler', 'socialmedia-health']
        }
    
    def list_backups(self) -> List[Tuple[Path, datetime]]:
        """List available backups with timestamps."""
        backups = []
        for item in sorted(self.backup_dir.iterdir(), reverse=True):
            if not item.is_dir() or item.name == 'rollback':
                continue
            try:
                dt = datetime.strptime(item.name, '%Y%m%d_%H%M%S')
                backups.append((item, dt))
            except ValueError:
                continue
        return backups
    
    def create_backup(self) -> bool:
        """Create a backup of current state before rollback."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'pre_rollback_{timestamp}'
        backup_path = self.rollback_dir / backup_name
        
        try:
            # Create backup directory
            (backup_path / 'code').mkdir(parents=True, exist_ok=True)
            (backup_path / 'database').mkdir(exist_ok=True)
            
            logger.info("Backing up current code...")
            # Copy application code
            subprocess.run([
                'rsync', '-a',
                '--exclude=venv',
                '--exclude=__pycache__',
                '--exclude=*.pyc',
                f"{self.app_dir}/",
                f"{backup_path}/code/"
            ], check=True)
            
            logger.info("Backing up database...")
            # Backup database
            db_backup = backup_path / 'database' / 'backup.sql'
            with open(db_backup, 'w') as f:
                subprocess.run([
                    'pg_dump',
                    '-h', self.config['database']['host'],
                    '-U', self.config['database']['user'],
                    '-d', self.config['database']['dbname'],
                    '-f', str(db_backup)
                ], check=True, env={
                    'PGPASSWORD': self.config['database']['password']
                })
            
            logger.info(f"Pre-rollback backup created at {backup_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during backup: {e}")
            return False
    
    def stop_services(self) -> bool:
        """Stop application services."""
        try:
            for service in self.config['services']:
                logger.info(f"Stopping {service}...")
                subprocess.run(['systemctl', 'stop', service], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop services: {e}")
            return False
    
    def start_services(self) -> bool:
        """Start application services."""
        try:
            for service in reversed(self.config['services']):
                logger.info(f"Starting {service}...")
                subprocess.run(['systemctl', 'start', service], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start services: {e}")
            return False
    
    def rollback_code(self, backup_path: Path) -> bool:
        """Roll back the application code."""
        try:
            # Backup current code
            self.create_backup()
            
            # Restore from backup
            logger.info("Rolling back code...")
            subprocess.run([
                'rsync', '-a', '--delete',
                f"{backup_path}/code/",
                f"{self.app_dir}/"
            ], check=True)
            
            # Fix permissions
            subprocess.run(['chown', '-R', 'socialmedia:socialmedia', str(self.app_dir)], check=True)
            
            # Reinstall dependencies if needed
            if (self.app_dir / 'requirements.txt').exists():
                logger.info("Reinstalling dependencies...")
                subprocess.run(
                    ['/opt/socialmedia/venv/bin/pip', 'install', '-r', 'requirements.txt'],
                    cwd=self.app_dir,
                    check=True
                )
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Code rollback failed: {e}")
            return False
    
    def rollback_database(self, backup_path: Path) -> bool:
        """Roll back the database."""
        db_backup = backup_path / 'database' / 'backup.sql'
        if not db_backup.exists():
            logger.warning(f"No database backup found at {db_backup}")
            return False
            
        try:
            logger.info("Rolling back database...")
            with open(db_backup, 'r') as f:
                subprocess.run([
                    'psql',
                    '-h', self.config['database']['host'],
                    '-U', self.config['database']['user'],
                    '-d', self.config['database']['dbname']
                ], stdin=f, check=True, env={
                    'PGPASSWORD': self.config['database']['password']
                })
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Database rollback failed: {e}")
            return False
    
    def rollback(self, backup_name: Optional[str] = None) -> bool:
        """Perform rollback to a specific backup or the latest."""
        try:
            if backup_name:
                backup_path = self.backup_dir / backup_name
                if not backup_path.exists():
                    logger.error(f"Backup not found: {backup_path}")
                    return False
            else:
                # Use latest backup
                backups = self.list_backups()
                if not backups:
                    logger.error("No backups available for rollback")
                    return False
                backup_path = backups[0][0]
            
            logger.info(f"Initiating rollback to {backup_path.name}")
            
            # Stop services
            if not self.stop_services():
                logger.error("Failed to stop services, aborting rollback")
                return False
            
            # Perform rollback
            success = True
            if not self.rollback_code(backup_path):
                logger.error("Code rollback failed")
                success = False
            
            if not self.rollback_database(backup_path):
                logger.error("Database rollback failed")
                success = False
            
            # Start services
            if not self.start_services():
                logger.error("Failed to start services after rollback")
                success = False
            
            if success:
                logger.info(f"Rollback to {backup_path.name} completed successfully")
            else:
                logger.warning("Rollback completed with errors")
            
            return success
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Rollback utility for Social Media Automation System')
    parser.add_argument('backup', nargs='?', help='Name of the backup to rollback to (optional)')
    parser.add_argument('--list', action='store_true', help='List available backups')
    
    args = parser.parse_args()
    
    try:
        manager = RollbackManager()
        
        if args.list:
            print("\nAvailable backups:")
            print("-" * 50)
            for backup, dt in manager.list_backups():
                print(f"{backup.name} - {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            return 0
            
        if manager.rollback(args.backup):
            return 0
        return 1
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
