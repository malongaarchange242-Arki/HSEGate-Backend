/**
 * API Client pour HSEGate
 * Gère la communication avec le backend FastAPI
 */

const API_ORIGIN = 'http://localhost:8000';
const API_BASE_URL = `${API_ORIGIN}/api/v1`;
const ADMIN_EMAIL = 'admin@hsegate.com';
const ADMIN_PASSWORD = 'admin123';

let authToken = localStorage.getItem('authToken');

/**
 * Classe pour gérer les appels API
 */
class HSEGateAPI {
    constructor() {
        this.token = localStorage.getItem('authToken');
    }

    /**
     * Authentifier l'utilisateur admin
     */
    async authenticate() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: ADMIN_EMAIL,
                    password: ADMIN_PASSWORD,
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Authentication failed');
            }

            const data = await response.json();
            this.token = data.access_token;
            localStorage.setItem('authToken', this.token);
            console.log('✅ Authentication successful');
            return data;
        } catch (error) {
            console.error('❌ Authentication error:', error);
            throw error;
        }
    }

    /**
     * Vérifier et renouveler le token si nécessaire
     */
    async ensureAuthenticated() {
        if (!this.token) {
            await this.authenticate();
        }
    }

    async _fetchWithAuth(url, options = {}) {
        await this.ensureAuthenticated();

        options.headers = {
            ...(options.headers || {}),
            Authorization: `Bearer ${this.token}`,
        };

        let response = await fetch(url, options);

        if (response.status === 401) {
            console.warn('⚠️ Token expired or invalid, re-authenticating...');
            localStorage.removeItem('authToken');
            this.token = null;
            await this.authenticate();

            options.headers.Authorization = `Bearer ${this.token}`;
            response = await fetch(url, options);
        }

        return response;
    }

    /**
     * Créer un nouveau travailleur
     */
    async createWorker(workerData) {
        await this.ensureAuthenticated();

        try {
            const response = await this._fetchWithAuth(`${API_BASE_URL}/workers`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(workerData),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to create worker');
            }

            const data = await response.json();
            console.log('✅ Worker created successfully');
            return data;
        } catch (error) {
            console.error('❌ Error creating worker:', error);
            throw error;
        }
    }

    /**
     * Récupérer tous les travailleurs
     */
    async getWorkers() {
        await this.ensureAuthenticated();

        try {
            const response = await this._fetchWithAuth(`${API_BASE_URL}/workers`, {
                method: 'GET',
            });

            if (!response.ok) {
                throw new Error('Failed to fetch workers');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('❌ Error fetching workers:', error);
            throw error;
        }
    }

    /**
     * Récupérer un travailleur par ID
     */
    async getWorker(id) {
        await this.ensureAuthenticated();

        try {
            const response = await this._fetchWithAuth(`${API_BASE_URL}/workers/${id}`, {
                method: 'GET',
            });

            if (!response.ok) {
                throw new Error('Failed to fetch worker');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('❌ Error fetching worker:', error);
            throw error;
        }
    }

    /**
     * Enregistrer la photo de face d'un travailleur
     */
    async registerWorkerFace(workerId, faceImageBase64) {
        await this.ensureAuthenticated();

        try {
            const response = await this._fetchWithAuth(
                `${API_BASE_URL}/workers/${workerId}/face`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        face_image_base64: faceImageBase64,
                    }),
                }
            );

            if (!response.ok) {
                throw new Error('Failed to register face');
            }

            const data = await response.json();
            console.log('✅ Face registered successfully');
            return data;
        } catch (error) {
            console.error('❌ Error registering face:', error);
            throw error;
        }
    }

    /**
     * Télécharger le QR code
     */
    async downloadQRCode(workerId, workerUUID) {
        await this.ensureAuthenticated();

        try {
            const response = await this._fetchWithAuth(
                `${API_BASE_URL}/workers/${workerId}/qrcode`,
                {
                    method: 'GET',
                }
            );

            if (!response.ok) {
                throw new Error('Failed to download QR code');
            }

            return response.blob();
        } catch (error) {
            console.error('❌ Error downloading QR code:', error);
            throw error;
        }
    }

    /**
     * Télécharger le badge
     */
    async downloadBadge(workerId, workerUUID) {
        await this.ensureAuthenticated();

        try {
            const response = await this._fetchWithAuth(
                `${API_BASE_URL}/workers/${workerId}/badge`,
                {
                    method: 'GET',
                }
            );

            if (!response.ok) {
                throw new Error('Failed to download badge');
            }

            return response.blob();
        } catch (error) {
            console.error('❌ Error downloading badge:', error);
            throw error;
        }
    }
}

// Instanciation globale de l'API client
const api = new HSEGateAPI();

/**
 * Initialiser l'authentification au chargement
 */
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await api.ensureAuthenticated();
    } catch (error) {
        console.error('Failed to authenticate on page load:', error);
    }
});
