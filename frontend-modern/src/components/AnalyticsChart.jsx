import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAnalytics } from '../api';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar } from 'recharts';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

export default function AnalyticsChart() {
  const { data, isLoading, isError } = useQuery(['analytics'], fetchAnalytics);

  // Example: posts per day by platform (adapt to your analytics data shape)
  let chartData = [];
  if (Array.isArray(data)) {
    chartData = data;
  } else if (data && data.posts_per_day) {
    // If backend returns { posts_per_day: [{ date, twitter, facebook, ... }] }
    chartData = data.posts_per_day;
  }

  return (
    <Paper elevation={3} sx={{ p: 2, height: 320 }}>
      <Typography variant="h6" gutterBottom>Posts Over Time</Typography>
      {isLoading ? (
        <Box sx={{ textAlign: 'center', pt: 8 }}>
          <Typography>Loading chart...</Typography>
        </Box>
      ) : isError ? (
        <Box sx={{ textAlign: 'center', pt: 8 }}>
          <Typography color="error">Failed to load analytics data.</Typography>
        </Box>
      ) : chartData && chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            {/* Dynamically render a line for each platform if present */}
            {chartData[0] && Object.keys(chartData[0]).filter(k => k !== 'date').map((platform) => (
              <Line key={platform} type="monotone" dataKey={platform} stroke={platform === 'twitter' ? '#1da1f2' : platform === 'facebook' ? '#1877f3' : '#8884d8'} dot={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <Box sx={{ textAlign: 'center', pt: 8 }}>
          <Typography>No analytics data available.</Typography>
        </Box>
      )}
    </Paper>
  );
}
