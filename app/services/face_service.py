"""Face recognition service for worker registration."""

import base64
import json
import numpy as np
from io import BytesIO
from PIL import Image
import hashlib
from pathlib import Path

from app.core.config import settings


class FaceRecognitionService:
    """Service for face encoding and recognition."""
    
    def __init__(self):
        self.face_dir = Path(settings.UPLOAD_DIR) / "faces"
        self.face_dir.mkdir(parents=True, exist_ok=True)
        self.face_encodings = {}  # In-memory cache for demo
        # For production, use a proper face recognition library
    
    def decode_base64_image(self, base64_string: str) -> np.ndarray:
        """Decode base64 image to numpy array."""
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        return np.array(image)
    
    def extract_face_encoding(self, image: np.ndarray) -> list:
        """
        Extract face encoding from image.
        For demo, returns a dummy encoding.
        In production, use face-recognition or deepface library.
        """
        # For now, generate a dummy encoding based on image hash
        # In production, replace with:
        # import face_recognition
        # encodings = face_recognition.face_encodings(image)
        # return encodings[0].tolist() if encodings else None
        
        # Dummy implementation for demo
        img_hash = hashlib.md5(image.tobytes()).hexdigest()
        # Create a deterministic "encoding" for demo
        dummy_encoding = [float(ord(c)) / 255.0 for c in img_hash[:128]]
        # Pad to 128 dimensions
        dummy_encoding.extend([0.0] * (128 - len(dummy_encoding)))
        return dummy_encoding
    
    def save_face_image(self, worker_id: int, image: np.ndarray) -> str:
        """Save face image to disk."""
        filename = f"face_{worker_id}.jpg"
        filepath = self.face_dir / filename
        
        # Convert to PIL and save
        pil_image = Image.fromarray(np.uint8(image))
        pil_image.save(filepath)
        
        return f"/uploads/faces/{filename}"
    
    def register_face(self, worker_id: int, face_image_base64: str) -> tuple[list, str]:
        """Register a worker's face."""
        try:
            # Decode image
            image = self.decode_base64_image(face_image_base64)
            
            # Extract face encoding
            encoding = self.extract_face_encoding(image)
            
            # Save face image
            face_url = self.save_face_image(worker_id, image)
            
            # Store encoding (in production, save to database)
            self.face_encodings[worker_id] = encoding
            
            return encoding, face_url
            
        except Exception as e:
            print(f"Face registration error: {e}")
            return None, None


# Global instance
face_service = FaceRecognitionService()
