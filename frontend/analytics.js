// Analytics event tracking utility
function trackEvent(event, data = {}) {
  fetch('/api/analytics/event', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({event, ...data, timestamp: new Date().toISOString()})
  });
}

// Example usage for post creation
function trackPostCreated(platform, postId) {
  trackEvent('post_created', {platform, postId});
}

// Example usage for scheduling
function trackPostScheduled(platform, scheduledTime, postId) {
  trackEvent('post_scheduled', {platform, scheduledTime, postId});
}

// Example usage for errors
function trackError(context, message, extra = {}) {
  trackEvent('error', {context, message, ...extra});
}
