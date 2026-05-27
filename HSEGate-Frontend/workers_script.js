let allWorkers = [];
        let currentWorker = null;

        /**
         * Charger tous les travailleurs
         */
        async function loadWorkers() {
            try {
                const workersList = document.getElementById('workersList');
                workersList.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Chargement des travailleurs...</p></div>';
                
                allWorkers = await api.getWorkers();
                updateStats();
                displayWorkers(allWorkers);
            } catch (error) {
                console.error('Error loading workers:', error);
                document.getElementById('workersList').innerHTML = `
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

        /**
         * Mettre à jour les statistiques
         */
        function updateStats() {
            const total = allWorkers.length;
            const active = allWorkers.filter(w => w.status === 'active').length;
            const qrGenerated = allWorkers.filter(w => w.qr_code_url).length;
            
            document.getElementById('totalWorkers').textContent = total;
            document.getElementById('activeWorkers').textContent = active;
            document.getElementById('qrGenerated').textContent = qrGenerated;
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
                            <th><i class="fas fa-id-card"></i> Matricule</th>
                            <th><i class="fas fa-user"></i> Nom</th>
                            <th><i class="fas fa-envelope"></i> Email</th>
                            <th><i class="fas fa-building"></i> Département</th>
                            <th><i class="fas fa-church"></i> Groupe sanguin</th>
                            <th><i class="fas fa-circle"></i> Statut</th>
                            <th><i class="fas fa-cog"></i> Actions</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            workers.forEach(worker => {
                const statusBadge = worker.status === 'active' 
                    ? '<span class="badge badge-active"><i class="fas fa-check-circle"></i> Actif</span>'
                    : '<span class="badge badge-inactive"><i class="fas fa-ban"></i> Inactif</span>';
                
                html += `
                    <tr>
                        <td><strong>${escapeHtml(worker.matricule)}</strong></td>
                        <td>${escapeHtml(worker.fullname)}</td>
                        <td>${worker.email ? escapeHtml(worker.email) : '-'}</td>
                        <td>${worker.department ? escapeHtml(worker.department) : '-'}</td>
                        <td>${worker.blood_group ? escapeHtml(worker.blood_group) : '-'}</td>
                        <td>${statusBadge}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="action-btn view" onclick="showWorkerDetails(${worker.id})" title="Voir détails">
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

            html += '</tbody></table>';
            workersList.innerHTML = html;
        }

        /**
         * Filtrer les travailleurs
         */
        function filterWorkers() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const statusFilter = document.getElementById('statusFilter').value;
            const departmentFilter = document.getElementById('departmentFilter').value;

            let filtered = allWorkers;

            if (searchTerm) {
                filtered = filtered.filter(worker =>
                    worker.fullname.toLowerCase().includes(searchTerm) ||
                    worker.matricule.toLowerCase().includes(searchTerm) ||
                    (worker.email && worker.email.toLowerCase().includes(searchTerm))
                );
            }

            if (statusFilter) {
                filtered = filtered.filter(worker => worker.status === statusFilter);
            }

            if (departmentFilter) {
                filtered = filtered.filter(worker => worker.department === departmentFilter);
            }

            displayWorkers(filtered);
        }

        /**
         * Afficher les détails d'un travailleur
         */
        async function showWorkerDetails(workerId) {
            try {
                currentWorker = await api.getWorker(workerId);
                
                document.getElementById('modal-matricule').textContent = currentWorker.matricule || '-';
                document.getElementById('modal-name').textContent = currentWorker.fullname || '-';
                document.getElementById('modal-email').textContent = currentWorker.email || '-';
                document.getElementById('modal-phone').textContent = currentWorker.phone || '-';
                document.getElementById('modal-department').textContent = currentWorker.department || '-';
                document.getElementById('modal-position').textContent = currentWorker.position || '-';
                document.getElementById('modal-blood').textContent = currentWorker.blood_group || '-';
                document.getElementById('modal-emergency').textContent = currentWorker.emergency_contact || '-';
                
                // QR Code
                const qrContainer = document.getElementById('qr-container');
                if (currentWorker.qr_code_url) {
                    document.getElementById('modal-qr').src = `${API_ORIGIN}${currentWorker.qr_code_url}`;
                    qrContainer.style.display = 'block';
                } else {
                    qrContainer.style.display = 'none';
                }
                
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
            document.getElementById('workerModal').classList.remove('active');
            currentWorker = null;
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
                const response = await fetch(`${API_ORIGIN}${currentWorker.qr_code_url}`);
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
            if (!currentWorker) return;
            
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                <head>
                    <title>Badge - ${currentWorker.fullname}</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: #f0f0f0;
                        }
                        .badge {
                            width: 300px;
                            background: white;
                            border-radius: 10px;
                            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                            overflow: hidden;
                            text-align: center;
                        }
                        .badge-header {
                            background: linear-gradient(135deg, #2563eb, #7c3aed);
                            color: white;
                            padding: 1rem;
                            font-size: 1.2rem;
                            font-weight: bold;
                        }
                        .badge-body {
                            padding: 1.5rem;
                        }
                        .badge-body img {
                            max-width: 150px;
                            margin: 1rem 0;
                        }
                        .badge-name {
                            font-size: 1.1rem;
                            font-weight: bold;
                            margin: 0.5rem 0;
                        }
                        .badge-matricule {
                            color: #666;
                            font-size: 0.9rem;
                        }
                        .badge-footer {
                            background: #f8fafc;
                            padding: 0.75rem;
                            font-size: 0.8rem;
                            color: #666;
                        }
                    </style>
                </head>
                <body>
                    <div class="badge">
                        <div class="badge-header">
                            <i class="fas fa-shield-alt"></i> HSEGate AI
                        </div>
                        <div class="badge-body">
                            <img src="${API_ORIGIN}${currentWorker.qr_code_url}" alt="QR Code">
                            <div class="badge-name">${currentWorker.fullname}</div>
                            <div class="badge-matricule">Matricule: ${currentWorker.matricule}</div>
                            <div>Groupe: ${currentWorker.blood_group || 'N/A'}</div>
                        </div>
                        <div class="badge-footer">
                            Valable pour accès au site
                        </div>
                    </div>
                </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();
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
                showToast('✅ Travailleur supprimé avec succès', 'success');
            } catch (error) {
                console.error('Error deleting worker:', error);
                alert('❌ Erreur lors de la suppression');
            }
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
            showToast('📁 Export terminé', 'success');
        }

        /**
         * Afficher une notification
         */
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: ${type === 'success' ? '#10b981' : '#3b82f6'};
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                z-index: 9999;
                animation: slideUp 0.3s ease;
            `;
            toast.innerHTML = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
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
        document.getElementById('searchInput').addEventListener('input', filterWorkers);
        document.getElementById('statusFilter').addEventListener('change', filterWorkers);
        document.getElementById('departmentFilter').addEventListener('change', filterWorkers);
        document.getElementById('exportBtn').addEventListener('click', exportWorkers);

        // Fermer le modal en cliquant à l'extérieur
        window.onclick = function(event) {
            const modal = document.getElementById('workerModal');
            if (event.target === modal) {
                closeWorkerModal();
            }
        };

        // Initialisation
        document.addEventListener('DOMContentLoaded', () => {
            loadWorkers();
            
            // Recharger toutes les 30 secondes
            setInterval(loadWorkers, 30000);
        });