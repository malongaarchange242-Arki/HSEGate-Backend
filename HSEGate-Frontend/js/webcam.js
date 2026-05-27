/**
 * Module Webcam pour HSEGate
 * Gère la capture de photo via webcam
 */

let stream = null;
let capturedImageBase64 = null;

/**
 * Démarrer la caméra
 */
async function startWebcam() {
    try {
        // Demander l'accès à la caméra
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        });

        // Afficher le flux vidéo
        const video = document.getElementById('video');
        video.srcObject = stream;

        // Afficher/masquer les boutons
        document.getElementById('startWebcamBtn').style.display = 'none';
        document.getElementById('captureBtn').style.display = 'inline-block';
        document.getElementById('stopWebcamBtn').style.display = 'inline-block';

        console.log('✅ Webcam started');
    } catch (error) {
        console.error('❌ Erreur accès caméra:', error);
        showStatusMessage(
            '❌ Impossible d\'accéder à la caméra. Vérifiez les permissions.',
            'error'
        );
    }
}

/**
 * Arrêter la caméra
 */
function stopWebcam() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    const video = document.getElementById('video');
    video.srcObject = null;

    // Afficher/masquer les boutons
    document.getElementById('startWebcamBtn').style.display = 'inline-block';
    document.getElementById('captureBtn').style.display = 'none';
    document.getElementById('stopWebcamBtn').style.display = 'none';

    console.log('✅ Webcam stopped');
}

/**
 * Capturer une photo de la webcam
 */
function capturePhoto() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');

    if (!video.srcObject) {
        showStatusMessage('❌ La caméra n\'est pas active', 'error');
        return;
    }

    // Configurer le canvas avec les dimensions de la vidéo
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Dessiner l'image de la vidéo sur le canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    // Convertir en base64
    capturedImageBase64 = canvas.toDataURL('image/jpeg', 0.9);

    // Afficher l'aperçu
    const capturedImage = document.getElementById('capturedImage');
    capturedImage.src = capturedImageBase64;

    const previewDiv = document.getElementById('capturePreview');
    previewDiv.style.display = 'block';

    console.log('✅ Photo captured');
}

/**
 * Reprendre une photo
 */
function retakePhoto() {
    capturedImageBase64 = null;
    document.getElementById('capturePreview').style.display = 'none';
}

/**
 * Accepter la photo capturée
 */
function acceptPhoto() {
    // Arrêter la caméra
    stopWebcam();

    // Remplir le champ caché
    document.getElementById('face_image_base64').value = capturedImageBase64;

    showStatusMessage('✅ Photo validée avec succès', 'success');
}

/**
 * Gérer l'upload d'image alternative
 */
function handleImageUpload(event) {
    const file = event.target.files[0];

    if (!file) return;

    // Vérifier que c'est une image
    if (!file.type.startsWith('image/')) {
        showStatusMessage('❌ Veuillez sélectionner une image', 'error');
        return;
    }

    // Lire le fichier
    const reader = new FileReader();

    reader.onload = (e) => {
        capturedImageBase64 = e.target.result;

        // Afficher l'aperçu
        const capturedImage = document.getElementById('capturedImage');
        capturedImage.src = capturedImageBase64;

        const previewDiv = document.getElementById('capturePreview');
        previewDiv.style.display = 'block';

        // Arrêter la webcam si elle tourne
        if (stream) {
            stopWebcam();
        }

        // Remplir le champ caché
        document.getElementById('face_image_base64').value = capturedImageBase64;

        showStatusMessage('✅ Image uploadée avec succès', 'success');
    };

    reader.onerror = () => {
        showStatusMessage('❌ Erreur lors de la lecture du fichier', 'error');
    };

    reader.readAsDataURL(file);
}

/**
 * Afficher un message de statut
 */
function showStatusMessage(message, type = 'info') {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    statusDiv.style.display = 'block';

    // Masquer après 5 secondes
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

// Arrêter la webcam quand la page se décharge
window.addEventListener('beforeunload', () => {
    if (stream) {
        stopWebcam();
    }
});
