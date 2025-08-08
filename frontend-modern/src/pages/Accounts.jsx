import Typography from '@mui/material/Typography';

import { DashboardSkeleton } from '../components/SkeletonLoader';
import Alert from '@mui/material/Alert';

export default function Accounts() {
  // Placeholder for async loading/error state
  const isLoading = false;
  const isError = false;

  if (isLoading) {
    return <DashboardSkeleton />;
  }
  if (isError) {
    return <Alert severity="error">Failed to load accounts data.</Alert>;
  }
  return (
    <>
      <Typography variant="h4" gutterBottom>
        Accounts
      </Typography>
      <Typography variant="body1">
        Manage social accounts and integrations here.
      </Typography>
    </>
  );
}
