/**
 * Encompass Automation Dashboard - Main JavaScript
 * 
 * This file contains all the interactive functionality for the Encompass Automation Dashboard.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initSidebar();
    initCalendar();
    initCharts();
    initTabs();
    initTooltips();
    initDropdowns();
    initModals();
    initFormValidation();
    initDatePickers();
    initFileUploads();
    initNotifications();
    
    // Add any other initialization functions here
});

/**
 * Initialize sidebar functionality
 */
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    
    // Toggle sidebar on mobile
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-open');
            sidebar.classList.toggle('active');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth < 992 && !e.target.closest('.sidebar') && !e.target.closest('.sidebar-toggle')) {
            document.body.classList.remove('sidebar-open');
            sidebar.classList.remove('active');
        }
    });
    
    // Handle active state for sidebar links
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Close sidebar on mobile after clicking a link
            if (window.innerWidth < 992) {
                document.body.classList.remove('sidebar-open');
                sidebar.classList.remove('active');
            }
        });
    });
}

/**
 * Initialize calendar
 */
function initCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    if (!calendarEl) return;
    
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        height: 'auto',
        events: [
            // Sample events - in a real app, these would come from an API
            {
                title: 'IT Services Launch',
                start: new Date(),
                end: new Date(new Date().setDate(new Date().getDate() + 1)),
                backgroundColor: '#4361ee',
                borderColor: '#4361ee',
                extendedProps: {
                    platform: 'instagram',
                    type: 'post'
                }
            },
            {
                title: 'Webinar: Digital Marketing 101',
                start: new Date(new Date().setDate(new Date().getDate() + 2)),
                end: new Date(new Date().setDate(new Date().getDate() + 2)),
                allDay: true,
                backgroundColor: '#e4405f',
                borderColor: '#e4405f',
                extendedProps: {
                    platform: 'facebook',
                    type: 'event'
                }
            },
            {
                title: 'New Blog Post',
                start: new Date(new Date().setDate(new Date().getDate() + 5)),
                allDay: true,
                backgroundColor: '#17a2b8',
                borderColor: '#17a2b8',
                extendedProps: {
                    platform: 'twitter',
                    type: 'post'
                }
            }
        ],
        eventDidMount: function(info) {
            // Add platform icon to event
            const platformIcon = document.createElement('span');
            platformIcon.className = 'event-platform-icon';
            
            switch(info.event.extendedProps.platform) {
                case 'instagram':
                    platformIcon.innerHTML = '<i class="ri-instagram-line"></i>';
                    break;
                case 'facebook':
                    platformIcon.innerHTML = '<i class="ri-facebook-circle-line"></i>';
                    break;
                case 'twitter':
                    platformIcon.innerHTML = '<i class="ri-twitter-line"></i>';
                    break;
                case 'tiktok':
                    platformIcon.innerHTML = '<i class="ri-tiktok-line"></i>';
                    break;
                default:
                    platformIcon.innerHTML = '<i class="ri-share-line"></i>';
            }
            
            info.el.querySelector('.fc-event-title').prepend(platformIcon);
        },
        eventClick: function(info) {
            // Handle event click (e.g., open event details modal)
            openEventModal(info.event);
            
            // Prevent default browser navigation
            info.jsEvent.preventDefault();
        },
        datesSet: function(dateInfo) {
            // Handle view change (e.g., update URL or fetch events for the visible range)
            console.log('View changed:', dateInfo.view.type);
        }
    });
    
    calendar.render();
}

/**
 * Initialize charts
 */
function initCharts() {
    // Performance Chart
    const performanceCtx = document.getElementById('performanceChart');
    
    if (performanceCtx) {
        const performanceChart = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                datasets: [
                    {
                        label: 'Impressions',
                        data: [12000, 19000, 15000, 25000, 22000, 30000, 28000],
                        borderColor: '#4361ee',
                        backgroundColor: 'rgba(67, 97, 238, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Engagements',
                        data: [8000, 12000, 10000, 15000, 14000, 18000, 16000],
                        borderColor: '#00b4d8',
                        backgroundColor: 'rgba(0, 180, 216, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Followers',
                        data: [5000, 7500, 6000, 9000, 11000, 13000, 15000],
                        borderColor: '#4cc9f0',
                        backgroundColor: 'rgba(76, 201, 240, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: '#1e293b',
                        titleFont: {
                            size: 14,
                            weight: '500'
                        },
                        bodyFont: {
                            size: 13
                        },
                        padding: 12,
                        boxPadding: 4,
                        usePointStyle: true,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('en-US').format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(226, 232, 240, 0.5)',
                            drawBorder: false,
                            borderDash: [4, 4]
                        },
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                if (value >= 1000) {
                                    return (value / 1000) + 'k';
                                }
                                return value;
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 0,
                        hoverRadius: 6,
                        hoverBorderWidth: 2
                    }
                },
                layout: {
                    padding: {
                        top: 10,
                        right: 20,
                        bottom: 10,
                        left: 10
                    }
                }
            }
        });
    }
    
    // Platform Distribution Chart (Doughnut)
    const platformCtx = document.getElementById('platformDistributionChart');
    
    if (platformCtx) {
        const platformChart = new Chart(platformCtx, {
            type: 'doughnut',
            data: {
                labels: ['Instagram', 'Facebook', 'Twitter', 'TikTok', 'LinkedIn'],
                datasets: [{
                    data: [35, 25, 20, 15, 5],
                    backgroundColor: [
                        '#e4405f',
                        '#1877f2',
                        '#1da1f2',
                        '#000000',
                        '#0a66c2'
                    ],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            boxWidth: 8,
                            boxHeight: 8,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleFont: {
                            size: 12,
                            weight: '500'
                        },
                        bodyFont: {
                            size: 11
                        },
                        padding: 8,
                        usePointStyle: true,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${percentage}% (${value})`;
                            }
                        }
                    }
                },
                cutoutPercentage: 70
            }
        });
    }
}

/**
 * Initialize tab functionality
 */
function initTabs() {
    const tabContainers = document.querySelectorAll('.tab-container');
    
    tabContainers.forEach(container => {
        const tabs = container.querySelectorAll('.tab');
        const tabContents = container.querySelectorAll('.tab-content');
        
        tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                tab.classList.add('active');
                if (tabContents[index]) {
                    tabContents[index].classList.add('active');
                }
                
                // Update URL hash if data-tab attribute exists
                const tabId = tab.getAttribute('data-tab');
                if (tabId) {
                    window.location.hash = tabId;
                }
            });
        });
        
        // Activate tab from URL hash on page load
        if (window.location.hash) {
            const activeTab = container.querySelector(`[data-tab="${window.location.hash.substring(1)}"]`);
            if (activeTab) {
                activeTab.click();
            }
        } else if (tabs.length > 0) {
            // Activate first tab by default if no hash
            tabs[0].click();
        }
    });
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover',
            placement: 'top',
            container: 'body',
            customClass: 'custom-tooltip',
            html: true
        });
    });
}

/**
 * Initialize dropdowns
 */
function initDropdowns() {
    const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    
    dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl, {
            autoClose: true,
            boundary: 'scrollParent',
            reference: 'toggle'
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(dropdown => {
            if (!dropdown.previousElementSibling.contains(e.target)) {
                const dropdownInstance = bootstrap.Dropdown.getInstance(dropdown.previousElementSibling);
                if (dropdownInstance) {
                    dropdownInstance.hide();
                }
            }
        });
    });
}

/**
 * Initialize modals
 */
function initModals() {
    const modalElementList = [].slice.call(document.querySelectorAll('.modal'));
    
    modalElementList.map(function (modalEl) {
        return new bootstrap.Modal(modalEl, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
    });
    
    // Handle modal events
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function () {
            // Clear form when modal is closed
            const form = this.querySelector('form');
            if (form) {
                form.reset();
            }
            
            // Remove any validation errors
            const invalidFields = this.querySelectorAll('.is-invalid');
            invalidFields.forEach(field => {
                field.classList.remove('is-invalid');
            });
            
            // Clear any file previews
            const filePreviews = this.querySelectorAll('.file-preview');
            filePreviews.forEach(preview => {
                preview.innerHTML = '';
                preview.style.display = 'none';
            });
            
            // Reset file inputs
            const fileInputs = this.querySelectorAll('input[type="file"]');
            fileInputs.forEach(input => {
                input.value = '';
            });
        });
    });
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    // Example form validation for the post creation form
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Custom validation for specific fields
    const postContent = document.getElementById('postContent');
    if (postContent) {
        postContent.addEventListener('input', function() {
            if (this.value.length > 0 && this.value.length < 10) {
                this.setCustomValidity('Post content must be at least 10 characters long');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

/**
 * Initialize date pickers
 */
function initDatePickers() {
    const dateInputs = document.querySelectorAll('.datepicker');
    
    if (dateInputs.length > 0 && typeof flatpickr !== 'undefined') {
        dateInputs.forEach(input => {
            flatpickr(input, {
                enableTime: true,
                dateFormat: 'Y-m-d H:i',
                minDate: 'today',
                time_24hr: true,
                minuteIncrement: 15,
                // Add more options as needed
            });
        });
    }
}

/**
 * Initialize file uploads with preview
 */
function initFileUploads() {
    const fileInputs = document.querySelectorAll('.file-upload');
    
    fileInputs.forEach(input => {
        const previewContainer = input.nextElementSibling;
        
        input.addEventListener('change', function() {
            const files = this.files;
            
            if (files.length === 0) {
                previewContainer.innerHTML = '';
                previewContainer.style.display = 'none';
                return;
            }
            
            previewContainer.innerHTML = '';
            previewContainer.style.display = 'block';
            
            Array.from(files).forEach(file => {
                if (!file.type.match('image.*')) {
                    // Handle non-image files
                    const filePreview = document.createElement('div');
                    filePreview.className = 'file-preview-item';
                    filePreview.innerHTML = `
                        <div class="file-icon">
                            <i class="ri-file-line"></i>
                        </div>
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${formatFileSize(file.size)}</div>
                        </div>
                        <button type="button" class="btn-remove-file">
                            <i class="ri-close-line"></i>
                        </button>
                    `;
                    previewContainer.appendChild(filePreview);
                } else {
                    // Handle image files with preview
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        const imagePreview = document.createElement('div');
                        imagePreview.className = 'file-preview-item';
                        imagePreview.innerHTML = `
                            <div class="image-preview">
                                <img src="${e.target.result}" alt="${file.name}">
                            </div>
                            <div class="file-info">
                                <div class="file-name">${file.name}</div>
                                <div class="file-size">${formatFileSize(file.size)}</div>
                            </div>
                            <button type="button" class="btn-remove-file">
                                <i class="ri-close-line"></i>
                            </button>
                        `;
                        previewContainer.appendChild(imagePreview);
                    };
                    
                    reader.readAsDataURL(file);
                }
            });
            
            // Add event listeners to remove buttons
            const removeButtons = previewContainer.querySelectorAll('.btn-remove-file');
            removeButtons.forEach(button => {
                button.addEventListener('click', function() {
                    this.closest('.file-preview-item').remove();
                    
                    // If no files left, hide the preview container
                    if (previewContainer.children.length === 0) {
                        previewContainer.style.display = 'none';
                    }
                    
                    // Clear the file input
                    input.value = '';
                });
            });
        });
    });
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

/**
 * Initialize notifications
 */
function initNotifications() {
    // Example: Show welcome notification
    const welcomeNotification = {
        title: 'Welcome to Encompass Automation',
        message: 'You have successfully logged in to your dashboard.',
        type: 'success',
        duration: 5000
    };
    
    // Uncomment to show welcome notification
    // showNotification(welcomeNotification);
    
    // Handle notification button clicks
    const notificationButtons = document.querySelectorAll('[data-notification]');
    
    notificationButtons.forEach(button => {
        button.addEventListener('click', function() {
            const type = this.getAttribute('data-notification-type') || 'info';
            const title = this.getAttribute('data-notification-title') || 'Notification';
            const message = this.getAttribute('data-notification-message') || 'This is a notification message.';
            const duration = parseInt(this.getAttribute('data-notification-duration')) || 5000;
            
            showNotification({
                title: title,
                message: message,
                type: type,
                duration: duration
            });
        });
    });
}

/**
 * Show notification
 * @param {Object} options - Notification options
 * @param {string} options.title - Notification title
 * @param {string} options.message - Notification message
 * @param {string} [options.type=info] - Notification type (success, error, warning, info)
 * @param {number} [options.duration=5000] - Duration in milliseconds
 */
function showNotification({ title, message, type = 'info', duration = 5000 }) {
    const notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        // Create notification container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.setAttribute('role', 'alert');
    
    // Set icon based on notification type
    let icon = 'ri-information-line';
    
    switch (type) {
        case 'success':
            icon = 'ri-checkbox-circle-line';
            break;
        case 'error':
            icon = 'ri-close-circle-line';
            break;
        case 'warning':
            icon = 'ri-alert-line';
            break;
        default:
            icon = 'ri-information-line';
    }
    
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="${icon}"></i>
        </div>
        <div class="notification-content">
            <h4 class="notification-title">${title}</h4>
            <p class="notification-message">${message}</p>
        </div>
        <button type="button" class="notification-close">
            <i class="ri-close-line"></i>
        </button>
    `;
    
    // Add notification to container
    document.getElementById('notification-container').appendChild(notification);
    
    // Show notification with animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Auto-remove notification after duration
    const timer = setTimeout(() => {
        closeNotification(notification);
    }, duration);
    
    // Close button event
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        clearTimeout(timer);
        closeNotification(notification);
    });
    
    // Pause timer on hover
    notification.addEventListener('mouseenter', () => {
        clearTimeout(timer);
    });
    
    // Resume timer when mouse leaves
    notification.addEventListener('mouseleave', () => {
        setTimeout(() => {
            closeNotification(notification);
        }, 1000);
    });
    
    // Close notification function
    function closeNotification(notification) {
        notification.classList.remove('show');
        notification.classList.add('hide');
        
        // Remove from DOM after animation
        setTimeout(() => {
            notification.remove();
            
            // Remove container if no notifications left
            const container = document.getElementById('notification-container');
            if (container && container.children.length === 0) {
                container.remove();
            }
        }, 300);
    }
}

/**
 * Open event details modal
 * @param {Object} event - FullCalendar event object
 */
function openEventModal(event) {
    // In a real app, this would open a modal with event details
    console.log('Event clicked:', event);
    
    // Example: Show a notification with event details
    showNotification({
        title: event.title,
        message: `Event on ${event.start.toLocaleDateString()} at ${event.start.toLocaleTimeString()}`,
        type: 'info',
        duration: 5000
    });
}

// Export functions for use in other modules
window.EncompassDashboard = {
    showNotification: showNotification,
    openEventModal: openEventModal
};
