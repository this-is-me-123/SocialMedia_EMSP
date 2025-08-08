import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# --- SQLAlchemy Base and Engine Setup ---
Base = declarative_base()

# Read DB URL from environment variable
DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://socialmedia:socialmedia@localhost:5432/socialmedia")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency generator for DB session.
    Usage (FastAPI):
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Configuration ---
# Set the POSTGRES_URL env var to your DB connection string, e.g.:
#   export POSTGRES_URL=postgresql://user:password@localhost:5432/dbname
# All DB models should inherit from Base.

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, default="Test User")
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip = Column(String, nullable=True)
    data = Column(String, nullable=True)  # Store JSON as string
