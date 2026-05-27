"""AI Service for PPE detection using YOLO."""

import torch
from ultralytics.nn.tasks import DetectionModel
from ultralytics.nn.modules import Conv, Bottleneck, C2f, SPPF, Detect, DFL

# ============================================================
# CORRECTION POUR PYTORCH 2.6+
# Autoriser les classes Ultralytics nécessaires pour le chargement
# ============================================================

# Liste des classes Ultralytics à autoriser
SAFE_GLOBALS = [
    DetectionModel,
    Conv,
    Bottleneck,
    C2f,
    SPPF,
    Detect,
    DFL,
]

# Enregistrer les classes comme sécurisées
try:
    torch.serialization.add_safe_globals(SAFE_GLOBALS)
    print("✅ PyTorch safe globals configured for Ultralytics")
except Exception as e:
    print(f"⚠️ Could not configure safe globals: {e}")

# ============================================================

import cv2
import numpy as np
from typing import Dict, List, Optional
from ultralytics import YOLO
import warnings

warnings.filterwarnings("ignore")


class AIService:
    """Service for AI-powered PPE detection using YOLOv8."""

    def __init__(self, model_path: str = "runs/detect/train3/weights/best.pt"):
        """
        Initialize AI service with custom PPE YOLO model.
        
        Args:
            model_path: Path to the trained YOLO model weights
        """
        try:
            # Utiliser le contexte safe_globals pour le chargement
            with torch.serialization.safe_globals(SAFE_GLOBALS):
                self.model = YOLO(model_path)
            
            self.confidence_threshold = 0.5
            
            # Définition des EPI requis pour la conformité HSE
            self.required_ppe = [
                "Hard_hat",      # Casque de sécurité
                "Vest",          # Gilet de sécurité
                "Safety_boots"   # Bottes de sécurité
            ]
            
            print(f"✅ PPE YOLO model loaded successfully from: {model_path}")
            print(f"📋 Required PPE classes: {self.required_ppe}")
            
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            self.model = None
            self.required_ppe = []

    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model status and information
        """
        if not self.model:
            return {
                "status": "not_loaded",
                "error": "Model not initialized"
            }

        try:
            return {
                "status": "loaded",
                "model_type": "PPE Detection Model (YOLOv8)",
                "model_path": str(self.model.model if hasattr(self.model, 'model') else "unknown"),
                "confidence_threshold": self.confidence_threshold,
                "required_ppe": self.required_ppe,
                "num_classes": len(self.model.names) if hasattr(self.model, 'names') else 0,
                "classes": self.model.names if hasattr(self.model, 'names') else {}
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def detect_from_array(self, image: np.ndarray) -> Dict:
        """
        Detect PPE objects in image from numpy array.
        
        Args:
            image: Numpy array (OpenCV format BGR)
            
        Returns:
            Dictionary with detection results and PPE compliance analysis
            {
                "success": bool,
                "compliant": bool,
                "missing_ppe": List[str],
                "detections": List[Dict],
                "error": str (if success=False)
            }
        """
        if self.model is None:
            return {
                "success": False,
                "error": "Model not loaded"
            }

        try:
            # Run inference with confidence threshold
            results = self.model(image, conf=self.confidence_threshold, verbose=False)

            detections: List[Dict] = []
            detected_classes: List[str] = []

            # Process detection results
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None and len(result.boxes) > 0:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        
                        # Get class name from model
                        class_name = self.model.names[class_id]
                        
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        detected_classes.append(class_name)
                        
                        detections.append({
                            "class_id": class_id,
                            "class_name": class_name,
                            "confidence": round(confidence, 3),
                            "bbox": [x1, y1, x2, y2]
                        })

            # Analyze PPE compliance
            missing_ppe = []
            for required_item in self.required_ppe:
                if required_item not in detected_classes:
                    missing_ppe.append(required_item)

            is_compliant = len(missing_ppe) == 0

            return {
                "success": True,
                "compliant": is_compliant,
                "missing_ppe": missing_ppe,
                "detections": detections,
                "summary": {
                    "total_detections": len(detections),
                    "ppe_detected": list(set([d["class_name"] for d in detections 
                                              if d["class_name"] in self.required_ppe])),
                    "compliance_score": ((len(self.required_ppe) - len(missing_ppe)) / len(self.required_ppe)) * 100
                    if self.required_ppe else 0
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def detect_from_image_path(self, image_path: str) -> Dict:
        """
        Detect PPE objects in image from file path.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Same as detect_from_array
        """
        if self.model is None:
            return {
                "success": False,
                "error": "Model not loaded"
            }

        try:
            # Read image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": f"Failed to read image: {image_path}"
                }
            
            return self.detect_from_array(image)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def detect_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        Detect PPE objects in image from bytes.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Same as detect_from_array
        """
        try:
            # Convert bytes to numpy array
            arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    "success": False,
                    "error": "Failed to decode image from bytes"
                }
            
            return self.detect_from_array(image)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global AI service instance with PPE model
ai_service = AIService()