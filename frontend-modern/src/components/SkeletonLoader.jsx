import React from 'react';
import { Skeleton, Box, Grid, Paper } from '@mui/material';

export function DashboardSkeleton() {
  // Skeletons for stats, quick actions, activity, platform health, analytics chart
  return (
    <Box>
      <Grid container spacing={3}>
        {[...Array(4)].map((_, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Paper elevation={3} sx={{ p: 2 }}>
              <Skeleton variant="circular" width={40} height={40} sx={{ mb: 1 }} />
              <Skeleton width="60%" height={28} />
              <Skeleton width="40%" height={18} />
            </Paper>
          </Grid>
        ))}
      </Grid>
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {[...Array(3)].map((_, i) => (
          <Grid item xs={12} md={4} key={i}>
            <Paper elevation={3} sx={{ p: 2 }}>
              <Skeleton width="80%" height={28} sx={{ mb: 1 }} />
              <Skeleton width="100%" height={56} />
              <Skeleton width="60%" height={18} />
            </Paper>
          </Grid>
        ))}
      </Grid>
      <Paper elevation={3} sx={{ mt: 3, p: 3 }}>
        <Skeleton width="30%" height={32} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" width="100%" height={220} />
      </Paper>
    </Box>
  );
}
