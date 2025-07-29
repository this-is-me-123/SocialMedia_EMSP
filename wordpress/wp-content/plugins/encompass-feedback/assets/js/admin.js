/**
 * Encompass Feedback Admin JavaScript
 * 
 * This file contains all the interactive functionality for the admin interface
 * of the Encompass Feedback plugin.
 */

(function($) {
    'use strict';

    // Document ready
    $(document).ready(function() {
        // Initialize components
        initModals();
        initAjaxActions();
        initFeedbackFilters();
        initBulkActions();
        initStatusUpdates();
        initFeedbackSearch();
        initTabs();
        initDatePickers();
        initTooltips();
    });

    /**
     * Initialize modal dialogs
     */
    function initModals() {
        // Open modal
        $('.encompass-feedback-open-modal').on('click', function(e) {
            e.preventDefault();
            const modalId = $(this).data('modal');
            const $modal = $('#' + modalId);
            
            if ($modal.length) {
                $modal.fadeIn(200);
                $('body').addClass('encompass-feedback-modal-open');
                
                // Load content via AJAX if needed
                if ($modal.find('.modal-content').data('ajax-url')) {
                    loadModalContent($modal);
                }
            }
        });
        
        // Close modal
        $('.encompass-feedback-modal-close, .encompass-feedback-modal-cancel').on('click', function() {
            closeModal($(this).closest('.encompass-feedback-modal'));
        });
        
        // Close when clicking outside modal content
        $('.encompass-feedback-modal').on('click', function(e) {
            if ($(e.target).hasClass('encompass-feedback-modal')) {
                closeModal($(this));
            }
        });
        
        // Close with ESC key
        $(document).on('keyup', function(e) {
            if (e.key === 'Escape') {
                closeModal($('.encompass-feedback-modal:visible'));
            }
        });
    }
    
    /**
     * Close modal dialog
     */
    function closeModal($modal) {
        $modal.fadeOut(200, function() {
            $('body').removeClass('encompass-feedback-modal-open');
            // Reset form if exists
            const $form = $modal.find('form');
            if ($form.length) {
                $form[0].reset();
            }
        });
    }
    
    /**
     * Load modal content via AJAX
     */
    function loadModalContent($modal) {
        const $content = $modal.find('.modal-content');
        const url = $content.data('ajax-url');
        const data = $content.data('ajax-data') || {};
        
        // Show loading state
        $content.html('<div class="encompass-feedback-loading"><span class="spinner is-active"></span> ' + encompassFeedbackVars.loadingText + '</div>');
        
        // Make AJAX request
        $.post(
            encompassFeedbackVars.ajaxUrl,
            {
                action: 'encompass_feedback_get_modal_content',
                nonce: encompassFeedbackVars.nonce,
                ...data
            },
            function(response) {
                if (response.success) {
                    $content.html(response.data.content);
                } else {
                    $content.html('<div class="error">' + (response.data.message || encompassFeedbackVars.errorText) + '</div>');
                }
            },
            'json'
        ).fail(function() {
            $content.html('<div class="error">' + encompassFeedbackVars.errorText + '</div>');
        });
    }
    
    /**
     * Initialize AJAX actions
     */
    function initAjaxActions() {
        // Update feedback status
        $('.encompass-feedback-status-update').on('change', function() {
            const $select = $(this);
            const feedbackId = $select.data('feedback-id');
            const status = $select.val();
            
            // Show loading state
            const $spinner = $('<span class="spinner is-active" style="float: none;"></span>');
            $select.after($spinner);
            
            // Make AJAX request
            $.post(
                encompassFeedbackVars.ajaxUrl,
                {
                    action: 'encompass_feedback_update_status',
                    nonce: encompassFeedbackVars.nonce,
                    feedback_id: feedbackId,
                    status: status
                },
                function(response) {
                    $spinner.remove();
                    
                    if (response.success) {
                        // Update UI
                        const $statusBadge = $select.closest('.feedback-actions').find('.status-badge');
                        $statusBadge
                            .removeClass('status-new status-in_progress status-resolved')
                            .addClass('status-' + status)
                            .text(response.data.status_label);
                        
                        // Show success message
                        showNotice('success', response.data.message);
                    } else {
                        // Revert select value
                        $select.val($select.data('current-status'));
                        
                        // Show error message
                        showNotice('error', response.data.message || encompassFeedbackVars.errorText);
                    }
                },
                'json'
            ).fail(function() {
                $spinner.remove();
                $select.val($select.data('current-status'));
                showNotice('error', encompassFeedbackVars.errorText);
            });
        });
        
        // Delete feedback
        $('.encompass-feedback-delete').on('click', function(e) {
            e.preventDefault();
            
            if (!confirm(encompassFeedbackVars.confirmDelete)) {
                return false;
            }
            
            const $button = $(this);
            const feedbackId = $button.data('feedback-id');
            
            // Show loading state
            $button.prop('disabled', true).text(encompassFeedbackVars.deletingText);
            
            // Make AJAX request
            $.post(
                encompassFeedbackVars.ajaxUrl,
                {
                    action: 'encompass_feedback_delete',
                    nonce: encompassFeedbackVars.nonce,
                    feedback_id: feedbackId
                },
                function(response) {
                    if (response.success) {
                        // Remove row from table
                        $button.closest('tr').fadeOut(300, function() {
                            $(this).remove();
                            
                            // Show success message
                            showNotice('success', response.data.message);
                            
                            // Update counters if they exist
                            updateFeedbackCounters(-1, response.data.status);
                        });
                    } else {
                        // Reset button
                        $button.prop('disabled', false).text(encompassFeedbackVars.deleteText);
                        
                        // Show error message
                        showNotice('error', response.data.message || encompassFeedbackVars.errorText);
                    }
                },
                'json'
            ).fail(function() {
                $button.prop('disabled', false).text(encompassFeedbackVars.deleteText);
                showNotice('error', encompassFeedbackVars.errorText);
            });
            
            return false;
        });
    }
    
    /**
     * Initialize feedback filters
     */
    function initFeedbackFilters() {
        const $filterForm = $('.encompass-feedback-filters form');
        
        if ($filterForm.length) {
            // Auto-submit on filter change
            $filterForm.on('change', 'select, input[type="checkbox"]', function() {
                // For select elements, check if value has changed
                if ($(this).is('select')) {
                    if ($(this).data('prev-value') !== $(this).val()) {
                        $filterForm.submit();
                    }
                } else {
                    $filterForm.submit();
                }
            });
            
            // Store initial values for comparison
            $filterForm.find('select').each(function() {
                $(this).data('prev-value', $(this).val());
            });
            
            // Reset filters
            $('.encompass-feedback-reset-filters').on('click', function(e) {
                e.preventDefault();
                
                // Reset form
                $filterForm[0].reset();
                
                // Submit form
                $filterForm.submit();
            });
        }
    }
    
    /**
     * Initialize bulk actions
     */
    function initBulkActions() {
        const $bulkActions = $('.tablenav .bulkactions');
        
        if ($bulkActions.length) {
            const $bulkAction = $bulkActions.find('select[name="action"]');
            const $bulkAction2 = $bulkActions.find('select[name="action2"]');
            const $applyButton = $bulkActions.find('.action');
            
            // Toggle bulk action buttons based on selection
            function toggleBulkActionButtons() {
                const hasSelected = $('.encompass-feedback-table input[type="checkbox"]:checked').length > 0;
                $applyButton.prop('disabled', !hasSelected);
            }
            
            // Check all checkboxes
            $('.encompass-feedback-table thead .check-column input[type="checkbox"]').on('change', function() {
                const isChecked = $(this).prop('checked');
                $('.encompass-feedback-table tbody .check-column input[type="checkbox"]').prop('checked', isChecked);
                toggleBulkActionButtons();
            });
            
            // Handle individual checkbox changes
            $('.encompass-feedback-table tbody .check-column input[type="checkbox"]').on('change', function() {
                toggleBulkActionButtons();
                
                // Update "check all" checkbox
                const allChecked = $('.encompass-feedback-table tbody .check-column input[type="checkbox"]:checked').length === 
                                 $('.encompass-feedback-table tbody .check-column input[type="checkbox"]').length;
                $('.encompass-feedback-table thead .check-column input[type="checkbox"]').prop('checked', allChecked);
            });
            
            // Apply bulk action
            $applyButton.on('click', function(e) {
                e.preventDefault();
                
                const action = $bulkAction.val() !== '-1' ? $bulkAction.val() : $bulkAction2.val();
                
                if (action === '-1') {
                    return false;
                }
                
                const $checked = $('.encompass-feedback-table tbody .check-column input[type="checkbox"]:checked');
                const feedbackIds = [];
                
                if ($checked.length === 0) {
                    showNotice('warning', encompassFeedbackVars.selectItemsText);
                    return false;
                }
                
                // Get selected feedback IDs
                $checked.each(function() {
                    feedbackIds.push($(this).val());
                });
                
                // Show confirmation for destructive actions
                if (['delete'].includes(action) && !confirm(encompassFeedbackVars.confirmBulkAction)) {
                    return false;
                }
                
                // Show loading state
                const $spinner = $('<span class="spinner is-active" style="float: none; margin-top: 0;"></span>');
                $applyButton.after($spinner);
                $applyButton.prop('disabled', true);
                
                // Make AJAX request
                $.post(
                    encompassFeedbackVars.ajaxUrl,
                    {
                        action: 'encompass_feedback_bulk_action',
                        nonce: encompassFeedbackVars.nonce,
                        bulk_action: action,
                        feedback_ids: feedbackIds
                    },
                    function(response) {
                        $spinner.remove();
                        $applyButton.prop('disabled', false);
                        
                        if (response.success) {
                            // Reload the page to reflect changes
                            window.location.reload();
                        } else {
                            showNotice('error', response.data.message || encompassFeedbackVars.errorText);
                        }
                    },
                    'json'
                ).fail(function() {
                    $spinner.remove();
                    $applyButton.prop('disabled', false);
                    showNotice('error', encompassFeedbackVars.errorText);
                });
            });
        }
    }
    
    /**
     * Initialize status updates
     */
    function initStatusUpdates() {
        $('.encompass-feedback-status-selector select').on('change', function() {
            const $form = $(this).closest('form');
            const $submitButton = $form.find('button[type="submit"]');
            const originalText = $submitButton.text();
            
            // Show loading state
            $submitButton.prop('disabled', true).text(encompassFeedbackVars.updatingText);
            
            // Submit form via AJAX
            $.post(
                $form.attr('action'),
                $form.serialize(),
                function(response) {
                    if (response.success) {
                        // Update status badge
                        const $statusBadge = $('.encompass-feedback-status');
                        $statusBadge
                            .removeClass('status-new status-in_progress status-resolved')
                            .addClass('status-' + response.data.status)
                            .text(response.data.status_label);
                        
                        // Show success message
                        showNotice('success', response.data.message);
                        
                        // Update history if it exists
                        if (response.data.history_item) {
                            const $historyList = $('.activity-log');
                            if ($historyList.length) {
                                $historyList.prepend(response.data.history_item);
                            }
                        }
                    } else {
                        // Show error message
                        showNotice('error', response.data.message || encompassFeedbackVars.errorText);
                    }
                    
                    // Reset button
                    $submitButton.prop('disabled', false).text(originalText);
                },
                'json'
            ).fail(function() {
                $submitButton.prop('disabled', false).text(originalText);
                showNotice('error', encompassFeedbackVars.errorText);
            });
            
            return false;
        });
    }
    
    /**
     * Initialize feedback search
     */
    function initFeedbackSearch() {
        const $searchInput = $('.encompass-feedback-search input[type="search"]');
        
        if ($searchInput.length) {
            // Debounce search
            let searchTimeout;
            
            $searchInput.on('keyup', function() {
                clearTimeout(searchTimeout);
                const searchTerm = $(this).val().trim();
                
                if (searchTerm.length >= 2 || searchTerm.length === 0) {
                    searchTimeout = setTimeout(function() {
                        performSearch(searchTerm);
                    }, 500);
                }
            });
            
            // Clear search
            $('.encompass-feedback-search-clear').on('click', function(e) {
                e.preventDefault();
                $searchInput.val('');
                performSearch('');
            });
        }
        
        function performSearch(term) {
            const $searchContainer = $('.encompass-feedback-search');
            const $resultsContainer = $('.encompass-feedback-search-results');
            const $spinner = $searchContainer.find('.spinner');
            
            // Show loading state
            $spinner.addClass('is-active');
            
            // Make AJAX request
            $.post(
                encompassFeedbackVars.ajaxUrl,
                {
                    action: 'encompass_feedback_search',
                    nonce: encompassFeedbackVars.nonce,
                    search: term
                },
                function(response) {
                    $spinner.removeClass('is-active');
                    
                    if (response.success) {
                        $resultsContainer.html(response.data.html);
                        
                        // Show/hide clear button
                        if (term.length > 0) {
                            $('.encompass-feedback-search-clear').show();
                        } else {
                            $('.encompass-feedback-search-clear').hide();
                        }
                    } else {
                        showNotice('error', response.data.message || encompassFeedbackVars.errorText);
                    }
                },
                'json'
            ).fail(function() {
                $spinner.removeClass('is-active');
                showNotice('error', encompassFeedbackVars.errorText);
            });
        }
    }
    
    /**
     * Initialize tabs
     */
    function initTabs() {
        $('.encompass-feedback-tabs').on('click', '.encompass-feedback-tab:not(.active)', function(e) {
            e.preventDefault();
            
            const $tab = $(this);
            const tabId = $tab.data('tab');
            
            if (!tabId) return;
            
            // Update active tab
            $tab.addClass('active').siblings().removeClass('active');
            
            // Show corresponding tab content
            $('#' + tabId).addClass('active').siblings('.encompass-feedback-tab-content').removeClass('active');
            
            // Update URL hash
            if (history.pushState) {
                history.pushState(null, null, '#' + tabId);
            } else {
                window.location.hash = '#' + tabId;
            }
        });
        
        // Check for hash on page load
        if (window.location.hash) {
            const $tab = $('.encompass-feedback-tab[data-tab="' + window.location.hash.substring(1) + '"]');
            if ($tab.length) {
                $tab.trigger('click');
            }
        }
    }
    
    /**
     * Initialize date pickers
     */
    function initDatePickers() {
        if (typeof $.fn.datepicker !== 'undefined') {
            $('.encompass-feedback-datepicker').datepicker({
                dateFormat: 'yy-mm-dd',
                changeMonth: true,
                changeYear: true,
                yearRange: '-10:+5',
                showButtonPanel: true
            });
        }
    }
    
    /**
     * Initialize tooltips
     */
    function initTooltips() {
        $('.encompass-feedback-tooltip').on('mouseenter', function() {
            const $tooltip = $(this).find('.tooltip-text');
            const tooltipWidth = $tooltip.outerWidth();
            const tooltipHeight = $tooltip.outerHeight();
            const windowWidth = $(window).width();
            const windowHeight = $(window).height();
            const offset = 10;
            
            // Position tooltip
            const pos = $(this).offset();
            const tooltipTop = pos.top - tooltipHeight - offset;
            const tooltipLeft = Math.max(offset, Math.min(pos.left - (tooltipWidth / 2) + ($(this).outerWidth() / 2), windowWidth - tooltipWidth - offset));
            
            $tooltip.css({
                top: tooltipTop,
                left: tooltipLeft
            });
        });
    }
    
    /**
     * Show notice message
     */
    function showNotice(type, message) {
        // Remove existing notices
        $('.encompass-feedback-notice').remove();
        
        // Create notice
        const $notice = $('<div class="notice notice-' + type + ' is-dismissible encompass-feedback-notice"><p>' + message + '</p></div>');
        
        // Add dismiss button
        $notice.append('<button type="button" class="notice-dismiss"><span class="screen-reader-text">' + encompassFeedbackVars.dismissText + '</span></button>');
        
        // Add to page
        $('.wrap h1').after($notice);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            $notice.fadeOut(300, function() {
                $(this).remove();
            });
        }, 5000);
        
        // Handle dismiss
        $notice.on('click', '.notice-dismiss', function() {
            $notice.fadeOut(300, function() {
                $(this).remove();
            });
        });
    }
    
    /**
     * Update feedback counters
     */
    function updateFeedbackCounters(change, status) {
        // Update total counter
        const $totalCounter = $('.encompass-feedback-total-count');
        if ($totalCounter.length) {
            const currentTotal = parseInt($totalCounter.text()) || 0;
            $totalCounter.text(currentTotal + change);
        }
        
        // Update status counter if provided
        if (status) {
            const $statusCounter = $('.encompass-feedback-status-count[data-status="' + status + '"]');
            if ($statusCounter.length) {
                const currentStatusCount = parseInt($statusCounter.text()) || 0;
                const newStatusCount = Math.max(0, currentStatusCount + change);
                $statusCounter.text(newStatusCount);
                
                // Update parent row visibility if count reaches zero
                if (newStatusCount === 0) {
                    $statusCounter.closest('tr').fadeOut(300);
                } else if (currentStatusCount === 0 && newStatusCount > 0) {
                    $statusCounter.closest('tr').fadeIn(300);
                }
            }
        }
    }
    
    // Make functions available globally
    window.encompassFeedbackAdmin = {
        showNotice: showNotice,
        updateFeedbackCounters: updateFeedbackCounters,
        closeModal: closeModal
    };
    
})(jQuery);
