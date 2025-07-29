#!/usr/bin/env python3
"""
Backup and restore utility for the Social Media Automation System.
Handles database backups, media files, and configuration.
"""
import os
import sys
import time
import logging
import shutil
import gzip
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backup_restore.log')
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    """Handles backup and restore operations for the application."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with configuration."""
        self.config = config or self.load_config()
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = Path(self.config.get('backup_dir', 'backups')) / self.timestamp
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Load configuration from environment variables."""
        load_dotenv()
        
        return {
            'database': {
                'dbname': os.getenv('DB_NAME', 'socialmedia'),
                'user': os.getenv('DB_USER', 'socialmedia'),
                'password': os.getenv('DB_PASSWORD', ''),
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432')
            },
            'storage': {
                'path': os.getenv('STORAGE_PATH', './data'),
                'include': ['media', 'uploads', 'config'],
                'exclude': ['*.tmp', '*.log', '*.pyc', '__pycache__']
            },
            'backup': {
                'local_dir': os.getenv('BACKUP_LOCAL_DIR', './backups'),
                'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
                's3_bucket': os.getenv('BACKUP_S3_BUCKET', ''),
                's3_prefix': os.getenv('BACKUP_S3_PREFIX', 'socialmedia/backups')
            }
        }
    
    def get_db_connection(self):
        """Create a database connection."""
        try:
            conn = psycopg2.connect(**self.config['database'])
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def backup_database(self) -> Path:
        """Create a database backup."""
        logger.info("Starting database backup...")
        backup_file = self.backup_dir / 'database.sql.gz'
        
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
                    cur.copy_expert(
                        "COPY (SELECT * FROM scheduled_posts) TO STDOUT WITH CSV HEADER",
                        f
                    )
            logger.info(f"Database backup created: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()
    
    def restore_database(self, backup_file: Path) -> bool:
        """Restore database from backup."""
        logger.info(f"Starting database restore from {backup_file}...")
        
        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_file}")
            return False
        
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                # Truncate existing data
                cur.execute("TRUNCATE TABLE scheduled_posts CASCADE")
                
                # Restore data
                with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                    cur.copy_expert(
                        "COPY scheduled_posts FROM STDIN WITH CSV HEADER",
                        f
                    )
            logger.info("Database restore completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def backup_files(self) -> List[Path]:
        """Backup important files and directories."""
        logger.info("Starting file backup...")
        backed_up = []
        
        for item in self.config['storage']['include']:
            src = Path(self.config['storage']['path']) / item
            if not src.exists():
                logger.warning(f"Source not found, skipping: {src}")
                continue
                
            dst = self.backup_dir / 'files' / item
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                if src.is_file():
                    shutil.copy2(src, dst)
                else:
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                backed_up.append(dst)
                logger.info(f"Backed up: {src} -> {dst}")
            except Exception as e:
                logger.error(f"Failed to backup {src}: {e}")
        
        return backed_up
    
    def restore_files(self, backup_dir: Path) -> bool:
        """Restore files from backup."""
        logger.info(f"Starting file restore from {backup_dir}...")
        
        if not backup_dir.exists():
            logger.error(f"Backup directory not found: {backup_dir}")
            return False
        
        try:
            src_dir = backup_dir / 'files'
            if not src_dir.exists():
                logger.error(f"No files directory found in backup: {backup_dir}")
                return False
            
            for item in src_dir.iterdir():
                dst = Path(self.config['storage']['path']) / item.name
                if dst.exists():
                    if dst.is_file():
                        dst.unlink()
                    else:
                        shutil.rmtree(dst)
                
                shutil.move(str(item), str(dst))
                logger.info(f"Restored: {item} -> {dst}")
            
            return True
        except Exception as e:
            logger.error(f"File restore failed: {e}")
            return False
    
    def upload_to_s3(self, local_path: Path) -> bool:
        """Upload backup to S3."""
        if not self.config['backup']['s3_bucket']:
            logger.info("S3 backup not configured, skipping upload")
            return False
        
        try:
            s3 = boto3.client('s3')
            s3_path = f"{self.config['backup']['s3_prefix']}/{self.timestamp}/{local_path.name}"
            
            logger.info(f"Uploading to S3: s3://{self.config['backup']['s3_bucket']}/{s3_path}")
            
            if local_path.is_file():
                s3.upload_file(
                    str(local_path),
                    self.config['backup']['s3_bucket'],
                    s3_path
                )
            else:
                for root, _, files in os.walk(local_path):
                    for file in files:
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(local_path)
                        s3.upload_file(
                            str(file_path),
                            self.config['backup']['s3_bucket'],
                            f"{s3_path}/{rel_path}"
                        )
            
            logger.info("S3 upload completed successfully")
            return True
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove old backup directories."""
        backup_root = Path(self.config['backup']['local_dir'])
        if not backup_root.exists():
            return
        
        now = time.time()
        cutoff = now - (self.config['backup']['retention_days'] * 86400)
        
        for item in backup_root.iterdir():
            if not item.is_dir():
                continue
                
            try:
                # Try to parse timestamp from directory name
                dir_time = time.mktime(time.strptime(item.name, '%Y%m%d_%H%M%S'))
                if dir_time < cutoff:
                    logger.info(f"Removing old backup: {item}")
                    shutil.rmtree(item)
            except (ValueError, OSError):
                continue
    
    def create_backup(self, upload_to_s3: bool = False) -> bool:
        """Create a complete backup."""
        try:
            # Create backup directory
            (self.backup_dir / 'files').mkdir(parents=True, exist_ok=True)
            
            # Backup database
            db_backup = self.backup_database()
            
            # Backup files
            file_backups = self.backup_files()
            
            # Create metadata
            metadata = {
                'timestamp': self.timestamp,
                'database': str(db_backup.relative_to(self.backup_dir)),
                'files': [str(f.relative_to(self.backup_dir)) for f in file_backups],
                'config': {
                    'database': {
                        'dbname': self.config['database']['dbname'],
                        'host': self.config['database']['host'],
                        'port': self.config['database']['port']
                    },
                    'storage_path': self.config['storage']['path']
                }
            }
            
            with open(self.backup_dir / 'backup_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Clean up old backups
            self.cleanup_old_backups()
            
            # Upload to S3 if configured
            if upload_to_s3 and self.config['backup']['s3_bucket']:
                self.upload_to_s3(self.backup_dir)
            
            logger.info(f"Backup completed successfully: {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def restore_backup(self, backup_path: Path, upload_to_s3: bool = False) -> bool:
        """Restore from a backup."""
        try:
            # Check if this is an S3 backup
            if str(backup_path).startswith('s3://'):
                if not self.download_from_s3(backup_path):
                    return False
                # Update backup_path to local download location
                backup_path = self.backup_dir / backup_path.name
            
            # Check if this is a directory containing a backup
            if backup_path.is_dir():
                metadata_file = backup_path / 'backup_metadata.json'
                if not metadata_file.exists():
                    logger.error(f"No backup metadata found in {backup_path}")
                    return False
                
                with open(metadata_file) as f:
                    metadata = json.load(f)
                
                # Restore database
                db_backup = backup_path / metadata['database']
                if not self.restore_database(db_backup):
                    return False
                
                # Restore files
                if not self.restore_files(backup_path):
                    return False
                
                logger.info("Restore completed successfully")
                return True
            
            logger.error(f"Invalid backup path: {backup_path}")
            return False
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

def main():
    """Main entry point for the backup/restore script."""
    parser = argparse.ArgumentParser(description='Backup and restore utility')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a backup')
    backup_parser.add_argument('--s3', action='store_true', help='Upload to S3')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_path', help='Path to backup directory or S3 URI')
    restore_parser.add_argument('--s3', action='store_true', help='Download from S3')
    
    args = parser.parse_args()
    
    try:
        manager = BackupManager()
        
        if args.command == 'backup':
            success = manager.create_backup(upload_to_s3=args.s3)
            sys.exit(0 if success else 1)
            
        elif args.command == 'restore':
            backup_path = Path(args.backup_path)
            success = manager.restore_backup(backup_path, upload_to_s3=args.s3)
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
