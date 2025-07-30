/**
 * API Service
 * 
 * Centralized service for making HTTP requests with authentication and error handling.
 */

import API_CONFIG from './config';
import AuthService from './auth';

class ApiService {
    constructor() {
        this.pendingRequests = [];
        this.isRefreshing = false;
    }

    /**
     * Make an authenticated API request
     * @param {string} method - HTTP method (GET, POST, PUT, DELETE, etc.)
     * @param {string} endpoint - API endpoint (without base URL)
     * @param {Object} data - Request payload (for POST, PUT, PATCH)
     * @param {Object} options - Additional options (headers, params, etc.)
     * @returns {Promise<Object>} - Response data
     */
    async request(method, endpoint, data = null, options = {}) {
        const url = this._buildUrl(endpoint, options.params);
        const headers = this._getHeaders(options.headers);
        
        const config = {
            method,
            headers,
            ...options,
            signal: options.signal || this._createAbortSignal(options.timeout)
        };

        if (data && method !== 'GET' && method !== 'HEAD') {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            
            // Handle 401 Unauthorized - try to refresh token and retry
            if (response.status === 401 && !options._retry) {
                return this._handleUnauthorized(method, endpoint, data, options);
            }
            
            return this._handleResponse(response);
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error(API_CONFIG.ERROR_MESSAGES.TIMEOUT);
            }
            throw error;
        }
    }

    /**
     * Make a GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} params - Query parameters
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Response data
     */
    get(endpoint, params = {}, options = {}) {
        return this.request('GET', endpoint, null, { ...options, params });
    }

    /**
     * Make a POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request payload
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Response data
     */
    post(endpoint, data = {}, options = {}) {
        return this.request('POST', endpoint, data, options);
    }

    /**
     * Make a PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request payload
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Response data
     */
    put(endpoint, data = {}, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }

    /**
     * Make a PATCH request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request payload
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Response data
     */
    patch(endpoint, data = {}, options = {}) {
        return this.request('PATCH', endpoint, data, options);
    }

    /**
     * Make a DELETE request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Response data
     */
    delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }

    /**
     * Upload a file
     * @param {string} endpoint - API endpoint
     * @ {FormData} formData - Form data with file
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Upload response
     */
    async upload(endpoint, formData, options = {}) {
        const headers = this._getHeaders({
            ...options.headers,
            'Content-Type': 'multipart/form-data'
        });
        
        // Remove Content-Type to let the browser set it with the correct boundary
        delete headers['Content-Type'];
        
        return this.request('POST', endpoint, formData, {
            ...options,
            headers
        });
    }

    /**
     * Build full URL with query parameters
     * @private
     */
    _buildUrl(endpoint, params = {}) {
        const url = new URL(`${API_CONFIG.BASE_URL}${endpoint}`);
        
        // Add query parameters
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                if (Array.isArray(value)) {
                    value.forEach(v => url.searchParams.append(`${key}[]`, v));
                } else {
                    url.searchParams.append(key, value);
                }
            }
        });
        
        return url.toString();
    }

    /**
     * Get request headers with authentication
     * @private
     */
    _getHeaders(customHeaders = {}) {
        const headers = {
            ...API_CONFIG.HEADERS,
            ...customHeaders
        };
        
        // Add auth token if available
        const token = AuthService.getAuthToken();
        if (token && !headers['Authorization']) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }

    /**
     * Handle API response
     * @private
     */
    async _handleResponse(response) {
        const contentType = response.headers.get('content-type');
        const isJson = contentType && contentType.includes('application/json');
        
        if (!response.ok) {
            const errorData = isJson ? await response.json() : await response.text();
            const error = new Error(errorData.message || API_CONFIG.ERROR_MESSAGES.SERVER_ERROR);
            error.status = response.status;
            error.data = errorData;
            throw error;
        }
        
        return isJson ? response.json() : response.text();
    }

    /**
     * Handle 401 Unauthorized response
     * @private
     */
    async _handleUnauthorized(method, endpoint, data, options) {
        // If we're already refreshing, add the request to the queue
        if (this.isRefreshing) {
            return new Promise((resolve, reject) => {
                this.pendingRequests.push({ resolve, reject });
            }).then(() => this.request(method, endpoint, data, { ...options, _retry: true }));
        }

        this.isRefreshing = true;

        try {
            // Try to refresh the token
            const refreshed = await AuthService.refreshToken();
            
            if (!refreshed) {
                throw new Error('Token refresh failed');
            }
            
            // Retry all pending requests
            this.pendingRequests.forEach(({ resolve }) => resolve());
            this.pendingRequests = [];
            
            // Retry the original request
            return this.request(method, endpoint, data, { ...options, _retry: true });
            
        } catch (error) {
            // If refresh fails, reject all pending requests and log out
            this.pendingRequests.forEach(({ reject }) => reject(error));
            this.pendingRequests = [];
            
            // Log out the user if token refresh fails
            if (AuthService.isAuthenticated()) {
                AuthService.logout();
                window.location.href = '/login';
            }
            
            throw error;
            
        } finally {
            this.isRefreshing = false;
        }
    }

    /**
     * Create an AbortController with timeout
     * @private
     */
    _createAbortSignal(timeout = API_CONFIG.TIMEOUT) {
        const controller = new AbortController();
        
        // Auto-abort after timeout
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, timeout);
        
        // Clean up the timeout when the signal is aborted
        controller.signal.addEventListener('abort', () => {
            clearTimeout(timeoutId);
        });
        
        return controller.signal;
    }
}

// Create a singleton instance
export default new ApiService();
