/**
 * Encompass Analytics - Frontend Tracking
 */
(function($) {
    'use strict';

    // Wait for DOM to be ready
    $(document).ready(function() {
        // Only initialize if tracking is enabled
        if (typeof encompassAnalytics === 'undefined') {
            return;
        }

        // Initialize the tracker
        const tracker = new EncompassAnalytics();
        tracker.init();
    });

    /**
     * Main tracking class
     */
    class EncompassAnalytics {
        constructor() {
            this.settings = encompassAnalytics || {};
            this.sessionId = this.getSessionId();
            this.pageStartTime = new Date().getTime();
            this.timeOnPageTimer = null;
            this.scrollDepthTracked = false;
            this.lastTrackedTime = 0;
            this.throttleDelay = 1000; // 1 second throttle for events
            this.scrollDepths = [25, 50, 75, 90];
            this.trackedScrollDepths = [];
        }

        /**
         * Initialize tracking
         */
        init() {
            // Track page view
            this.trackPageView();

            // Set up event listeners
            this.setupEventListeners();

            // Track time on page
            if (this.settings.trackTimeOnPage) {
                this.setupTimeOnPageTracking();
            }

            // Track scroll depth
            if (this.settings.trackScroll) {
                this.setupScrollTracking();
            }

            // Track outbound links
            if (this.settings.trackOutboundLinks) {
                this.setupOutboundLinkTracking();
            }

            // Track downloads
            if (this.settings.trackDownloads) {
                this.setupDownloadTracking();
            }

            // Track form submissions
            if (this.settings.trackForms) {
                this.setupFormTracking();
            }

            // Track video interactions
            if (this.settings.trackVideos) {
                this.setupVideoTracking();
            }

            // Track clicks if enabled
            if (this.settings.trackClicks) {
                this.setupClickTracking();
            }
        }

        /**
         * Get or create a session ID
         */
        getSessionId() {
            let sessionId = this.getCookie('_encompass_session');
            if (!sessionId) {
                sessionId = this.generateUUID();
                this.setCookie('_encompass_session', sessionId, 30); // 30 days
            }
            return sessionId;
        }

        /**
         * Generate a UUID v4
         */
        generateUUID() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        }

        /**
         * Set a cookie
         */
        setCookie(name, value, days) {
            let expires = '';
            if (days) {
                const date = new Date();
                date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                expires = '; expires=' + date.toUTCString();
            }
            document.cookie = name + '=' + (value || '') + expires + '; path=/';
        }

        /**
         * Get a cookie value by name
         */
        getCookie(name) {
            const nameEQ = name + '=';
            const ca = document.cookie.split(';');
            for (let i = 0; i < ca.length; i++) {
                let c = ca[i];
                while (c.charAt(0) === ' ') c = c.substring(1, c.length);
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
            }
            return null;
        }

        /**
         * Track a page view
         */
        trackPageView() {
            const pageData = {
                url: window.location.href,
                referrer: document.referrer || '',
                title: document.title,
                path: window.location.pathname,
                search: window.location.search,
                hash: window.location.hash,
                screen_width: window.screen.width,
                screen_height: window.screen.height,
                viewport_width: window.innerWidth,
                viewport_height: window.innerHeight,
                color_depth: window.screen.colorDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                language: navigator.language,
                user_agent: navigator.userAgent,
                is_mobile: /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent),
                is_retina: window.devicePixelRatio > 1,
                time_on_page: 0
            };

            this.sendEvent('page_view', pageData);
        }

        /**
         * Track an event
         */
        trackEvent(category, action, label = '', value = null) {
            const eventData = {
                category: category,
                action: action,
                label: label,
                value: value,
                url: window.location.href,
                timestamp: new Date().toISOString()
            };

            this.sendEvent('event', eventData);
        }

        /**
         * Send event to the server
         */
        sendEvent(eventType, eventData) {
            // Throttle events
            const now = new Date().getTime();
            if (now - this.lastTrackedTime < this.throttleDelay) {
                return;
            }
            this.lastTrackedTime = now;

            // Add session and page info
            eventData = Object.assign({
                session_id: this.sessionId,
                page_title: document.title,
                page_url: window.location.href,
                timestamp: new Date().toISOString()
            }, eventData);

            // Use navigator.sendBeacon if available for better performance
            if (navigator.sendBeacon && this.settings.apiUrl) {
                const blob = new Blob(
                    [JSON.stringify({
                        event: eventType,
                        data: eventData,
                        _wpnonce: this.settings.nonce
                    })],
                    { type: 'application/json' }
                );
                
                navigator.sendBeacon(
                    this.settings.apiUrl + 'events',
                    blob
                );
            } else {
                // Fallback to AJAX
                $.ajax({
                    url: this.settings.apiUrl + 'events',
                    type: 'POST',
                    data: JSON.stringify({
                        event: eventType,
                        data: eventData,
                        _wpnonce: this.settings.nonce
                    }),
                    contentType: 'application/json',
                    dataType: 'json'
                });
            }
        }

        /**
         * Set up time on page tracking
         */
        setupTimeOnPageTracking() {
            // Track time on page before unload
            window.addEventListener('beforeunload', () => {
                const timeOnPage = Math.round((new Date().getTime() - this.pageStartTime) / 1000);
                this.sendEvent('time_on_page', {
                    time_on_page: timeOnPage,
                    url: window.location.href,
                    title: document.title
                });
            });

            // Also track periodically in case the beforeunload event doesn't fire
            setInterval(() => {
                const timeOnPage = Math.round((new Date().getTime() - this.pageStartTime) / 1000);
                // Only send if the user has been on the page for at least 10 seconds
                if (timeOnPage >= 10 && timeOnPage % 30 === 0) { // Every 30 seconds after 10 seconds
                    this.sendEvent('time_on_page', {
                        time_on_page: timeOnPage,
                        url: window.location.href,
                        title: document.title
                    });
                }
            }, 10000); // Check every 10 seconds
        }

        /**
         * Set up scroll depth tracking
         */
        setupScrollTracking() {
            const self = this;
            const $window = $(window);
            const $document = $(document);
            const windowHeight = $window.height();
            const documentHeight = $document.height();
            const scrollHeight = documentHeight - windowHeight;

            // Check scroll depth on scroll
            $window.on('scroll', this.throttle(function() {
                const scrollTop = $window.scrollTop();
                const scrollPercentage = Math.round((scrollTop / scrollHeight) * 100);
                
                // Track scroll depth milestones
                self.scrollDepths.forEach(depth => {
                    if (scrollPercentage >= depth && !self.trackedScrollDepths.includes(depth)) {
                        self.trackEvent('scroll', 'scroll_depth', depth + '%');
                        self.trackedScrollDepths.push(depth);
                    }
                });
            }, 250));
        }

        /**
         * Set up outbound link tracking
         */
        setupOutboundLinkTracking() {
            const self = this;
            
            // Handle clicks on all links
            $(document).on('click', 'a[href^="http"]', function(e) {
                const link = this;
                const href = link.href;
                const currentDomain = window.location.hostname;
                
                // Skip if it's not an outbound link
                if (href.indexOf(currentDomain) !== -1 || 
                    href.indexOf('javascript:') === 0 || 
                    href.indexOf('mailto:') === 0 || 
                    href.indexOf('tel:') === 0) {
                    return;
                }
                
                // Track the outbound link
                self.trackEvent('outbound', 'click', href);
                
                // Small delay to ensure the event is tracked before navigating away
                if (!e.ctrlKey && !e.shiftKey && !e.metaKey) {
                    e.preventDefault();
                    
                    setTimeout(() => {
                        window.location.href = href;
                    }, 100);
                }
            });
        }

        /**
         * Set up download tracking
         */
        setupDownloadTracking() {
            const self = this;
            const downloadExtensions = [
                // Documents
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp', 'odg', 'odc', 'odf', 'odb', 'odm', 'ott', 'ots', 'otp', 'otg', 'otc', 'odf', 'odi', 'odm', 'rtf', 'txt', 'csv',
                // Archives
                'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'iso',
                // Executables
                'exe', 'dmg', 'pkg', 'msi', 'apk',
                // Media
                'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp', 'tiff', 'mp3', 'wav', 'ogg', 'mp4', 'webm', 'mov', 'avi', 'wmv', 'flv', 'mkv'
            ];
            
            const downloadPattern = new RegExp('\.(' + downloadExtensions.join('|') + ')([?&#]|$)', 'i');
            
            $(document).on('click', 'a', function() {
                const href = this.href;
                
                if (downloadPattern.test(href)) {
                    const fileName = href.split('/').pop().split('?')[0];
                    self.trackEvent('download', 'click', fileName, {
                        file_url: href,
                        file_extension: fileName.split('.').pop().toLowerCase(),
                        link_text: $(this).text().trim() || $(this).find('img').attr('alt') || 'N/A'
                    });
                }
            });
        }

        /**
         * Set up form tracking
         */
        setupFormTracking() {
            const self = this;
            
            // Track form submissions
            $(document).on('submit', 'form', function() {
                const $form = $(this);
                const formId = $form.attr('id') || 'unknown';
                const formAction = $form.attr('action') || window.location.href;
                const formMethod = $form.attr('method') || 'get';
                
                // Get form data
                const formData = {};
                $form.serializeArray().forEach(item => {
                    formData[item.name] = item.value;
                });
                
                // Track the form submission
                self.trackEvent('form', 'submit', formId, {
                    form_action: formAction,
                    form_method: formMethod,
                    form_fields: Object.keys(formData),
                    form_data: formData
                });
            });
        }

        /**
         * Set up video tracking
         */
        setupVideoTracking() {
            const self = this;
            
            // Track HTML5 video events
            $('video').each(function() {
                const $video = $(this);
                const videoSrc = $video.attr('src') || $video.find('source').attr('src') || 'unknown';
                let videoTitle = $video.attr('title') || $video.attr('aria-label') || 'Untitled Video';
                let lastPlayTime = 0;
                
                $video.on('play', function() {
                    self.trackEvent('video', 'play', videoTitle, {
                        video_src: videoSrc,
                        current_time: this.currentTime,
                        duration: this.duration || 0
                    });
                });
                
                $video.on('pause', function() {
                    self.trackEvent('video', 'pause', videoTitle, {
                        video_src: videoSrc,
                        current_time: this.currentTime,
                        duration: this.duration || 0
                    });
                });
                
                $video.on('ended', function() {
                    self.trackEvent('video', 'complete', videoTitle, {
                        video_src: videoSrc,
                        duration: this.duration || 0
                    });
                });
                
                // Track time update (every 5 seconds)
                $video.on('timeupdate', function() {
                    const currentTime = Math.floor(this.currentTime);
                    
                    // Only track every 5 seconds
                    if (currentTime > 0 && currentTime % 5 === 0 && currentTime !== lastPlayTime) {
                        lastPlayTime = currentTime;
                        
                        // Calculate percentage watched
                        const percentWatched = this.duration > 0 ? 
                            Math.round((currentTime / this.duration) * 100) : 0;
                        
                        self.trackEvent('video', 'progress', videoTitle, {
                            video_src: videoSrc,
                            current_time: currentTime,
                            duration: this.duration || 0,
                            percent_watched: percentWatched
                        });
                    }
                });
            });
            
            // Track YouTube embeds
            if (typeof YT !== 'undefined') {
                // This would be extended to track YouTube player events
                // using the YouTube IFrame API
            }
        }

        /**
         * Set up click tracking
         */
        setupClickTracking() {
            const self = this;
            
            $(document).on('click', '*', function(e) {
                const $target = $(this);
                const tagName = this.tagName.toLowerCase();
                
                // Skip if it's a link, button, or form element (handled elsewhere)
                if (['a', 'button', 'input', 'select', 'textarea'].includes(tagName)) {
                    return;
                }
                
                // Get element info
                const elementId = $target.attr('id') || '';
                const elementClass = $target.attr('class') || '';
                const elementText = $target.text().trim().substring(0, 100);
                const elementPath = self.getElementPath(this);
                
                // Track the click
                self.trackEvent('element', 'click', elementPath, {
                    element_id: elementId,
                    element_class: elementClass,
                    element_text: elementText,
                    element_tag: tagName,
                    page_x: e.pageX,
                    page_y: e.pageY,
                    client_x: e.clientX,
                    client_y: e.clientY,
                    screen_x: e.screenX,
                    screen_y: e.screenY
                });
            });
        }

        /**
         * Get the DOM path of an element
         */
        getElementPath(element) {
            if (!element || !element.nodeName) return '';
            
            const path = [];
            while (element && element.nodeType === Node.ELEMENT_NODE) {
                let selector = element.nodeName.toLowerCase();
                
                if (element.id) {
                    selector += '#' + element.id;
                    path.unshift(selector);
                    break;
                } else {
                    let sibling = element;
                    let nth = 1;
                    
                    while (sibling = sibling.previousElementSibling) {
                        if (sibling.nodeName.toLowerCase() === selector) {
                            nth++;
                        }
                    }
                    
                    if (nth !== 1) {
                        selector += ':nth-of-type(' + nth + ')';
                    } else {
                        const tagName = element.nodeName.toLowerCase();
                        if (tagName !== 'body' && tagName !== 'html') {
                            selector += ':nth-of-type(1)';
                        }
                    }
                }
                
                path.unshift(selector);
                element = element.parentNode;
            }
            
            return path.join(' > ');
        }

        /**
         * Throttle function calls to improve performance
         */
        throttle(func, limit) {
            let inThrottle;
            const self = this;
            
            return function() {
                const args = arguments;
                const context = self;
                
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    }

})(jQuery);
