# init_db.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def init_database():
    db = SessionLocal()
    
    try:
        # Vérifier si l'utilisateur existe déjà
        existing = db.query(User).filter(User.email == "admin@hsegate.com").first()
        if existing:
            print(f"⚠️ L'utilisateur existe déjà (ID: {existing.id})")
            return
        
        # Créer le nouvel utilisateur
        user = User(
            fullname="Administrateur HSEGate",
            email="admin@hsegate.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("=" * 50)
        print("✅ UTILISATEUR CRÉÉ AVEC SUCCÈS !")
        print("=" * 50)
        print(f"🆔 ID: {user.id}")
        print(f"👤 Nom: {user.fullname}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Mot de passe: admin123")
        print(f"👔 Role: {user.role}")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()