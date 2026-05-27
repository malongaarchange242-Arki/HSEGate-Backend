"""Script to create a test worker via API."""

import sys
import os
import base64
import requests
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Base API URL
API_BASE = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get JWT token using admin credentials."""
    print("🔐 Getting authentication token...")
    
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={
            "email": "admin@hsegate.com",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Token obtained: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        raise Exception("Authentication failed")

def create_worker(token):
    """Create a test worker."""
    print("\n👷 Creating worker...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create a dummy base64 image for face (1x1 pixel JPEG)
    dummy_jpg_base64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
    
    worker_data = {
        "fullname": "Jean Dupont",
        "matricule": "W001234",
        "department": "Production",
        "position": "Opérateur HSE",
        "company": "HSEGate Corp",
        "phone": "+24112345678",
        "email": "jean.dupont@hsegate.com",
        "emergency_contact": "+24187654321",
        "blood_group": "O+",
        "face_image_base64": f"data:image/jpeg;base64,{dummy_jpg_base64}"
    }
    
    response = requests.post(
        f"{API_BASE}/workers",
        headers=headers,
        json=worker_data
    )
    
    if response.status_code == 201:
        worker = response.json()
        print(f"✅ Worker created successfully!")
        print(f"\n📊 Worker Details:")
        print(f"  ID: {worker['id']}")
        print(f"  UUID: {worker['worker_uuid']}")
        print(f"  Name: {worker['fullname']}")
        print(f"  Matricule: {worker['matricule']}")
        print(f"  Badge ID: {worker['badge_id']}")
        print(f"  QR Code URL: {worker['qr_code_url']}")
        print(f"  Badge Image: {worker['badge_image_url']}")
        print(f"  Photo URL: {worker['photo_url']}")
        print(f"  Status: {worker['status']}")
        print(f"  Created: {worker['created_at']}")
        
        return worker
    else:
        print(f"❌ Failed to create worker: {response.text}")
        raise Exception("Worker creation failed")

def get_worker_qrcode(token, worker_id):
    """Get worker QR code."""
    print(f"\n🔲 Getting QR code for worker {worker_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_BASE}/workers/{worker_id}/qrcode",
        headers=headers
    )
    
    if response.status_code == 200:
        qr_data = response.json()
        print(f"✅ QR code retrieved!")
        print(f"\n📋 QR Code Details:")
        print(f"  URL: {qr_data['qr_code_url']}")
        print(f"  Badge: {qr_data['badge_image_url']}")
        print(f"  Data: {qr_data['qr_data']}")
        
        return qr_data
    else:
        print(f"❌ Failed to get QR code: {response.text}")
        raise Exception("QR code retrieval failed")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 HSEGate Worker Creation Test")
    print("=" * 60)
    
    try:
        # Get token
        token = get_auth_token()
        
        # Create worker
        worker = create_worker(token)
        
        # Get QR code
        qr_data = get_worker_qrcode(token, worker["id"])
        
        print("\n" + "=" * 60)
        print("✨ Worker creation completed successfully!")
        print("=" * 60)
        print(f"\n🔗 Access URLs:")
        print(f"  - Full Worker: http://localhost:8000/api/v1/workers/{worker['id']}")
        print(f"  - QR Code: {worker['qr_code_url']}")
        print(f"  - Badge: {worker['badge_image_url']}")
        print(f"  - Face: {worker['photo_url']}")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
