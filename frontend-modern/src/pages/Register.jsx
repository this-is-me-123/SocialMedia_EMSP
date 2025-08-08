import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { TextField, Button, Paper, Typography, Box, Alert } from '@mui/material';
import axios from 'axios';

export default function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const registerMutation = useMutation({
    mutationFn: async ({ username, password }) => {
      const form = new URLSearchParams();
      form.append('username', username);
      form.append('password', password);
      const { data } = await axios.post('/api/auth/register', form);
      return data;
    },
    onSuccess: () => {
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    },
    onError: (err) => {
      setError('Registration failed (username may be taken)');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);
    registerMutation.mutate({ username, password });
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', bgcolor: '#f7f7fa' }}>
      <Paper elevation={3} sx={{ p: 4, width: 340 }}>
        <Typography variant="h5" gutterBottom>Register</Typography>
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
          {success && <Alert severity="success" sx={{ mt: 2 }}>Registration successful! Redirecting to login...</Alert>}
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 2 }}
            disabled={registerMutation.isLoading}
          >
            {registerMutation.isLoading ? 'Registering...' : 'Register'}
          </Button>
        </form>
      </Paper>
    </Box>
  );
}
