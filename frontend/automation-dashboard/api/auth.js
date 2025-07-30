/**
 * Authentication Service
 * 
 * Handles user authentication, token management, and session persistence.
 */

import API_CONFIG from './config';

class AuthService {
    constructor() {
        this.tokenKey = 'encompass_auth_token';
        this.refreshTokenKey = 'encompass_refresh_token';
        this.userKey = 'encompass_user';
        this.tokenExpiryKey = 'encompass_token_expiry';
        
        // Bind methods
        this.login = this.login.bind(this);
        this.logout = this.logout.bind(this);
        this.getCurrentUser = this.getCurrentUser.bind(this);
        this.getAuthToken = this.getAuthToken.bind(this);
        this.isAuthenticated = this.isAuthenticated.bind(this);
        this.refreshToken = this.refreshToken.bind(this);
        this._checkTokenExpiry = this._checkTokenExpiry.bind(this);
    }
    
    /**
     * Log in a user with email and password
     * @param {string} email - User's email
     * @param {string} password - User's password
     * @returns {Promise<Object>} - User data and tokens
     */
    async login(email, password) {
        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.AUTH.LOGIN}`, {
                method: 'POST',
                headers: API_CONFIG.HEADERS,
                body: JSON.stringify({ email, password })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Login failed');
            }
            
            const data = await response.json();
            
            // Store tokens and user data
            this._setSession(data);
            
            return data.user;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }
    
    /**
     * Log out the current user
     */
    logout() {
        // Call the logout endpoint to invalidate the token
        fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.AUTH.LOGOUT}`, {
            method: 'POST',
            headers: {
                ...API_CONFIG.HEADERS,
                'Authorization': `Bearer ${this.getAuthToken()}`
            }
        }).catch(error => {
            console.error('Logout error:', error);
        });
        
        // Clear local storage
        this._clearSession();
    }
    
    /**
     * Get the current authenticated user
     * @returns {Object|null} - User object or null if not authenticated
     */
    getCurrentUser() {
        const user = localStorage.getItem(this.userKey);
        return user ? JSON.parse(user) : null;
    }
    
    /**
     * Get the authentication token
     * @returns {string|null} - JWT token or null if not available
     */
    getAuthToken() {
        return localStorage.getItem(this.tokenKey);
    }
    
    /**
     * Check if the user is authenticated
     * @returns {boolean} - True if authenticated, false otherwise
     */
    isAuthenticated() {
        const token = this.getAuthToken();
        return !!token && !this._isTokenExpired();
    }
    
    /**
     * Refresh the authentication token
     * @returns {Promise<boolean>} - True if token was refreshed, false otherwise
     */
    async refreshToken() {
        const refreshToken = localStorage.getItem(this.refreshTokenKey);
        
        if (!refreshToken) {
            this._clearSession();
            return false;
        }
        
        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.AUTH.REFRESH}`, {
                method: 'POST',
                headers: API_CONFIG.HEADERS,
                body: JSON.stringify({ refreshToken })
            });
            
            if (!response.ok) {
                throw new Error('Token refresh failed');
            }
            
            const data = await response.json();
            this._setSession(data);
            return true;
            
        } catch (error) {
            console.error('Token refresh error:', error);
            this._clearSession();
            return false;
        }
    }
    
    /**
     * Get authentication headers with the current token
     * @returns {Object} - Headers object with authorization
     */
    getAuthHeaders() {
        return {
            ...API_CONFIG.HEADERS,
            'Authorization': `Bearer ${this.getAuthToken()}`
        };
    }
    
    /**
     * Check if the current token is expired
     * @private
     * @returns {boolean} - True if token is expired, false otherwise
     */
    _isTokenExpired() {
        const expiry = localStorage.getItem(this.tokenExpiryKey);
        if (!expiry) return true;
        
        return Date.now() >= parseInt(expiry, 10);
    }
    
    /**
     * Set the authentication session
     * @private
     * @param {Object} data - Authentication response data
     */
    _setSession(data) {
        const { token, refreshToken, user, expiresIn } = data;
        const expiryTime = Date.now() + (expiresIn * 1000);
        
        localStorage.setItem(this.tokenKey, token);
        localStorage.setItem(this.refreshTokenKey, refreshToken);
        localStorage.setItem(this.userKey, JSON.stringify(user));
        localStorage.setItem(this.tokenExpiryKey, expiryTime.toString());
        
        // Set up token refresh before it expires (5 minutes before)
        const refreshTime = (expiresIn - 300) * 1000; // 5 minutes before expiry
        
        // Clear any existing refresh timeout
        if (this._refreshTimeout) {
            clearTimeout(this._refreshTimeout);
        }
        
        this._refreshTimeout = setTimeout(() => {
            this.refreshToken();
        }, refreshTime);
    }
    
    /**
     * Clear the authentication session
     * @private
     */
    _clearSession() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshTokenKey);
        localStorage.removeItem(this.userKey);
        localStorage.removeItem(this.tokenExpiryKey);
        
        if (this._refreshTimeout) {
            clearTimeout(this._refreshTimeout);
        }
    }
    
    /**
     * Check token expiry and refresh if needed
     * @private
     * @returns {Promise<boolean>} - True if token is valid or was refreshed
     */
    async _checkTokenExpiry() {
        if (!this.isAuthenticated()) {
            if (this._isTokenExpired()) {
                return await this.refreshToken();
            }
            return false;
        }
        return true;
    }
}

// Create a singleton instance
export default new AuthService();
