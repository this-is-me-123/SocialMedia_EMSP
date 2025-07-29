#!/usr/bin/env python3
"""
Deployment verification script for the Social Media Automation System.
Runs a series of tests to verify the system is properly deployed.
"""
import sys
import json
import requests
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import psycopg2
import redis
from dotenv import load_dotenv
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deployment_verification.log')
    ]
)
logger = logging.getLogger(__name__)

class DeploymentVerifier:
    """Verifies the deployment of the Social Media Automation System."""
    
    def __init__(self):
        """Initialize the verifier with configuration."""
        load_dotenv()
        self.config = self.load_config()
        self.failures = 0
        self.successes = 0
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            'health_check': {
                'url': os.getenv('HEALTH_CHECK_URL', 'http://localhost:8000/health'),
                'timeout': int(os.getenv('HEALTH_CHECK_TIMEOUT', '5'))
            },
            'database': {
                'dbname': os.getenv('DB_NAME', 'socialmedia'),
                'user': os.getenv('DB_USER', 'socialmedia'),
                'password': os.getenv('DB_PASSWORD', ''),
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432')
            },
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', '6379')),
                'db': int(os.getenv('REDIS_DB', '0')),
                'password': os.getenv('REDIS_PASSWORD', '')
            },
            'storage': {
                'path': Path(os.getenv('STORAGE_PATH', './data')),
                'required_dirs': ['media', 'uploads', 'config']
            },
            'services': {
                'required_ports': [8000, 5432, 6379],
                'required_processes': ['postgres', 'redis-server']
            }
        }
    
    def run_checks(self) -> bool:
        """Run all verification checks."""
        logger.info("Starting deployment verification...")
        
        # Run all checks
        checks = [
            ("Filesystem Permissions", self.check_filesystem_permissions),
            ("Health Check Endpoint", self.check_health_endpoint),
            ("Database Connection", self.check_database_connection),
            ("Database Schema", self.check_database_schema),
            ("Redis Connection", self.check_redis_connection),
            ("Required Services", self.check_required_services),
            ("Storage Directories", self.check_storage_directories)
        ]
        
        results = []
        for name, check in checks:
            success, message = check()
            results.append({
                'check': name,
                'status': 'PASS' if success else 'FAIL',
                'message': message
            })
            
            if success:
                self.successes += 1
                logger.info(f"✓ {name}: {message}")
            else:
                self.failures += 1
                logger.error(f"✗ {name}: {message}")
        
        # Print summary
        self.print_summary(results)
        
        return self.failures == 0
    
    def check_filesystem_permissions(self) -> tuple[bool, str]:
        """Verify filesystem permissions."""
        required_paths = [
            self.config['storage']['path'],
            Path('/var/log/socialmedia'),
            Path('/var/backups/socialmedia')
        ]
        
        for path in required_paths:
            if not path.exists():
                return False, f"Required path does not exist: {path}"
            if not os.access(path, os.W_OK):
                return False, f"No write permission for: {path}"
            if not os.access(path, os.R_OK):
                return False, f"No read permission for: {path}"
        
        return True, "All required paths are accessible"
    
    def check_health_endpoint(self) -> tuple[bool, str]:
        """Verify health check endpoint is responding."""
        try:
            response = requests.get(
                self.config['health_check']['url'],
                timeout=self.config['health_check']['timeout']
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    return True, "Health check passed"
                return False, f"Health check failed: {data}"
            return False, f"Unexpected status code: {response.status_code}"
        except Exception as e:
            return False, f"Health check error: {str(e)}"
    
    def check_database_connection(self) -> tuple[bool, str]:
        """Verify database connection."""
        try:
            conn = psycopg2.connect(**self.config['database'])
            conn.close()
            return True, "Database connection successful"
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    def check_database_schema(self) -> tuple[bool, str]:
        """Verify database schema."""
        required_tables = ['scheduled_posts', 'platform_credentials']
        
        try:
            conn = psycopg2.connect(**self.config['database'])
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                existing_tables = {row[0] for row in cur.fetchall()}
                
                missing_tables = [t for t in required_tables if t not in existing_tables]
                if missing_tables:
                    return False, f"Missing tables: {', '.join(missing_tables)}
                
                return True, "All required tables exist"
        except Exception as e:
            return False, f"Schema check failed: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()
    
    def check_redis_connection(self) -> tuple[bool, str]:
        """Verify Redis connection."""
        try:
            r = redis.Redis(**self.config['redis'])
            if r.ping():
                return True, "Redis connection successful"
            return False, "Redis ping failed"
        except Exception as e:
            return False, f"Redis connection failed: {str(e)}"
    
    def check_required_services(self) -> tuple[bool, str]:
        """Verify required services are running."""
        try:
            import psutil
            
            running_services = []
            for proc in psutil.process_iter(['name']):
                try:
                    running_services.append(proc.info['name'].lower())
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            missing_services = [
                svc for svc in self.config['services']['required_processes']
                if svc not in running_services
            ]
            
            if missing_services:
                return False, f"Missing services: {', '.join(missing_services)}
            return True, "All required services are running"
        except ImportError:
            return False, "psutil module not available"
        except Exception as e:
            return False, f"Service check failed: {str(e)}"
    
    def check_storage_directories(self) -> tuple[bool, str]:
        """Verify required storage directories exist."""
        missing_dirs = []
        
        for dir_name in self.config['storage']['required_dirs']:
            dir_path = self.config['storage']['path'] / dir_name
            if not dir_path.exists() or not dir_path.is_dir():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return False, f"Missing directories: {', '.join(missing_dirs)}
        return True, "All required directories exist"
    
    def print_summary(self, results: List[Dict[str, str]]) -> None:
        """Print verification summary."""
        print("\n" + "="*50)
        print("DEPLOYMENT VERIFICATION SUMMARY")
        print("="*50)
        
        for result in results:
            status = "✓" if result['status'] == 'PASS' else "✗"
            print(f"{status} {result['check']}: {result['message']}")
        
        print("\n" + "="*50)
        print(f"TOTAL: {self.successes} PASSED, {self.failures} FAILED"
        print("="*50 + "\n")
        
        if self.failures > 0:
            print("❌ Some checks failed. Please review the errors above.")
            sys.exit(1)
        else:
            print("✅ All checks passed successfully!")

def main():
    """Main entry point."""
    verifier = DeploymentVerifier()
    success = verifier.run_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
