/**
 * ============================================================
 * HireGenius AI — API Client
 * ============================================================
 * Centralized fetch wrapper with JWT auth, error handling,
 * and response parsing.
 * ============================================================
 */

const API_BASE = '/api';

class APIClient {
    /**
     * Get stored JWT token.
     */
    static getToken() {
        return localStorage.getItem('hg_token');
    }

    /**
     * Build request headers with JWT authentication.
     */
    static getHeaders(isFormData = false) {
        const headers = {};
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        if (!isFormData) {
            headers['Content-Type'] = 'application/json';
        }
        return headers;
    }

    /**
     * Handle API response, throw on errors.
     */
    static async handleResponse(response) {
        if (response.status === 401) {
            localStorage.removeItem('hg_token');
            localStorage.removeItem('hg_user');
            window.location.href = '/login';
            throw new Error('Session expired. Please login again.');
        }

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            const message = data?.detail || data?.message || `Error ${response.status}`;
            throw new Error(message);
        }

        return data;
    }

    /**
     * GET request.
     */
    static async get(endpoint) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'GET',
            headers: this.getHeaders(),
        });
        return this.handleResponse(response);
    }

    /**
     * POST request (JSON body).
     */
    static async post(endpoint, data = {}) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });
        return this.handleResponse(response);
    }

    /**
     * PUT request (JSON body).
     */
    static async put(endpoint, data = {}) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });
        return this.handleResponse(response);
    }

    /**
     * DELETE request.
     */
    static async delete(endpoint) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });
        return this.handleResponse(response);
    }

    /**
     * POST request with FormData (file uploads).
     */
    static async upload(endpoint, formData) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.getToken()}`,
            },
            body: formData,
        });
        return this.handleResponse(response);
    }
}

// Export globally
window.API = APIClient;
