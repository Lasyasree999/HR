"""
HireGenius AI — Database Setup Script
========================================
Creates the MySQL database, initializes tables via SQLAlchemy ORM,
and seeds the default admin user.

Usage:
    python scripts/setup_db.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from config import get_settings, ensure_directories
from database.connection import engine, Base, SessionLocal
from database.models import User
from utils.security import hash_password


def setup_database():
    """Create all tables and seed default data."""
    print("=" * 60)
    print("  HireGenius AI — Database Setup")
    print("=" * 60)

    settings = get_settings()
    print(f"\nDatabase: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    # Create all tables
    print("\n[DB] Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("   [OK] All tables created successfully")
    except Exception as e:
        print(f"   [ERROR] Failed: {e}")
        print("\n   Make sure the database configuration is correct and running.")
        return

    # Create data directories
    print("\n[DIR] Creating data directories...")
    ensure_directories()
    print("   [OK] Directories created")

    # Seed admin user
    print("\n[USER] Seeding admin user...")
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@hiregenius.ai",
                password_hash=hash_password("admin123"),
                full_name="System Administrator",
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("   [OK] Admin user created (admin / admin123)")
        else:
            print("   [INFO] Admin user already exists")
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("  Setup complete! Run the app with:")
    print("  cd backend && python -m uvicorn main:app --reload")
    print("=" * 60)


if __name__ == "__main__":
    setup_database()
