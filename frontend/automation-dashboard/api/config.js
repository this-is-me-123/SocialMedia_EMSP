/**
 * API Configuration
 * 
 * This file contains all the configuration settings for the API endpoints
 * and authentication services used throughout the application.
 */

const API_CONFIG = {
    // Base API URL - will be different in development/production
    BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
    
    // Authentication endpoints
    AUTH: {
        LOGIN: '/auth/login',
        LOGOUT: '/auth/logout',
        REFRESH: '/auth/refresh',
        PROFILE: '/auth/me'
    },
    
    // Social media endpoints
    SOCIAL: {
        // Posts
        POSTS: {
            BASE: '/posts',
            SCHEDULE: '/posts/schedule',
            DRAFTS: '/posts/drafts',
            PUBLISHED: '/posts/published',
            BY_ID: (id) => `/posts/${id}`,
            PUBLISH: (id) => `/posts/${id}/publish`,
            ANALYTICS: (id) => `/posts/${id}/analytics`
        },
        
        // Media
        MEDIA: {
            UPLOAD: '/media/upload',
            BY_ID: (id) => `/media/${id}`,
            DELETE: (id) => `/media/${id}`
        },
        
        // Analytics
        ANALYTICS: {
            OVERVIEW: '/analytics/overview',
            ENGAGEMENT: '/analytics/engagement',
            AUDIENCE: '/analytics/audience',
            POSTS: '/analytics/posts'
        },
        
        // Integrations
        INTEGRATIONS: {
            LIST: '/integrations',
            CONNECT: (platform) => `/integrations/${platform}/connect`,
            DISCONNECT: (platform) => `/integrations/${platform}/disconnect`,
            STATUS: (platform) => `/integrations/${platform}/status`
        }
    },
    
    // WordPress integration endpoints
    WORDPRESS: {
        BASE: '/wordpress',
        SITE_INFO: '/wordpress/site-info',
        SYNC: '/wordpress/sync',
        FEEDBACK: {
            BASE: '/wordpress/feedback',
            BY_ID: (id) => `/wordpress/feedback/${id}`,
            STATS: '/wordpress/feedback/stats'
        }
    },
    
    // Default request headers
    HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    
    // Default timeout for requests (in milliseconds)
    TIMEOUT: 30000,
    
    // Maximum number of retries for failed requests
    MAX_RETRIES: 3,
    
    // Default pagination settings
    PAGINATION: {
        PAGE_SIZE: 10,
        MAX_PAGE_SIZE: 100
    },
    
    // Cache settings (in milliseconds)
    CACHE: {
        ENABLED: true,
        DEFAULT_TTL: 300000, // 5 minutes
        PREFIX: 'encompass_'
    },
    
    // Feature flags
    FEATURES: {
        ANALYTICS: true,
        SCHEDULING: true,
        MEDIA_UPLOAD: true,
        MULTI_ACCOUNT: false
    },
    
    // Social media platforms configuration
    PLATFORMS: {
        FACEBOOK: {
            ENABLED: true,
            API_VERSION: 'v15.0',
            PERMISSIONS: ['pages_manage_posts', 'pages_read_engagement']
        },
        INSTAGRAM: {
            ENABLED: true,
            API_VERSION: 'v15.0',
            PERMISSIONS: ['instagram_basic', 'instagram_content_publish', 'pages_show_list']
        },
        TWITTER: {
            ENABLED: true,
            API_VERSION: '2',
            SCOPES: ['tweet.read', 'tweet.write', 'users.read', 'offline.access']
        },
        TIKTOK: {
            ENABLED: true,
            API_VERSION: 'v1.3',
            SCOPES: ['user.info.basic', 'video.upload', 'video.publish']
        },
        LINKEDIN: {
            ENABLED: false,
            API_VERSION: 'v2',
            SCOPES: ['r_liteprofile', 'w_member_social', 'r_emailaddress']
        }
    },
    
    // Default timezone for scheduling
    TIMEZONE: 'America/New_York',
    
    // Logging configuration
    LOGGING: {
        LEVEL: process.env.NODE_ENV === 'production' ? 'error' : 'debug',
        CONSOLE: true,
        FILE: process.env.NODE_ENV === 'production',
        MAX_FILE_SIZE: '10m',
        MAX_FILES: '14d'
    },
    
    // Environment detection
    isProduction: process.env.NODE_ENV === 'production',
    isDevelopment: process.env.NODE_ENV === 'development',
    isTest: process.env.NODE_ENV === 'test',
    
    // Helper methods
    getPlatformConfig: (platform) => {
        const platformKey = platform.toUpperCase();
        return API_CONFIG.PLATFORMS[platformKey] || null;
    },
    
    isPlatformEnabled: (platform) => {
        const config = API_CONFIG.getPlatformConfig(platform);
        return config ? config.ENABLED : false;
    },
    
    // API versioning
    VERSIONS: {
        V1: 'v1',
        V2: 'v2',
        CURRENT: 'v1'
    },
    
    // Default error messages
    ERROR_MESSAGES: {
        NETWORK: 'Unable to connect to the server. Please check your internet connection.',
        TIMEOUT: 'Request timed out. Please try again.',
        UNAUTHORIZED: 'Your session has expired. Please log in again.',
        FORBIDDEN: 'You do not have permission to access this resource.',
        NOT_FOUND: 'The requested resource was not found.',
        SERVER_ERROR: 'An unexpected error occurred. Please try again later.',
        VALIDATION: 'Please check your input and try again.'
    }
};

export default API_CONFIG;
