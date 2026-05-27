# 🚀 QUICK START - HSEGate System

## Prérequis
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (optionnel)
- Navigateur moderne (Chrome, Firefox, Safari, Edge)

---

## 1️⃣ Démarrer le Backend

### Windows PowerShell:
```powershell
# Naviguer vers le dossier backend
cd d:\HSEGate-Backend

# Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python init_db.py

# Démarrer le serveur
python -m uvicorn app.main:app --reload --port 8000
```

### Linux/Mac:
```bash
cd ~/HSEGate-Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8000
```

✅ **Backend prêt**: http://localhost:8000

---

## 2️⃣ Démarrer le Frontend

### Option A: Live Server (Recommandé)
```bash
cd d:\HSEGate-Frontend
npm install
npm start
```

### Option B: Python Simple HTTP
```bash
cd d:\HSEGate-Frontend
python -m http.server 5500
```

### Option C: Ouvrir directement
Navigateur → `file:///d:/HSEGate-Frontend/index.html`

✅ **Frontend prêt**: http://localhost:5500

---

## 3️⃣ Premier Test

### Via Page d'Accueil:
```
1. Ouvrir http://localhost:5500
2. Voir les statistiques (Dashboard)
3. Cliquer "Nouveau Travailleur"
4. Remplir le formulaire
5. Démarrer caméra ou uploader une image
6. Prendre photo
7. Cliquer "Enregistrer Travailleur"
8. ✅ Matricule auto-généré (HSE-YYYY-XXXX)
9. ✅ Badge et QR code générés
```

### Via API (Postman/curl):
```bash
# Authentification
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hsegate.com","password":"admin123"}'

# Copier le token retourné

# Récupérer les travailleurs
curl -X GET http://localhost:8000/api/v1/workers \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔐 Credentials Admin

```
Email:    admin@hsegate.com
Password: admin123
```

---

## 📁 Structure du Projet

```
d:\HSEGate-Backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── workers.py        # Endpoints travailleurs
│   │       └── auth.py           # Authentification
│   ├── services/
│   │   ├── qrcode_service.py     # Génération QR
│   │   ├── face_service.py       # Reconnaissance faciale
│   │   └── matricule_service.py  # Auto-génération matricule
│   ├── models/
│   │   └── worker.py             # Modèle travailleur
│   └── main.py
├── requirements.txt
├── docker-compose.yml
└── init_db.py

d:\HSEGate-Frontend/
├── index.html                    # Dashboard
├── workers/
│   └── workers/register.html      # Enregistrement
├── workers.html                  # Liste travailleurs
├── test.html                     # Test système
├── css/
│   └── style.css                 # Styles
├── js/
│   ├── api.js                    # Client API
│   ├── webcam.js                 # Webcam
│   ├── register.js               # Enregistrement
│   ├── dashboard.js              # Dashboard
│   └── workers.js                # Liste
├── README.md
└── package.json
```

---

## ✅ Checklist de Vérification

- [ ] Backend tourne sur http://localhost:8000
- [ ] PostgreSQL est opérationnel
- [ ] Base de données 'hsegate' créée
- [ ] Frontend accessible sur http://localhost:5500
- [ ] Console pas d'erreurs (F12)
- [ ] Webcam fonctionne (ou upload possible)
- [ ] Formulaire accepte les données
- [ ] Matricule auto-généré en HSE-YYYY-XXXX
- [ ] Badge et QR code générés
- [ ] Travailleurs affichés dans la liste

---

## 🚨 Troubleshooting

### Backend ne démarre pas:
```
1. Vérifier Python: python --version
2. Vérifier pip: pip list | grep fastapi
3. Vérifier PostgreSQL: psql -U postgres
4. Essayer: pip install --upgrade -r requirements.txt
```

### Frontend ne charge pas:
```
1. Vérifier console: F12 → Console
2. Vérifier backend: curl http://localhost:8000
3. Essayer autre port: python -m http.server 5501
4. Vider cache: Ctrl+Shift+Delete
```

### Webcam ne marche pas:
```
1. Vérifier permissions du navigateur
2. Essayer incognito
3. Utiliser upload d'image alternative
4. Vérifier: navigator.mediaDevices.getUserMedia()
```

### Erreur CORS:
```
1. Vérifier que Backend tourne
2. Vérifier configuration CORS du backend
3. Essayer localhost au lieu de 127.0.0.1
4. Vérifier les headers Authorization
```

---

## 📚 Documentation Complète

- [Backend README](../HSEGate-Backend/README.md)
- [Frontend README](./README.md)
- [API Docs](http://localhost:8000/docs)
- [Database Schema](../HSEGate-Backend/README.md#base-de-donn%C3%A9es)

---

## 🆘 Support Rapide

| Problème | Solution |
|----------|----------|
| Port 8000 occupé | Changer port: `--port 8001` |
| Port 5500 occupé | Utiliser autre port: `:5501` |
| DB n'existe pas | Exécuter: `python init_db.py` |
| Extension PostgreSQL | `CREATE EXTENSION IF NOT EXISTS uuid-ossp;` |
| Token expiré | Rafraîchir page ou réauthentifier |
| Webcam refusée | Vérifier paramètres navigateur |

---

## 🎯 Workflow Complet

```
[Frontend]
    ↓ (Formulaire + Photo)
[Validation Frontend]
    ↓ (HTTP POST JSON)
[Backend API]
    ↓ (Validation + Auth)
[Services]
    ├→ MatriculeService (HSE-2026-0001)
    ├→ QRCodeService (Générer badge)
    └→ FaceService (Enregistrer visage)
    ↓ (Sauvegarder données)
[PostgreSQL]
    ↓ (Retourner JSON)
[Frontend]
    ↓ (Afficher résultats)
[Modal Succès]
```

---

## 🎨 URLs Principales

```
📊 Dashboard:      http://localhost:5500/index.html
📸 Enregistrement: http://localhost:5500/workers/register.html
👥 Travailleurs:   http://localhost:5500/workers.html
🧪 Tests:          http://localhost:5500/test.html

🔌 Backend API:    http://localhost:8000
📖 API Docs:       http://localhost:8000/docs
🔄 API ReDoc:      http://localhost:8000/redoc
```

---

## ⚡ Performance

- Backend: ~50ms par requête
- QR Code generation: ~100ms
- Face encoding: ~200ms
- Transfert image: ~500ms (5MB)
- Temps total enregistrement: ~1-2 secondes

---

## 🔒 Sécurité

✅ JWT Authentication
✅ Role-based Access Control (RBAC)
✅ Password Hashing (bcrypt)
✅ SQL Injection Prevention (SQLAlchemy)
✅ CORS Configuration
✅ Rate Limiting (optionnel)
✅ Input Validation (Pydantic)

---

## 📞 Commandes Utiles

```bash
# Backend logs
tail -f backend.log

# Database
psql -U postgres -d hsegate

# Frontend test
curl http://localhost:5500/index.html

# API health check
curl http://localhost:8000/docs

# Kill port
# Windows: netstat -ano | findstr :8000
# Linux: lsof -i :8000 | kill -9 PID
```

---

## 🎉 Prêt?

```
1. ✅ Backend démarré
2. ✅ Frontend démarré
3. ✅ Database prête
4. ✅ Admin connecté

→ Aller à http://localhost:5500 🚀
```

---

**Créé avec ❤️ pour HSEGate System**
