## 📮 **Postman Guide - HSEGate Worker Management**

### **BASE URL**
```
http://localhost:8000/api/v1
```

---

## 🔐 **1. Login (Get JWT Token)**

### Request
```http
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@hsegate.com",
  "password": "admin123"
}
```

### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**⚠️ Copy the `access_token` value - you'll need it for all other requests!**

---

## 👷 **2. Create Worker (POST /workers)**

### Request Headers
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

### Request Body
```json
{
  "fullname": "Jean Dupont",
  "matricule": "W001234",
  "department": "Production",
  "position": "Opérateur HSE",
  "company": "HSEGate Corp",
  "phone": "+24112345678",
  "email": "jean.dupont@hsegate.com",
  "emergency_contact": "+24187654321",
  "blood_group": "O+",
  "face_image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
}
```

### Response
```json
{
  "id": 1,
  "worker_uuid": "78ed644b-ebfc-4a9d-a068-593d7e9de7c7",
  "fullname": "Jean Dupont",
  "matricule": "W001234",
  "department": "Production",
  "position": "Opérateur HSE",
  "company": "HSEGate Corp",
  "phone": "+24112345678",
  "email": "jean.dupont@hsegate.com",
  "photo_url": "/uploads/faces/face_1.jpg",
  "badge_id": "fc3ca3cd-e1bb-447f-82fe-ab80edcd6526",
  "qr_code_url": "/uploads/qrcodes/worker_1_78ed644b-ebfc-4a9d-a068-593d7e9de7c7.png",
  "badge_image_url": "/uploads/badges/badge_1_78ed644b-ebfc-4a9d-a068-593d7e9de7c7.png",
  "emergency_contact": "+24187654321",
  "blood_group": "O+",
  "status": "active",
  "created_at": "2026-05-23T18:24:55.257025"
}
```

---

## 📋 **3. Get All Workers (GET /workers)**

### Request
```http
GET http://localhost:8000/api/v1/workers
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### Response
```json
[
  {
    "id": 1,
    "worker_uuid": "78ed644b-ebfc-4a9d-a068-593d7e9de7c7",
    "fullname": "Jean Dupont",
    "matricule": "W001234",
    ...
  }
]
```

---

## 🔍 **4. Get Worker by ID (GET /workers/{id})**

### Request
```http
GET http://localhost:8000/api/v1/workers/1
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

## 🔍 **5. Get Worker by Matricule (GET /workers/by-matricule/{matricule})**

### Request
```http
GET http://localhost:8000/api/v1/workers/by-matricule/W001234
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

## 🔲 **6. Get QR Code (GET /workers/{id}/qrcode)**

### Request
```http
GET http://localhost:8000/api/v1/workers/1/qrcode
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### Response
```json
{
  "worker_id": 1,
  "worker_uuid": "78ed644b-ebfc-4a9d-a068-593d7e9de7c7",
  "fullname": "Jean Dupont",
  "matricule": "W001234",
  "qr_code_url": "/uploads/qrcodes/worker_1_78ed644b-ebfc-4a9d-a068-593d7e9de7c7.png",
  "badge_image_url": "/uploads/badges/badge_1_78ed644b-ebfc-4a9d-a068-593d7e9de7c7.png",
  "qr_data": "{\"worker_id\": 1, \"worker_uuid\": \"78ed644b-ebfc-4a9d-a068-593d7e9de7c7\", \"matricule\": \"W001234\", \"fullname\": \"Jean Dupont\"}"
}
```

---

## 😊 **7. Register Face (POST /workers/{id}/face)**

### Request
```http
POST http://localhost:8000/api/v1/workers/1/face
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json

{
  "face_image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH..."
}
```

### Response
```json
{
  "worker_id": 1,
  "face_registered": true,
  "face_encoding_stored": true,
  "message": "Face registered successfully"
}
```

---

## ✏️ **8. Update Worker (PUT /workers/{id})**

### Request
```http
PUT http://localhost:8000/api/v1/workers/1
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json

{
  "fullname": "Jean Dupont Updated",
  "position": "Senior Opérateur HSE",
  "status": "active"
}
```

---

## 🗑️ **9. Delete Worker (DELETE /workers/{id})**

### Request
```http
DELETE http://localhost:8000/api/v1/workers/1
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

## 🎬 **Quick Postman Setup**

### Step 1: Set Environment Variable
1. Click **"Environment"** button (top-right)
2. Click **"Manage Environments"**
3. Create new environment: `HSEGate-Dev`
4. Add variable:
   ```
   Name: token
   Value: (leave empty, we'll set it after login)
   ```

### Step 2: Save Token After Login
1. Send Login request
2. In the **Tests** tab, add:
   ```javascript
   if (pm.response.code === 200) {
       pm.environment.set("token", pm.response.json().access_token);
   }
   ```
3. Send login request

### Step 3: Use Token in Other Requests
Replace `YOUR_ACCESS_TOKEN_HERE` with `{{token}}`

---

## 📊 **Test Results**

✅ **Worker Created Successfully:**
- ID: 1
- UUID: 78ed644b-ebfc-4a9d-a068-593d7e9de7c7
- Matricule: W001234
- QR Code: Generated and saved
- Badge: Generated and saved
- Status: active

---

## 🔗 **Access Generated Files**

After creating a worker, you can access:

- **Full Worker Data:** `http://localhost:8000/api/v1/workers/1`
- **QR Code Image:** `http://localhost:8000/uploads/qrcodes/worker_1_*.png`
- **Badge Image:** `http://localhost:8000/uploads/badges/badge_1_*.png`
- **Face Photo:** `http://localhost:8000/uploads/faces/face_1.jpg`

---

## 💡 **Tips**

1. **Blood Groups:** A+, A-, B+, B-, AB+, AB-, O+, O-
2. **Statuses:** active, inactive
3. **Roles:** admin, hse_supervisor, worker
4. **Face Image:** Optional, can be added later via face registration endpoint
5. **QR Code:** Auto-generated on worker creation

---

**🎉 Ton système est prêt à gérer les workers avec UUID, QR Codes, Badges et Reconnaissance Faciale!**
