"""Unit tests for backup and restore functionality."""
import unittest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts.backup_restore import BackupManager

class TestBackupRestore(unittest.TestCase):
    """Test backup and restore operations."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = os.path.join(self.test_dir, 'backups')
        self.data_dir = os.path.join(self.test_dir, 'data')
        
        # Create test files
        os.makedirs(os.path.join(self.data_dir, 'config'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'media'), exist_ok=True)
        
        with open(os.path.join(self.data_dir, 'config', 'settings.json'), 'w') as f:
            f.write('{"test": "data"}')
            
        # Initialize backup manager
        self.manager = BackupManager()
        self.manager.backup_dir = Path(self.backup_dir)
        self.manager.config = {
            'storage': {
                'path': self.data_dir,
                'include': ['config', 'media'],
                'exclude': ['*.tmp']
            }
        }
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('psycopg2.connect')
    def test_backup_database(self, mock_connect):
        """Test database backup creation."""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Call the method
        backup_file = self.manager.backup_database()
        
        # Verify the backup file was created
        self.assertTrue(backup_file.exists())
        self.assertGreater(backup_file.stat().st_size, 0)
    
    def test_backup_files(self):
        """Test file backup creation."""
        # Call the method
        backed_up = self.manager.backup_files()
        
        # Verify files were backed up
        self.assertGreater(len(backed_up), 0)
        for file_path in backed_up:
            self.assertTrue(file_path.exists())
    
    @patch('boto3.client')
    def test_upload_to_s3(self, mock_boto):
        """Test S3 upload functionality."""
        # Configure test
        test_file = Path(self.test_dir) / 'test.txt'
        test_file.write_text('test content')
        
        # Mock S3 client
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        # Configure manager for S3
        self.manager.config['backup'] = {
            's3_bucket': 'test-bucket',
            's3_prefix': 'backups'
        }
        
        # Call the method
        result = self.manager.upload_to_s3(test_file)
        
        # Verify S3 upload was called
        self.assertTrue(result)
        mock_s3.upload_file.assert_called_once()
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backups."""
        # Create test backup directories
        old_backup = os.path.join(self.backup_dir, '20230101_000000')
        new_backup = os.path.join(self.backup_dir, '20230102_120000')
        
        os.makedirs(old_backup)
        os.makedirs(new_backup)
        
        # Set retention to 1 day
        self.manager.config['backup'] = {'retention_days': 1}
        
        # Mock current time to be after the old backup
        with patch('time.time', return_value=1672646400):  # 2023-01-03 00:00:00
            self.manager.cleanup_old_backups()
        
        # Verify old backup was removed
        self.assertFalse(os.path.exists(old_backup))
        self.assertTrue(os.path.exists(new_backup))

if __name__ == "__main__":
    unittest.main()
