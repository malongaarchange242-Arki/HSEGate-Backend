"""PPE Detection service.py — wrapper around `ai_service` and YOLO model.

This module provides a single entrypoint `detect_ppe_from_bytes` which accepts
image bytes and returns the structured detection + PPE compliance payload used
by the rest of the application.
"""

from typing import Dict
import cv2
import numpy as np
from app.services.ai_service import ai_service
from app.schemas.detection import DetectionDetail, PPEStatus, DetectionSummary


def build_detection_result_from_ai_response(ai_response: Dict) -> Dict:
    """
    Convert AI service response to DetectionResult schema.
    
    Args:
        ai_response: Raw response from ai_service.detect_from_array()
        
    Returns:
        Structured dictionary matching DetectionResult schema
    """
    if not ai_response.get("success"):
        return {
            "success": False,
            "compliant": False,
            "missing_ppe": [],
            "detections": [],
            "ppe_status": None,
            "summary": None,
            "image_size": None,
            "error": ai_response.get("error", "Unknown error")
        }
    
    # Convertir les détections
    detections = []
    for det in ai_response.get("detections", []):
        detection_detail = DetectionDetail(
            class_id=det.get("class_id", 0),
            class_name=det.get("class_name", "Unknown"),
            confidence=det.get("confidence", 0.0),
            bbox=det.get("bbox")
        )
        detections.append(detection_detail.dict())
    
    # Extraire les détections pour PPEStatus
    ppe_detected = ai_response.get("summary", {}).get("ppe_detected", [])
    
    # Déterminer la conformité individuelle des EPI
    ppe_status = PPEStatus(
        helmet="Hard_hat" in ppe_detected,
        vest="Vest" in ppe_detected,
        gloves="Gloves" in ppe_detected,
        boots="Safety_boots" in ppe_detected,
        glasses=False,  # À adapter selon ton modèle
        compliant=ai_response.get("compliant", False)
    )
    
    # Construire le résumé
    summary = DetectionSummary(
        total_detections=len(detections),
        ppe_detected=ppe_detected,
        compliance_score=ai_response.get("summary", {}).get("compliance_score", 0)
    )
    
    return {
        "success": True,
        "compliant": ai_response.get("compliant", False),
        "missing_ppe": ai_response.get("missing_ppe", []),
        "detections": detections,
        "ppe_status": ppe_status.dict(),
        "summary": summary.dict(),
        "image_size": ai_response.get("image_size"),
        "error": None
    }


def detect_ppe_from_bytes(image_bytes: bytes) -> Dict:
    """
    Decode image bytes and run PPE detection using `ai_service`.
    
    Returns a structured dictionary matching DetectionResult schema.
    """
    try:
        # Convert bytes to numpy array then to BGR image for OpenCV
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {
                "success": False,
                "compliant": False,
                "missing_ppe": [],
                "detections": [],
                "ppe_status": None,
                "summary": None,
                "image_size": None,
                "error": "Failed to decode image"
            }
        
        # Get raw detection from AI service
        ai_response = ai_service.detect_from_array(img)
        
        # Convert to structured format
        return build_detection_result_from_ai_response(ai_response)
        
    except Exception as e:
        return {
            "success": False,
            "compliant": False,
            "missing_ppe": [],
            "detections": [],
            "ppe_status": None,
            "summary": None,
            "image_size": None,
            "error": str(e)
        }


def detect_ppe_from_path(image_path: str) -> Dict:
    """
    Load image from file path and run PPE detection.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Structured dictionary matching DetectionResult schema
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {
                "success": False,
                "compliant": False,
                "missing_ppe": [],
                "detections": [],
                "ppe_status": None,
                "summary": None,
                "image_size": None,
                "error": f"Failed to read image from path: {image_path}"
            }
        
        ai_response = ai_service.detect_from_array(img)
        return build_detection_result_from_ai_response(ai_response)
        
    except Exception as e:
        return {
            "success": False,
            "compliant": False,
            "missing_ppe": [],
            "detections": [],
            "ppe_status": None,
            "summary": None,
            "image_size": None,
            "error": str(e)
        }