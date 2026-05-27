# 🏭 HSEGate Frontend

Frontend moderne pour le système HSEGate - Système de biométrie pour identification des travailleurs

## 🚀 Démarrage Rapide

### Prérequis
- Node.js 18+ (optionnel, pour le live-server)
- Backend FastAPI en cours d'exécution sur `http://localhost:8000`
- Chrome, Firefox, ou tout navigateur moderne supportant WebRTC

### Installation

1. **Démarrer le live-server** (méthode recommandée pour le développement):
```bash
npm install -g live-server
cd d:\HSEGate-Frontend
live-server --port=5500
```

Ou ouvrir directement les fichiers HTML dans le navigateur.

2. **Accéder à l'application**:
```
http://localhost:5500
```

## 📁 Structure du Projet

```
HSEGate-Frontend/
├── index.html              # 📊 Dashboard principal
├── workers/
│   └── register.html      # 📸 Enregistrement travailleur avec webcam
├── workers.html            # 👥 Liste des travailleurs
├── css/
│   └── style.css          # 🎨 Styles principaux (responsive)
└── js/
    ├── api.js             # 🔌 Client API & authentification
    ├── webcam.js          # 📷 Gestion de la webcam
    ├── register.js        # 📝 Logique d'enregistrement
    ├── dashboard.js       # 📈 Gestion du dashboard
    └── workers.js         # 👤 Gestion de la liste des travailleurs
```

## 🎯 Fonctionnalités Principales

### 1️⃣ **Dashboard** (`index.html`)
- Affiche les statistiques globales
- Liste des 5 travailleurs récents
- Actions rapides (ajouter, voir tous)
- Mise à jour automatique toutes les 30 secondes

### 2️⃣ **Enregistrement Travailleur** (`workers/register.html`)
- Formulaire complet avec tous les champs HSE
- **Capture webcam**:
  - Démarrer/arrêter caméra
  - Prendre photo du visage
  - Prévisualisation et retouche
- **Upload alternatif** d'image
- Auto-génération du matricule (format: HSE-YYYY-XXXX)
- Modal de succès avec:
  - Badge généré 🎫
  - QR Code généré 🔲
  - Téléchargement possible

### 3️⃣ **Liste Travailleurs** (`workers.html`)
- Tableau complet de tous les travailleurs
- Recherche par nom/matricule/email
- Filtrage par statut
- Modal détails avec:
  - Toutes les informations
  - QR Code
  - Badge
  - Photo du visage

## 🔐 Authentification

- **Admin par défaut**:
  - Email: `admin@hsegate.com`
  - Mot de passe: `admin123`
- Token JWT stocké dans `localStorage`
- Renouvellement automatique si expiration

## 📸 Fonctionnalité Webcam

```javascript
// Workflow dans workers/register.html:
1. Cliquer "Démarrer Caméra"
   → navigator.mediaDevices.getUserMedia() demande permission
   
2. Caméra active
   → Video stream s'affiche
   
3. Cliquer "Prendre Photo"
   → Capture le frame vidéo sur canvas
   → Conversion en base64 (JPEG qualité 90%)
   
4. Aperçu + Valider
   → Stocker base64 dans form hidden field
   
5. Enregistrer
   → Envoyer au backend avec autres données
```

## 🔌 Intégration API

### Endpoints utilisés:

```
POST   /api/v1/auth/login              # Authentification
POST   /api/v1/workers                 # Créer travailleur
GET    /api/v1/workers                 # Lister travailleurs
GET    /api/v1/workers/{id}            # Détails travailleur
GET    /api/v1/workers/{id}/qrcode     # QR Code
GET    /api/v1/workers/{id}/badge      # Badge image
```

### Format de création travailleur:
```json
{
  "fullname": "string *",
  "email": "string",
  "phone": "string",
  "department": "string",
  "position": "string",
  "company": "string",
  "blood_group": "enum (O+, O-, A+, A-, B+, B-, AB+, AB-)",
  "emergency_contact": "string",
  "face_image_base64": "data:image/jpeg;base64,..."
}
```

**Notes**:
- Le `matricule` est auto-généré par le backend (HSE-YYYY-XXXX)
- `face_image_base64` doit inclure le préfixe `data:image/jpeg;base64,`
- Tous les champs sauf `fullname` et `face_image_base64` sont optionnels

## 🎨 Design & UX

### Thème Couleur
- Primaire: `#0066cc` (Bleu)
- Secondaire: `#6b21a8` (Violet)
- Succès: `#16a34a` (Vert)
- Danger: `#dc2626` (Rouge)
- Arrière-plan: Gradient violet (667eea → 764ba2)

### Responsive Design
- ✅ Desktop (1200px+)
- ✅ Tablet (768px - 1199px)
- ✅ Mobile (< 768px)

### Accessibilité
- Labels associés aux inputs
- ARIA labels sur les modals
- Contraste des couleurs conforme WCAG
- Navigation au clavier complète

## 🚨 Gestion des Erreurs

L'application affiche des messages clairs:
- ❌ Erreurs: Message persistent jusqu'à fermeture
- ⏳ Infos: Disparaît après 5 secondes
- ✅ Succès: Disparaît après 5 secondes

## 📝 Logs en Console

L'application log toutes les actions importantes en console (Dev Tools: F12)

```javascript
// Exemples:
✅ Authentication successful
✅ Worker created successfully
❌ Error creating worker: [detail]
✅ Photo captured
✅ Face registered successfully
```

## 🔧 Configuration Backend

Assurer que le backend FastAPI:
1. Tourne sur `http://localhost:8000`
2. A les endpoints CORS configurés pour `localhost:5500`
3. Database PostgreSQL initialisée (via `init_db.py`)

### Backend URL dans le code:
```javascript
// js/api.js
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

## 🐛 Troubleshooting

### La webcam n'accède pas?
```
1. Vérifier que le navigateur a la permission caméra
2. Essayer dans un mode privé/incognito
3. Vérifier que HTTPS est disponible (WebRTC req. souvent HTTPS en prod)
4. Alternative: Uploader une image
```

### Les données ne s'enregistrent pas?
```
1. Vérifier que le backend tourne: http://localhost:8000/docs
2. Vérifier la console (F12) pour les erreurs d'API
3. Vérifier les credentials admin: admin@hsegate.com / admin123
4. Vérifier que PostgreSQL est actif
```

### Le formulaire rejette l'email?
```
- Format email requis: utilisateur@domaine.com
- Pas d'espaces avant/après
- Caractères valides uniquement
```

## 📦 Dépendances Frontend

**Aucune dépendance externe requise!**

- HTML5 natif
- CSS3 natif (Grid, Flexbox, Media queries)
- JavaScript ES6+ natif
- WebRTC API (navigator.mediaDevices)
- Fetch API (requêtes HTTP)

## 🚀 Déploiement

Pour déployer en production:

1. **Build statique** (copier tous les fichiers):
```bash
cp -r css/ dist/
cp -r js/ dist/
cp -r *.html dist/
```

2. **Serveur**: Tout serveur HTTP statique (Nginx, Apache, Vercel, etc.)

3. **Configuration CORS backend**: Permettre le domaine de production

4. **HTTPS obligatoire** pour webcam en production

## 📞 Support

Pour les problèmes:
1. Vérifier la console (F12 → Console tab)
2. Vérifier les réponses API (F12 → Network tab)
3. Vérifier que le backend tourne correctement

## 📄 Licence

Propriétaire - HSEGate System

---

**Développé avec ❤️ pour la sécurité des travailleurs** 🏭👷
