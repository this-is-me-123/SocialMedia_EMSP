import axios from 'axios';

// Attach JWT to all requests
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

const API_BASE = '/api';

export const fetchStats = async () => {
  // Analytics summary: total posts, successes, failures, etc.
  const { data } = await axios.get(`${API_BASE}/analytics/summary`);
  return data;
};

export const fetchPosts = async () => {
  // All posts (for recent activity, etc.)
  const { data } = await axios.get(`${API_BASE}/posts`);
  return data;
};

export const fetchScheduledPosts = async () => {
  // Scheduled posts (for stats or future widgets)
  const { data } = await axios.get(`${API_BASE}/scheduled_posts`);
  return data;
};

export const fetchAnalytics = async () => {
  // Analytics view (for charts, etc.)
  const { data } = await axios.get(`${API_BASE}/analytics/view`);
  return data;
};

export const fetchPlatforms = async () => {
  // Platform health (mocked for now, can be updated if endpoint exists)
  // If you add a /platforms or /platform_health endpoint, update here.
  return [
    { name: 'Twitter', status: 'Online', color: 'success' },
    { name: 'Instagram', status: 'Online', color: 'success' },
    { name: 'Facebook', status: 'Issues', color: 'warning' },
    { name: 'TikTok', status: 'Offline', color: 'error' },
  ];
};

export const createPost = async (post) => {
  // Create a new post
  const { data } = await axios.post(`${API_BASE}/post`, post);
  return data;
};
