/**
 * Module Dashboard pour HSEGate
 * Affiche les statistiques et les travailleurs récents
 */

/**
 * Charger et afficher les statistiques
 */
async function loadDashboardStats() {
    try {
        const workers = await api.getWorkers();

        // Mettre à jour les compteurs
        document.getElementById('worker-count').textContent = workers.length;
        document.getElementById('qr-count').textContent = workers.length;
        document.getElementById('badge-count').textContent = workers.length;

        // Afficher les travailleurs récents
        displayRecentWorkers(workers);
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        document.getElementById('worker-count').textContent = '0';
    }
}

/**
 * Afficher les travailleurs récents
 */
function displayRecentWorkers(workers) {
    const recentList = document.getElementById('recent-list');

    if (!workers || workers.length === 0) {
        recentList.innerHTML = '<p class="loading">Aucun travailleur enregistré</p>';
        return;
    }

    // Prendre les 5 derniers
    const recent = workers.slice(-5).reverse();

    let html = '<table>';
    html += '<thead><tr><th>Matricule</th><th>Nom</th><th>Département</th><th>Status</th></tr></thead>';
    html += '<tbody>';

    recent.forEach(worker => {
        const status = worker.status === 'active' ? '🟢 Actif' : '🔴 Inactif';
        html += `<tr>
            <td><strong>${worker.matricule}</strong></td>
            <td>${worker.fullname}</td>
            <td>${worker.department || 'N/A'}</td>
            <td>${status}</td>
        </tr>`;
    });

    html += '</tbody></table>';
    recentList.innerHTML = html;
}

/**
 * Initialisation du dashboard
 */
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();

    // Recharger les stats toutes les 30 secondes
    setInterval(loadDashboardStats, 30000);
});
