/**
 * Module d'enregistrement travailleur pour HSEGate
 * Gère la soumission du formulaire et l'enregistrement
 */

/**
 * Enregistrer un nouveau travailleur
 */
async function submitWorker(event) {
    event?.preventDefault();

    const workerForm = document.getElementById('workerForm');
    const submitBtn = document.querySelector('button[type="submit"][form="workerForm"], #workerForm button[type="submit"]');
    const faceImageBase64 = document.getElementById('face_image_base64').value;

    // Valider que la photo est présente
    if (!faceImageBase64) {
        showStatusMessage('❌ Veuillez prendre ou uploader une photo', 'error');
        return;
    }

    // Récupérer les données du formulaire
    const workerData = {
        fullname: document.getElementById('fullname').value,
        email: document.getElementById('email').value || null,
        phone: document.getElementById('phone').value || null,
        department: document.getElementById('department').value || null,
        position: document.getElementById('position').value || null,
        company: document.getElementById('company').value || null,
        blood_group: document.getElementById('blood_group').value || null,
        emergency_contact: document.getElementById('emergency_contact').value || null,
        face_image_base64: faceImageBase64,
    };

    // Validation basique
    if (!workerData.fullname || workerData.fullname.trim() === '') {
        showStatusMessage('❌ Le nom complet est obligatoire', 'error');
        return;
    }

    try {
        // Désactiver le bouton
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Enregistrement...';
        }

        showStatusMessage('⏳ Enregistrement en cours...', 'info');

        // Créer le travailleur
        const response = await api.createWorker(workerData);

        console.log('✅ Worker created:', response);

        // Afficher le modal de succès
        showSuccessModal(response);

        // Réinitialiser le formulaire
        workerForm.reset();
        document.getElementById('face_image_base64').value = '';
        document.getElementById('capturePreview').style.display = 'none';

        // Réactiver le bouton
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Enregistrer Travailleur';
        }

        showStatusMessage('✅ Travailleur enregistré avec succès!', 'success');
    } catch (error) {
        console.error('Error creating worker:', error);

        let errorMessage = '❌ Erreur lors de l\'enregistrement';
        if (error.message.includes('already exists')) {
            errorMessage = '❌ Cet email ou matricule existe déjà';
        }

        showStatusMessage(errorMessage, 'error');

        // Réactiver le bouton
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Enregistrer Travailleur';
        }
    }
}

/**
 * Afficher le modal de succès
 */
function showSuccessModal(worker) {
    const modal = document.getElementById('successModal');

    // Remplir les informations
    document.getElementById('result-matricule').textContent = worker.matricule;
    document.getElementById('result-uuid').textContent = worker.worker_uuid;
    document.getElementById('result-name').textContent = worker.fullname;

    // Afficher QR Code
    if (worker.qr_code_url) {
        const qrImg = document.getElementById('qrcode-image');
        qrImg.src = `${API_ORIGIN}${worker.qr_code_url}`;
    }

    // Afficher Badge
    if (worker.badge_image_url) {
        const badgeImg = document.getElementById('badge-image');
        badgeImg.src = `${API_ORIGIN}${worker.badge_image_url}`;
    }

    // Stocker l'ID du travailleur pour le téléchargement
    modal.dataset.workerId = worker.id;
    modal.dataset.workerUUID = worker.worker_uuid;

    // Afficher le modal
    modal.style.display = 'block';
}

/**
 * Fermer le modal de succès
 */
function closeSuccessModal() {
    document.getElementById('successModal').style.display = 'none';
}

/**
 * Télécharger le badge
 */
async function downloadBadge() {
    const modal = document.getElementById('successModal');
    const workerId = modal.dataset.workerId;
    const matricule = document.getElementById('result-matricule').textContent;

    try {
        const badgeBlob = await api.downloadBadge(workerId);
        const url = window.URL.createObjectURL(badgeBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `badge_${matricule}.png`;
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);
    } catch (error) {
        console.error('Error downloading badge:', error);
        showStatusMessage('❌ Erreur lors du téléchargement', 'error');
    }
}

/**
 * Afficher un message de statut
 */
function showStatusMessage(message, type = 'info') {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    statusDiv.style.display = 'block';

    // Auto-masquer après 5 secondes pour les messages info/success
    if (type !== 'error') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

/**
 * Initialisation du formulaire
 */
document.addEventListener('DOMContentLoaded', () => {
    const workerForm = document.getElementById('workerForm');
    if (workerForm) {
        workerForm.addEventListener('submit', submitWorker);
    }

    // Fermer le modal en cliquant en dehors
    window.addEventListener('click', (event) => {
        const modal = document.getElementById('successModal');
        if (event.target === modal) {
            closeSuccessModal();
        }
    });
});
