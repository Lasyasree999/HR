/**
 * ============================================================
 * HireGenius AI — Authentication Module
 * ============================================================
 * Login, logout, session management, and auth guards.
 * ============================================================
 */

class Auth {
    /**
     * Login with username and password.
     */
    static async login(username, password) {
        const response = await API.post('/auth/login', { username, password });
        if (response.access_token) {
            localStorage.setItem('hg_token', response.access_token);
            localStorage.setItem('hg_user', JSON.stringify(response.user));
            return response;
        }
        throw new Error('Login failed: no token received');
    }

    /**
     * Logout — clear session and redirect.
     */
    static logout() {
        localStorage.removeItem('hg_token');
        localStorage.removeItem('hg_user');
        window.location.href = '/login';
    }

    /**
     * Check if user is authenticated.
     */
    static isAuthenticated() {
        return !!localStorage.getItem('hg_token');
    }

    /**
     * Get current user from localStorage.
     */
    static getUser() {
        const userData = localStorage.getItem('hg_user');
        return userData ? JSON.parse(userData) : null;
    }

    /**
     * Auth guard — redirect to login if not authenticated.
     * Call this at the top of every protected page.
     */
    static guard() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    }

    /**
     * Check if current user is admin.
     */
    static isAdmin() {
        const user = this.getUser();
        return user?.role === 'admin';
    }
}

window.Auth = Auth;
