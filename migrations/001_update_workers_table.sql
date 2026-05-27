"""
Migration script to update Workers table with new fields.
Run this before starting the application with the new models.

Steps:
1. Connect to PostgreSQL:
   psql -U hsegate_user -d hsegate_db

2. If the workers table already exists, run:
   ALTER TABLE workers DROP TABLE IF EXISTS workers CASCADE;

3. Then run the SQLAlchemy models to create the table:
   python -c "from app.database.base import Base; from app.database.connection import engine; Base.metadata.create_all(bind=engine)"

Or execute the SQL below directly in psql.
"""

-- Drop existing workers table if it exists
DROP TABLE IF EXISTS workers CASCADE;

-- Create new workers table with all new fields
CREATE TABLE workers (
    id SERIAL PRIMARY KEY,
    worker_uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    fullname VARCHAR(255) NOT NULL,
    matricule VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(255),
    position VARCHAR(255),
    company VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255) UNIQUE,
    photo_url TEXT,
    face_embedding TEXT,  -- Stored as base64/JSON
    badge_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    qr_code_url TEXT,
    badge_image_url TEXT,
    emergency_contact VARCHAR(255),
    blood_group VARCHAR(20),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Create indexes for performance
    CHECK (blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', NULL))
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_workers_matricule ON workers(matricule);
CREATE INDEX idx_workers_email ON workers(email);
CREATE INDEX idx_workers_worker_uuid ON workers(worker_uuid);
CREATE INDEX idx_workers_badge_id ON workers(badge_id);
CREATE INDEX idx_workers_status ON workers(status);

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
