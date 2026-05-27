"""Detection schemas for PPE detection results."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict


class DetectionCreate(BaseModel):
    """Detection creation request."""
    worker_id: Optional[int] = None
    class_name: str  # e.g., "Hard_hat", "Vest", "Gloves"
    confidence: float
    camera_id: Optional[str] = None


class DetectionResponse(BaseModel):
    """Detection response schema for database records."""
    id: int
    worker_id: Optional[int]
    class_name: str
    confidence: float
    camera_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DetectionDetail(BaseModel):
    """Single detection detail with bounding box."""
    class_id: int = Field(..., description="Class ID from model")
    class_name: str = Field(..., description="Detected class name (e.g., Hard_hat, Vest)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    bbox: Optional[List[int]] = Field(None, description="Bounding box [x1, y1, x2, y2]")


class PPEStatus(BaseModel):
    """PPE detection status for each equipment type."""
    helmet: bool = Field(default=False, description="Hard hat detected")
    vest: bool = Field(default=False, description="Safety vest detected")
    glasses: bool = Field(default=False, description="Safety glasses detected")
    gloves: bool = Field(default=False, description="Gloves detected")
    boots: bool = Field(default=False, description="Safety boots detected")
    compliant: bool = Field(default=False, description="Overall compliance (helmet + vest)")


class DetectionSummary(BaseModel):
    """Summary of detection results."""
    total_detections: int = Field(..., description="Total number of detections")
    ppe_detected: List[str] = Field(default_factory=list, description="List of detected PPE classes")
    compliance_score: float = Field(..., description="Compliance percentage (0-100)")


class DetectionResult(BaseModel):
    """
    Complete detection result from PPE analysis.
    Matches the output of ai_service.detect_from_array()
    """
    success: bool = Field(..., description="Whether detection succeeded")
    compliant: bool = Field(default=False, description="Whether worker is PPE compliant")
    missing_ppe: List[str] = Field(default_factory=list, description="List of missing PPE items")
    detections: List[DetectionDetail] = Field(default_factory=list, description="All detected objects")
    ppe_status: Optional[PPEStatus] = Field(None, description="PPE status per equipment type")
    summary: Optional[DetectionSummary] = Field(None, description="Summary statistics")
    image_size: Optional[Dict[str, int]] = Field(None, description="Original image dimensions")
    error: Optional[str] = Field(None, description="Error message if success=False")
    filename: Optional[str] = Field(None, description="Original filename (for batch operations)")


class BatchDetectionResult(BaseModel):
    """Result for batch detection operations."""
    success: bool = Field(..., description="Whether batch operation succeeded")
    total_images: int = Field(..., description="Total number of images processed")
    results: List[DetectionResult] = Field(default_factory=list, description="Results for each image")