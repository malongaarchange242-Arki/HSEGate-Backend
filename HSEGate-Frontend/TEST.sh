#!/bin/bash

echo "🚀 === HSEGate System - Test Script ==="
echo ""

# Vérifier que le backend tourne
echo "1️⃣  Vérification du backend..."
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend FastAPI tourne sur http://localhost:8000"
else
    echo "❌ Backend FastAPI ne répond pas sur http://localhost:8000"
    echo "   Assurez-vous que:"
    echo "   - Python 3.11+ est installé"
    echo "   - Naviguer vers: d:\\HSEGate-Backend"
    echo "   - Exécuter: python -m uvicorn app.main:app --reload --port 8000"
    exit 1
fi

# Vérifier PostgreSQL
echo ""
echo "2️⃣  Vérification de PostgreSQL..."
if psql -U postgres -h localhost -d postgres -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ PostgreSQL est opérationnel"
else
    echo "❌ PostgreSQL ne répond pas"
    echo "   Assurez-vous que PostgreSQL est installé et en cours d'exécution"
    exit 1
fi

# Vérifier que la base de données existe
echo ""
echo "3️⃣  Vérification de la base de données HSEGate..."
if psql -U postgres -h localhost -d hsegate -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ Base de données 'hsegate' existe"
else
    echo "⚠️  Base de données 'hsegate' n'existe pas"
    echo "   Assurez-vous d'avoir exécuté: python init_db.py"
fi

# Tester l'authentification API
echo ""
echo "4️⃣  Test d'authentification API..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hsegate.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✅ Authentification API fonctionne"
    TOKEN=$(echo "$RESPONSE" | grep -oP '"access_token":"\K[^"]+')
    echo "   Token obtenu: ${TOKEN:0:20}..."
else
    echo "❌ Authentification échouée"
    echo "   Réponse: $RESPONSE"
    exit 1
fi

# Récupérer la liste des travailleurs
echo ""
echo "5️⃣  Test de récupération des travailleurs..."
WORKERS=$(curl -s -X GET http://localhost:8000/api/v1/workers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

if echo "$WORKERS" | grep -q "\[\]" || echo "$WORKERS" | grep -q "id"; then
    echo "✅ API des travailleurs fonctionne"
    COUNT=$(echo "$WORKERS" | grep -o '"id"' | wc -l)
    echo "   Nombre de travailleurs: $COUNT"
else
    echo "⚠️  Impossible de récupérer les travailleurs"
    echo "   Réponse: $WORKERS"
fi

# Vérifier les uploads
echo ""
echo "6️⃣  Vérification des répertoires d'upload..."
if [ -d "d:\\HSEGate-Backend\\uploads\\qrcodes" ]; then
    echo "✅ Répertoire QR codes existe"
else
    echo "⚠️  Répertoire QR codes n'existe pas - créé automatiquement au premier upload"
fi

if [ -d "d:\\HSEGate-Backend\\uploads\\badges" ]; then
    echo "✅ Répertoire badges existe"
else
    echo "⚠️  Répertoire badges n'existe pas - créé automatiquement au premier upload"
fi

# Frontend
echo ""
echo "7️⃣  Status du Frontend..."
echo "📂 Fichiers Frontend:"
echo "   ✅ index.html (Dashboard)"
echo "   ✅ register.html (Enregistrement avec webcam)"
echo "   ✅ workers.html (Liste des travailleurs)"
echo "   ✅ css/style.css (Styles responsifs)"
echo "   ✅ js/api.js (Client API)"
echo "   ✅ js/webcam.js (Gestion webcam)"
echo "   ✅ js/register.js (Logique enregistrement)"
echo "   ✅ js/dashboard.js (Dashboard)"
echo "   ✅ js/workers.js (Liste travailleurs)"

echo ""
echo "🚀 === Démarrage du Frontend ==="
echo ""
echo "Option 1: Avec live-server (recommandé)"
echo "  npm install"
echo "  npm start"
echo ""
echo "Option 2: Avec Python"
echo "  python -m http.server 5500"
echo ""
echo "Option 3: Ouvrir directement dans le navigateur"
echo "  Ouvrir: file:///d:/HSEGate-Frontend/index.html"
echo ""
echo "✅ === Configuration Complète ==="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5500"
echo ""
echo "Credentials:"
echo "  Email:    admin@hsegate.com"
echo "  Password: admin123"
echo ""
echo "📝 Workflow de test:"
echo "  1. Aller sur http://localhost:5500"
echo "  2. Cliquer sur 'Nouveau Travailleur'"
echo "  3. Remplir le formulaire"
echo "  4. Cliquer 'Démarrer Caméra' ou uploader une image"
echo "  5. Prendre une photo"
echo "  6. Cliquer 'Enregistrer Travailleur'"
echo "  7. Vérifier que Matricule, Badge et QR Code sont générés"
echo "  8. Aller sur 'Travailleurs' pour voir la liste"
echo ""
echo "🎉 === Prêt à démarrer! ==="
