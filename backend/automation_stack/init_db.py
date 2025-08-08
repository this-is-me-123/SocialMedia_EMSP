#!/usr/bin/env python3
"""
Database initialization script for the Social Media Automation System.
Run this script to create the necessary database tables and initial data.

Required environment variables:
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT

TODO: For production-grade migrations/versioning, use Alembic.

Usage:
    python init_db.py [--dry-run]
        --dry-run   Print SQL statements but do not execute them.
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'socialmedia'),
            user=os.getenv('DB_USER', 'socialmedia'),
            password=os.getenv('DB_PASSWORD', ''),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        sys.exit(1)

def create_tables(conn, dry_run=False):
    """Create database tables if they don't exist. If dry_run, print SQL without executing."""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id SERIAL PRIMARY KEY,
            platform VARCHAR(50) NOT NULL,
            content_path TEXT NOT NULL,
            caption TEXT,
            scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
            status VARCHAR(20) DEFAULT 'scheduled',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB,
            error_message TEXT
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_scheduled_posts_platform ON scheduled_posts(platform);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_scheduled_posts_time ON scheduled_posts(scheduled_time);
        """,
        """
        CREATE TABLE IF NOT EXISTS platform_credentials (
            platform VARCHAR(50) PRIMARY KEY,
            access_token TEXT,
            refresh_token TEXT,
            expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    if dry_run:
        print("-- DRY RUN: The following SQL statements would be executed:")
        for sql in tables:
            print(sql.strip())
        return
    for sql in tables:
        with conn.cursor() as cur:
            cur.execute(sql)
    logger.info("Successfully created/verified tables")

def main():
    """Main function to initialize the database."""
    import argparse
    parser = argparse.ArgumentParser(description="Initialize the Social Media Automation database.")
    parser.add_argument('--dry-run', action='store_true', help='Print SQL statements but do not execute them.')
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    conn = None
    try:
        if not args.dry_run:
            conn = get_db_connection()
        create_tables(conn, dry_run=args.dry_run)
        if not args.dry_run:
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
