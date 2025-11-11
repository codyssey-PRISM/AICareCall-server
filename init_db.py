"""
Script to initialize the database tables.
Run this once to create all tables defined in models.py
"""
from database import engine, Base
from models import Callee

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()

