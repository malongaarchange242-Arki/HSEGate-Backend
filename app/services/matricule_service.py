"""Worker matricule generation service."""

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.worker import Worker


class MatriculeService:
    """Service for generating worker matricule numbers."""
    
    MATRICULE_PREFIX = "HSE"
    
    @staticmethod
    def generate_matricule(db: Session) -> str:
        """
        Generate a unique matricule in format: HSE-YYYY-XXXX
        where YYYY is the current year and XXXX is a sequential number.
        """
        current_year = datetime.utcnow().year
        prefix = f"{MatriculeService.MATRICULE_PREFIX}-{current_year}"
        
        # Get the last worker with this year's prefix
        last_worker = db.query(Worker).filter(
            Worker.matricule.like(f"{prefix}-%")
        ).order_by(Worker.matricule.desc()).first()
        
        if last_worker:
            # Extract the sequence number from the last matricule
            last_sequence = int(last_worker.matricule.split('-')[-1])
            next_sequence = last_sequence + 1
        else:
            # First worker of this year
            next_sequence = 1
        
        # Generate new matricule with zero-padded sequence number
        matricule = f"{prefix}-{next_sequence:04d}"
        
        return matricule


# Global instance
matricule_service = MatriculeService()
