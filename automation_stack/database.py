from sqlalchemy.orm import declarative_base

Base = declarative_base()

def get_db():
    """Placeholder get_db generator for dependency injection."""
    db = None
    try:
        yield db
    finally:
        if db:
            db.close()
