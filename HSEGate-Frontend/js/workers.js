/**
 * Module Travailleurs pour HSEGate
 * Version corrigée
 */

let allWorkers = [];
let currentWorker = null;
let currentFilters = {
    search: '',
    status: '',
    department: ''
};

function getAssetUrl(path) {
    if (!path) return '';
    if (/^https?:\/\//i.test(path)) return path;
    return `${API_ORIGIN}${path.startsWith('/') ? path : `/${path}`}`;
}

/**
 * Charger tous les travailleurs
 */
async function loadWorkers() {
    const workersList = document.getElementById('workersList');
    if (workersList) {
        workersList.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Chargement des travailleurs...</p>
            </div>
        `;
    }
    
    try {
        allWorkers = await api.getWorkers();
        updateStats();
        applyFilters();
    } catch (error) {
        console.error('Error loading workers:', error);
        if (workersList) {
            workersList.innerHTML = `
                <div style="text-align: center; padding: 3rem;">
                    <i class="fas fa-exclamation-circle" style="font-size: 3rem; color: var(--danger); margin-bottom: 1rem;"></i>
                    <p>Erreur lors du chargement des travailleurs</p>
                    <button class="btn btn-primary" onclick="loadWorkers()" style="margin-top: 1rem;">
                        <i class="fas fa-sync-alt"></i> Réessayer
                    </button>
                </div>
            `;
        }
    }
}

/**
 * Mettre à jour les statistiques
 */
function updateStats() {
    const total = allWorkers.length;
    const active = allWorkers.filter(w => w.status === 'active').length;
    const withQR = allWorkers.filter(w => w.qr_code_url).length;
    
    // Mettre à jour les cartes statistiques
    const totalEl = document.getElementById('totalWorkers');
    const activeEl = document.getElementById('activeWorkers');
    const qrEl = document.getElementById('qrGenerated');
    const incidentsEl = document.getElementById('incidentsCount');
    
    if (totalEl) totalEl.textContent = total;
    if (activeEl) activeEl.textContent = active;
    if (qrEl) qrEl.textContent = withQR;
    if (incidentsEl) incidentsEl.textContent = "0";
}

/**
 * Appliquer tous les filtres
 */
function applyFilters() {
    let filtered = [...allWorkers];
    
    if (currentFilters.search) {
        const search = currentFilters.search.toLowerCase();
        filtered = filtered.filter(worker =>
            worker.fullname.toLowerCase().includes(search) ||
            worker.matricule.toLowerCase().includes(search) ||
            (worker.email && worker.email.toLowerCase().includes(search))
        );
    }
    
    if (currentFilters.status) {
        filtered = filtered.filter(worker => worker.status === currentFilters.status);
    }
    
    if (currentFilters.department) {
        filtered = filtered.filter(worker => worker.department === currentFilters.department);
    }
    
    displayWorkers(filtered);
}

/**
 * Afficher les travailleurs dans un tableau
 */
function displayWorkers(workers) {
    const workersList = document.getElementById('workersList');
    
    if (!workers || workers.length === 0) {
        workersList.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <i class="fas fa-users-slash" style="font-size: 3rem; color: var(--gray); margin-bottom: 1rem;"></i>
                <p>Aucun travailleur trouvé</p>
                <a href="workers/register.html" class="btn btn-primary" style="margin-top: 1rem;">
                    <i class="fas fa-plus"></i> Ajouter un travailleur
                </a>
            </div>
        `;
        return;
    }
    
    let html = `
        <table class="workers-table">
            <thead>
                <tr>
                    <th>Matricule</th>
                    <th>Nom</th>
                    <th>Email</th>
                    <th>Département</th>
                    <th>Statut</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    workers.forEach(worker => {
        const statusClass = worker.status === 'active' ? 'badge-active' : 'badge-inactive';
        const statusText = worker.status === 'active' ? 'Actif' : 'Inactif';
        
        html += `
            <tr>
                <td><strong>${escapeHtml(worker.matricule)}</strong></td>
                <td>${escapeHtml(worker.fullname)}</td>
                <td>${worker.email ? escapeHtml(worker.email) : '-'}</td>
                <td>${worker.department ? escapeHtml(worker.department) : '-'}</td>
                <td><span class="badge ${statusClass}">${statusText}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn view" onclick="showWorkerDetails(${worker.id})" title="Voir">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="action-btn edit" onclick="editWorker(${worker.id})" title="Modifier">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete" onclick="deleteWorker(${worker.id})" title="Supprimer">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    workersList.innerHTML = html;
}

/**
 * Filtrer les travailleurs
 */
function filterWorkers() {
    currentFilters.search = document.getElementById('searchInput')?.value || '';
    currentFilters.status = document.getElementById('statusFilter')?.value || '';
    currentFilters.department = document.getElementById('departmentFilter')?.value || '';
    applyFilters();
}

/**
 * Afficher les détails d'un travailleur
 */
async function showWorkerDetails(workerId) {
    try {
        const worker = await api.getWorker(workerId);
        currentWorker = worker;
        
        // Remplir les informations
        document.getElementById('modal-matricule').textContent = worker.matricule || '-';
        document.getElementById('modal-name').textContent = worker.fullname || '-';
        document.getElementById('modal-email').textContent = worker.email || '-';
        document.getElementById('modal-phone').textContent = worker.phone || '-';
        document.getElementById('modal-department').textContent = worker.department || '-';
        document.getElementById('modal-position').textContent = worker.position || '-';
        document.getElementById('modal-blood').textContent = worker.blood_group || '-';
        document.getElementById('modal-emergency').textContent = worker.emergency_contact || '-';
        document.getElementById('modal-profile-name').textContent = worker.fullname || '-';
        document.getElementById('modal-profile-position').textContent = worker.position || worker.department || '-';

        const photoImage = document.getElementById('modal-photo');
        const photoPlaceholder = document.getElementById('modal-photo-placeholder');
        if (worker.photo_url) {
            photoImage.src = getAssetUrl(worker.photo_url);
            photoImage.style.display = 'block';
            photoPlaceholder.style.display = 'none';
            photoImage.onerror = () => {
                photoImage.style.display = 'none';
                photoPlaceholder.style.display = 'block';
            };
        } else {
            photoImage.removeAttribute('src');
            photoImage.style.display = 'none';
            photoPlaceholder.style.display = 'block';
        }
        
        // QR Code
        const qrContainer = document.getElementById('qr-container');
        const qrImage = document.getElementById('modal-qr');
        if (worker.qr_code_url) {
            qrImage.src = getAssetUrl(worker.qr_code_url);
            qrImage.onerror = () => {
                qrContainer.style.display = 'none';
                alert('QR code introuvable sur le serveur. Verifiez que le backend expose le dossier uploads.');
            };
            qrContainer.style.display = 'block';
        } else {
            qrImage.removeAttribute('src');
            qrContainer.style.display = 'none';
        }
        
        document.getElementById('workerModal').style.display = 'flex';
        document.getElementById('workerModal').classList.add('active');
    } catch (error) {
        console.error('Error loading worker details:', error);
        alert('❌ Erreur lors du chargement des détails');
    }
}

/**
 * Fermer le modal
 */
function closeWorkerModal() {
    const modal = document.getElementById('workerModal');
    modal.style.display = 'none';
    modal.classList.remove('active');
    currentWorker = null;
}

/**
 * Modifier un travailleur
 */
function editWorker(workerId) {
    window.location.href = `workers/edit.html?id=${workerId}`;
}

/**
 * Supprimer un travailleur
 */
async function deleteWorker(workerId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce travailleur ?')) return;
    
    try {
        await api.deleteWorker(workerId);
        loadWorkers();
        alert('✅ Travailleur supprimé avec succès');
    } catch (error) {
        console.error('Error deleting worker:', error);
        alert('❌ Erreur lors de la suppression');
    }
}

/**
 * Télécharger le QR code
 */
async function downloadQRCode() {
    if (!currentWorker || !currentWorker.qr_code_url) {
        alert('QR code non disponible');
        return;
    }
    
    try {
        const response = await fetch(getAssetUrl(currentWorker.qr_code_url));
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `qr_${currentWorker.matricule}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading QR code:', error);
        alert('Erreur lors du téléchargement');
    }
}

/**
 * Imprimer le badge
 */
function printBadge() {
    if (!currentWorker || !currentWorker.qr_code_url) {
        alert('QR code non disponible');
        return;
    }
    
    const qrUrl = getAssetUrl(currentWorker.qr_code_url);
    const photoUrl = currentWorker.photo_url ? getAssetUrl(currentWorker.photo_url) : '';
    const workerName = escapeHtml(currentWorker.fullname || '-');
    const workerPosition = escapeHtml(currentWorker.position || currentWorker.department || '');
    const workerMatricule = escapeHtml(currentWorker.matricule || '-');
    const workerBloodGroup = escapeHtml(currentWorker.blood_group || 'N/A');
    const photoHtml = photoUrl
        ? `<img id="badge-photo" class="badge-photo" src="${photoUrl}" alt="Photo du travailleur">`
        : '<div class="badge-photo badge-photo-placeholder">Photo</div>';
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
        alert('Impossible d ouvrir la fenetre d impression');
        return;
    }

    printWindow.document.write(`
        <html>
        <head>
            <title>Badge - ${workerName}</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 20px; color: #1e293b; }
                .badge { width: 340px; margin: 0 auto; border: 1px solid #cbd5e1; border-radius: 10px; padding: 18px; }
                h2 { margin: 0 0 14px; font-size: 22px; }
                .badge-media { display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 12px; }
                .badge-photo { width: 120px; height: 120px; object-fit: cover; border: 1px solid #cbd5e1; border-radius: 8px; }
                .badge-photo-placeholder { display: flex; align-items: center; justify-content: center; color: #64748b; background: #f8fafc; font-size: 13px; }
                .badge-qr { width: 120px; height: 120px; object-fit: contain; }
                h3 { margin: 8px 0 4px; font-size: 18px; }
                .position { margin: 0 0 10px; color: #64748b; font-size: 13px; }
                p { margin: 5px 0; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="badge">
                <h2>HSEGate AI</h2>
                <div class="badge-media">
                    ${photoHtml}
                    <img id="badge-qr" class="badge-qr" src="${qrUrl}" alt="QR Code">
                </div>
                <h3>${workerName}</h3>
                <p class="position">${workerPosition}</p>
                <p>Matricule: ${workerMatricule}</p>
                <p>Groupe: ${workerBloodGroup}</p>
            </div>
            <script>
                const images = Array.from(document.querySelectorAll('img'));
                const printNow = () => {
                    window.focus();
                    window.print();
                };
                let pending = images.filter(image => !image.complete).length;
                if (pending === 0) {
                    printNow();
                } else {
                    const done = () => {
                        pending -= 1;
                        if (pending === 0) printNow();
                    };
                    images.forEach(image => {
                        if (!image.complete) {
                            image.onload = done;
                            image.onerror = done;
                        }
                    });
                }
            <\/script>
        </body>
        </html>
    `);
    printWindow.document.close();
}

/**
 * Exporter les données
 */
function exportWorkers() {
    const data = JSON.stringify(allWorkers, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `workers_export_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    alert('Export terminé');
}

/**
 * Échapper le HTML
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadWorkers();
    
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const departmentFilter = document.getElementById('departmentFilter');
    const exportBtn = document.getElementById('exportBtn');
    
    if (searchInput) searchInput.addEventListener('input', filterWorkers);
    if (statusFilter) statusFilter.addEventListener('change', filterWorkers);
    if (departmentFilter) departmentFilter.addEventListener('change', filterWorkers);
    if (exportBtn) exportBtn.addEventListener('click', exportWorkers);
    
    // Fermer le modal en cliquant en dehors
    window.addEventListener('click', event => {
        const modal = document.getElementById('workerModal');
        if (event.target === modal) closeWorkerModal();
    });
    
    // Recharger toutes les 60 secondes
    setInterval(loadWorkers, 60000);
});
