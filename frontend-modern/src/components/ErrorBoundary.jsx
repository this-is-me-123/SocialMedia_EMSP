import React from 'react';
import { Box, Typography, Button } from '@mui/material';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to an error reporting service if needed
    // console.error(error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 6, textAlign: 'center' }}>
          <Typography variant="h4" color="error" gutterBottom>
            Oops! Something went wrong.
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            An unexpected error occurred. Please try refreshing the page.
          </Typography>
          <Button variant="contained" color="primary" onClick={this.handleReload}>Reload</Button>
        </Box>
      );
    }
    return this.props.children;
  }
}
