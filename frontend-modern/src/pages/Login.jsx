import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { TextField, Button, Paper, Typography, Box, Alert } from '@mui/material';
import axios from 'axios';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const loginMutation = useMutation({
    mutationFn: async ({ username, password }) => {
      const form = new URLSearchParams();
      form.append('username', username);
      form.append('password', password);
      const { data } = await axios.post('/api/auth/login', form);
      return data;
    },
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      navigate('/');
    },
    onError: (err) => {
      setError('Invalid username or password');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);
    loginMutation.mutate({ username, password });
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', bgcolor: '#f7f7fa' }}>
      <Paper elevation={3} sx={{ p: 4, width: 340 }}>
        <Typography variant="h5" gutterBottom>Login</Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            fullWidth
            margin="normal"
            autoFocus
            required
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            fullWidth
            margin="normal"
            required
          />
          {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 2 }}
            disabled={loginMutation.isLoading}
          >
            {loginMutation.isLoading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2">
            Don't have an account? <a href="/register" style={{ color: '#1976d2', textDecoration: 'underline' }}>Register</a>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}
