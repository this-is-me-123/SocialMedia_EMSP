#!/usr/bin/env python3
"""
Database initialization script for the Social Media Automation System.
Run this script to create the necessary database tables and initial data.
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

def create_tables(conn):
    """Create database tables if they don't exist."""
    tables = ["""
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
    """, """
    CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status);
    """, """
    CREATE INDEX IF NOT EXISTS idx_scheduled_posts_platform ON scheduled_posts(platform);
    """, """
    CREATE INDEX IF NOT EXISTS idx_scheduled_posts_time ON scheduled_posts(scheduled_time);
    """, """
    CREATE TABLE IF NOT EXISTS platform_credentials (
        platform VARCHAR(50) PRIMARY KEY,
        access_token TEXT,
        refresh_token TEXT,
        token_expiry TIMESTAMP WITH TIME ZONE,
        is_active BOOLEAN DEFAULT true,
        last_used TIMESTAMP WITH TIME ZONE,
        metadata JSONB
    );
    """]
    
    with conn.cursor() as cur:
        for table in tables:
            try:
                cur.execute(table)
                logger.info("Successfully created/verified tables")
            except Exception as e:
                logger.error(f"Error creating tables: {e}")
                conn.rollback()
                raise

def main():
    """Main function to initialize the database."""
    # Load environment variables
    load_dotenv()
    
    logger.info("Starting database initialization...")
    
    try:
        # Connect to the database
        conn = get_db_connection()
        logger.info("Connected to the database")
        
        # Create tables
        create_tables(conn)
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
