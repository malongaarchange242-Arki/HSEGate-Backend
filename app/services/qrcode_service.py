"""QR Code generation service with photo embedding."""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
import uuid
from io import BytesIO
import base64
from pathlib import Path
import json
from datetime import datetime
from PIL import Image

from app.core.config import settings


class QRCodeService:
    """Service for generating QR codes for workers with photo."""
    
    def __init__(self):
        self.qr_dir = Path(settings.UPLOAD_DIR) / "qrcodes"
        self.qr_dir.mkdir(parents=True, exist_ok=True)
        self.badge_dir = Path(settings.UPLOAD_DIR) / "badges"
        self.badge_dir.mkdir(parents=True, exist_ok=True)
    
    def encode_image_to_base64(self, image_path: str = None, image_base64: str = None) -> str:
        """Encode image to base64 string."""
        if image_base64:
            # Si déjà en base64, retourner tel quel
            return image_base64
        
        if image_path and Path(image_path).exists():
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        
        return None
    
    def generate_worker_qr_data(self, worker: dict) -> dict:
        """Generate QR data for a worker with complete information including photo."""
        
        # Données complètes du travailleur
        qr_data = {
            "type": "worker_identification",
            "version": "2.0",
            "timestamp": str(datetime.utcnow()),
            
            # Informations d'identification
            "worker_id": worker.get("id"),
            "worker_uuid": str(worker.get("worker_uuid", "")),
            "matricule": worker.get("matricule", ""),
            
            # Informations personnelles
            "fullname": worker.get("fullname", ""),
            "first_name": worker.get("first_name", ""),
            "last_name": worker.get("last_name", ""),
            "email": worker.get("email", ""),
            "phone": worker.get("phone", ""),
            
            # Informations professionnelles
            "department": worker.get("department", ""),
            "position": worker.get("position", ""),
            "company": worker.get("company", ""),
            
            # Informations médicales (urgence)
            "blood_group": worker.get("blood_group", ""),
            "emergency_contact": worker.get("emergency_contact", ""),
            "emergency_name": worker.get("emergency_name", ""),
            
            # Statut et dates
            "status": worker.get("status", "active"),
            "created_at": str(worker.get("created_at", "")),
            
            # Photo encodée en base64 (optionnel - peut être lourd)
            "photo_base64": worker.get("face_image_base64") or self.encode_image_to_base64(worker.get("photo_url")),
            
            # URL de la photo (alternative plus légère)
            "photo_url": worker.get("photo_url", ""),
            "badge_url": worker.get("badge_image_url", "")
        }
        
        return qr_data
    
    def create_qr_code(self, data: dict, size: int = 10) -> BytesIO:
        """Create a styled QR code image."""
        # Convertir les données en JSON avec gestion de la taille
        json_data = json.dumps(data, ensure_ascii=False)
        
        # Vérifier la taille des données (QR code max ~3KB pour version 40)
        if len(json_data) > 3000:
            # Si trop gros, créer une version allégée sans la photo base64
            light_data = {k: v for k, v in data.items() if k != "photo_base64"}
            light_data["has_photo"] = bool(data.get("photo_base64"))
            light_data["photo_url"] = data.get("photo_url", "")
            json_data = json.dumps(light_data, ensure_ascii=False)
        
        qr = qrcode.QRCode(
            version=5,  # Version plus grande pour contenir plus de données
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=4,
        )
        qr.add_data(json_data)
        qr.make(fit=True)
        
        # Create styled QR code
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=RadialGradiantColorMask(
                center_color=(0, 100, 255),
                edge_color=(100, 0, 255)
            )
        )
        
        # Save to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    def create_badge_with_photo(self, worker: dict, qr_buffer: BytesIO) -> BytesIO:
        """Create a badge image with worker photo and QR code."""
        from PIL import Image, ImageDraw, ImageFont
        
        # Créer un badge (carte d'identité)
        badge_width = 600
        badge_height = 400
        badge = Image.new('RGB', (badge_width, badge_height), 'white')
        draw = ImageDraw.Draw(badge)
        
        # Fond dégradé
        for i in range(badge_height):
            color_value = 245 - int(i / badge_height * 50)
            draw.rectangle([(0, i), (badge_width, i)], fill=(color_value, color_value, 255))
        
        # Cadre
        draw.rectangle([(5, 5), (badge_width - 5, badge_height - 5)], outline='#2563eb', width=3)
        
        # En-tête
        draw.rectangle([(5, 5), (badge_width - 5, 70)], fill='#2563eb')
        
        # Charger la photo du travailleur
        if worker.get("photo_url"):
            try:
                photo_path = Path(settings.UPLOAD_DIR) / worker["photo_url"].split('/')[-1]
                if photo_path.exists():
                    photo = Image.open(photo_path)
                    photo = photo.resize((120, 120))
                    badge.paste(photo, (30, 90))
            except Exception as e:
                print(f"Erreur chargement photo: {e}")
        
        # Ajouter le QR code
        qr_img = Image.open(qr_buffer)
        qr_img = qr_img.resize((150, 150))
        badge.paste(qr_img, (badge_width - 200, badge_height - 180))
        
        # Ajouter les informations texte
        try:
            font_title = ImageFont.truetype("arial.ttf", 20)
            font_text = ImageFont.truetype("arial.ttf", 14)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
        
        # Nom
        draw.text((180, 95), f"Nom: {worker.get('fullname', '')[:30]}", fill='#1f2937', font=font_text)
        draw.text((180, 125), f"Matricule: {worker.get('matricule', '')}", fill='#1f2937', font=font_text)
        draw.text((180, 155), f"Département: {worker.get('department', '')}", fill='#1f2937', font=font_text)
        draw.text((180, 185), f"Poste: {worker.get('position', '')}", fill='#1f2937', font=font_text)
        draw.text((180, 215), f"Groupe sanguin: {worker.get('blood_group', '')}", fill='#1f2937', font=font_text)
        
        # Pied de page
        draw.rectangle([(5, badge_height - 40), (badge_width - 5, badge_height - 5)], fill='#2563eb')
        draw.text((badge_width // 2 - 100, badge_height - 35), "HSEGate AI - Badge de Sécurité", fill='white', font=font_text)
        
        # Sauvegarder
        buffer = BytesIO()
        badge.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    def save_qr_code(self, worker_id: int, worker_uuid: uuid.UUID, worker_data: dict) -> tuple[str, str]:
        """Generate and save QR code and badge for a worker."""
        # Ajouter l'ID et l'UUID aux données
        worker_data["id"] = worker_id
        worker_data["worker_uuid"] = worker_uuid
        
        # Generate QR data
        qr_data = self.generate_worker_qr_data(worker_data)
        
        # Create QR code image
        qr_buffer = self.create_qr_code(qr_data)
        
        # Save QR code
        qr_filename = f"worker_{worker_id}_{worker_uuid}.png"
        qr_path = self.qr_dir / qr_filename
        with open(qr_path, 'wb') as f:
            f.write(qr_buffer.getvalue())
        
        # Create and save badge with photo
        qr_buffer.seek(0)
        badge_buffer = self.create_badge_with_photo(worker_data, qr_buffer)
        badge_filename = f"badge_{worker_id}_{worker_uuid}.png"
        badge_path = self.badge_dir / badge_filename
        with open(badge_path, 'wb') as f:
            f.write(badge_buffer.getvalue())
        
        return f"/uploads/qrcodes/{qr_filename}", f"/uploads/badges/{badge_filename}"
    
    def get_qr_code_base64(self, worker_id: int, worker_uuid: uuid.UUID, worker_data: dict) -> str:
        """Generate QR code and return as base64."""
        worker_data["id"] = worker_id
        worker_data["worker_uuid"] = worker_uuid
        qr_data = self.generate_worker_qr_data(worker_data)
        qr_buffer = self.create_qr_code(qr_data)
        return base64.b64encode(qr_buffer.getvalue()).decode('utf-8')


# Global instance
qr_service = QRCodeService()