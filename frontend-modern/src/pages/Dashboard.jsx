import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import Avatar from '@mui/material/Avatar';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import SendIcon from '@mui/icons-material/Send';
import { useQuery } from '@tanstack/react-query';
import * as api from '../api';
import AnalyticsChart from '../components/AnalyticsChart';
import { DashboardSkeleton } from '../components/SkeletonLoader';
import Alert from '@mui/material/Alert';

const statIcons = [
  <TrendingUpIcon color="primary" />, // total posts
  <AccessTimeIcon color="secondary" />, // scheduled
  <ErrorIcon color="error" />, // failed
  <CheckCircleIcon color="success" /> // active accounts
];

export default function Dashboard() {
  // Stats summary
  const { data: stats, isLoading: statsLoading, isError: statsError } = useQuery(['stats'], api.fetchStats);
  // Recent activity (posts)
  const { data: posts, isLoading: postsLoading, isError: postsError } = useQuery(['posts'], api.fetchPosts);
  // Platform health (mocked for now)
  const { data: platforms } = useQuery(['platforms'], api.fetchPlatforms);
  // Analytics (for chart placeholder)
  const { data: analytics, isLoading: analyticsLoading, isError: analyticsError } = useQuery(['analytics'], api.fetchAnalytics);

  // Map stats to widget cards (fallback to 0 if missing)
  const statCards = [
    {
      label: 'Total Posts',
      value: stats?.total_posts ?? 0,
      icon: statIcons[0],
    },
    {
      label: 'Scheduled Posts',
      value: stats?.scheduled_posts ?? 0,
      icon: statIcons[1],
    },
    {
      label: 'Failed Posts',
      value: stats?.failures ?? 0,
      icon: statIcons[2],
    },
    {
      label: 'Active Accounts',
      value: stats?.active_accounts ?? 0,
      icon: statIcons[3],
    },
  ];

  // Map posts to activity feed (show last 5)
  const activity = Array.isArray(posts)
    ? posts.slice(-5).reverse().map((p) => ({
        user: p.user_id ?? 'User',
        action: `Posted to ${p.platform || 'Platform'}`,
        time: p.created_at ? new Date(p.created_at).toLocaleString() : '',
      }))
    : [];

  if (statsLoading || postsLoading || analyticsLoading) {
    return <DashboardSkeleton />;
  }

  if (statsError || postsError || analyticsError) {
    return (
      <Box p={4}>
        <Alert severity="error">Failed to load dashboard data. Please check your connection or try again later.</Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        {/* Stats Summary */}
        {statCards.map((stat) => (
          <Grid item xs={12} sm={6} md={3} key={stat.label}>
            <Paper elevation={3} sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
              <Avatar sx={{ bgcolor: 'primary.light', mr: 2 }}>{stat.icon}</Avatar>
              <Box>
                <Typography variant="h6">{stat.value}</Typography>
                <Typography variant="body2" color="text.secondary">{stat.label}</Typography>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Quick Actions</Typography>
            <Button variant="contained" color="primary" startIcon={<SendIcon />} sx={{ mr: 1, mb: 1 }}>Post Now</Button>
            <Button variant="outlined" color="secondary" sx={{ mr: 1, mb: 1 }}>Sync Accounts</Button>
            <Button variant="outlined" color="success" sx={{ mb: 1 }}>Refresh Analytics</Button>
          </Paper>
        </Grid>
        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Recent Activity</Typography>
            <List dense>
              {activity && activity.length > 0 ? activity.map((item, idx) => (
                <ListItem key={idx}>
                  <ListItemAvatar>
                    <Avatar>{typeof item.user === 'string' ? item.user[0] : 'U'}</Avatar>
                  </ListItemAvatar>
                  <ListItemText primary={item.action} secondary={item.time} />
                </ListItem>
              )) : (
                <ListItem><ListItemText primary="No recent activity" /></ListItem>
              )}
            </List>
          </Paper>
        </Grid>
        {/* Platform Health */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Platform Health</Typography>
            <List dense>
              {platforms && platforms.length > 0 ? platforms.map((plat, idx) => (
                <ListItem key={plat.name}>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: `${plat.color}.main` }}>
                      <CheckCircleIcon color={plat.color === 'success' ? 'success' : plat.color === 'warning' ? 'warning' : 'error'} />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText primary={plat.name} secondary={plat.status} />
                </ListItem>
              )) : (
                <ListItem><ListItemText primary="No platform data" /></ListItem>
              )}
            </List>
          </Paper>
        </Grid>
      </Grid>
      {/* Analytics Chart */}
      <Box sx={{ mt: 3 }}>
        <AnalyticsChart />
      </Box>
    </Box>
  );
}
