"""
Initialization script for database schema with new Worker model.
This script will create all necessary tables based on SQLAlchemy models.

Usage:
    python init_db_schema.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.base import Base
from app.database.connection import engine
from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.incident import Incident
from app.models.alert import Alert
from app.models.detection import Detection
from app.models.risk_report import RiskReport
from app.models.access_log import AccessLog
from app.core.security import get_password_hash
from sqlalchemy import text

def init_database_schema():
    """Create all tables from SQLAlchemy models."""
    print("=" * 60)
    print("🚀 Initializing Database Schema...")
    print("=" * 60)
    
    try:
        # Enable PostgreSQL extensions
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
            conn.commit()
            print("✅ PostgreSQL extensions enabled")
        
        # Create all tables from Base metadata
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        print("\n" + "=" * 60)
        print("📊 Tables created:")
        print("=" * 60)
        for table_name in Base.metadata.tables.keys():
            print(f"  ✓ {table_name}")
        
        print("\n" + "=" * 60)
        print("✨ Database initialization completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

def init_default_user():
    """Create default admin user if it doesn't exist."""
    from app.database.connection import SessionLocal
    
    print("\n" + "=" * 60)
    print("👤 Initializing Default User...")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == "admin@hsegate.com").first()
        if existing:
            print(f"⚠️  Admin user already exists (ID: {existing.id})")
            return
        
        # Create default admin user - NOTE: role must match UserRole enum values
        admin_user = User(
            fullname="Administrateur HSEGate",
            email="admin@hsegate.com",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("\n" + "=" * 60)
        print("✅ DEFAULT ADMIN USER CREATED!")
        print("=" * 60)
        print(f"🆔 ID: {admin_user.id}")
        print(f"👤 Name: {admin_user.fullname}")
        print(f"📧 Email: {admin_user.email}")
        print(f"🔑 Password: admin123")
        print(f"👔 Role: {admin_user.role}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creating default user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("\n")
    
    # Initialize schema
    init_database_schema()
    
    # Initialize default user
    init_default_user()
    
    print("\n" + "=" * 60)
    print("🎉 Database initialization completed successfully!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("  1. Start the backend: uvicorn app.main:app --reload")
    print("  2. Create workers with QR codes and face recognition")
    print("  3. Access API at http://localhost:8000/docs")
    print("\n")
