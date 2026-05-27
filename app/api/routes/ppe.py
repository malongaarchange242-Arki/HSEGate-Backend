"""PPE detection API routes."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.services.ppe_detection_service import detect_ppe_from_bytes
from app.schemas.detection import DetectionResult

logger = logging.getLogger(__name__)

router = APIRouter(tags=["PPE Detection"])


@router.post("/detect", response_model=DetectionResult, summary="Détection EPI sur une image")
async def detect_ppe(
    file: UploadFile = File(..., description="Image à analyser (JPEG, PNG)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload an image file and run PPE detection.
    
    - **file**: Image file (jpg, jpeg, png)
    - **Returns**: Detection results with PPE compliance status
    """
    # Vérifier le type de fichier
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être une image (JPEG, PNG, etc.)"
        )
    
    # Vérifier la taille du fichier (max 10MB)
    file.file.seek(0, 2)  # Aller à la fin du fichier
    file_size = file.file.tell()
    file.file.seek(0)  # Revenir au début
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier ne doit pas dépasser 10MB"
        )
    
    try:
        contents = await file.read()
        logger.info(f"📸 Détection PPE sur: {file.filename} (taille: {file_size} bytes)")
        
    except Exception as e:
        logger.error(f"Erreur lecture fichier: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la lecture du fichier: {str(e)}"
        )

    # Exécuter la détection
    result = detect_ppe_from_bytes(contents)

    if not result.get("success"):
        logger.error(f"Échec détection: {result.get('error')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "La détection a échoué")
        )

    # Log du résultat
    if result.get("compliant"):
        logger.info(f"✅ Conforme - EPI détectés: {result.get('summary', {}).get('ppe_detected', [])}")
    else:
        logger.warning(f"⚠️ Non conforme - Manquant: {result.get('missing_ppe', [])}")

    return result


@router.post("/detect-batch", summary="Détection EPI sur plusieurs images")
async def detect_ppe_batch(
    files: list[UploadFile] = File(..., description="Liste d'images à analyser"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload multiple images and run PPE detection on each.
    
    - **files**: List of image files
    - **Returns**: List of detection results for each image
    """
    results = []
    
    for file in files:
        if not file.content_type.startswith("image/"):
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Format non supporté"
            })
            continue
        
        try:
            contents = await file.read()
            result = detect_ppe_from_bytes(contents)
            result["filename"] = file.filename
            results.append(result)
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {
        "success": True,
        "total_images": len(files),
        "results": results
    }


@router.get("/model-info", summary="Informations sur le modèle IA")
async def get_model_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get information about the loaded PPE detection model.
    """
    from app.services.ai_service import ai_service
    
    try:
        info = ai_service.get_model_info()
        return info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )