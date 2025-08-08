import { useState, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import companyLogo from './assets/fulllogo.jpg';
import './App.css';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Drawer from '@mui/material/Drawer';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Dashboard from './pages/Dashboard';
import Accounts from './pages/Accounts';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';
import { ErrorBoundary } from './components/ErrorBoundary';
import Tooltip from '@mui/material/Tooltip';
import Avatar from '@mui/material/Avatar';

const drawerWidth = 240;
const navItems = [
  { text: 'Dashboard', path: '/' },
  { text: 'Accounts', path: '/accounts' },
  { text: 'Analytics', path: '/analytics' },
  { text: 'Settings', path: '/settings' },
];

const AuthContext = createContext();
function useAuth() {
  return useContext(AuthContext);
}

function ProtectedRoute({ children }) {
  const { token } = useAuth();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AuthUserMenu() {
  const { token, handleLogout } = useAuth();
  let username = '';
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
      username = payload.sub || payload.username || '';
    } catch (e) {}
  }
  if (!token) return null;
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
      <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.dark', mr: 1 }}>{username ? username[0].toUpperCase() : '?'}</Avatar>
      <Typography variant="body1" sx={{ mr: 2 }}>{username}</Typography>
      <Tooltip title="Logout" arrow>
        <button color="inherit" style={{ border: 'none', background: 'none', cursor: 'pointer' }} onClick={handleLogout}>Logout</button>
      </Tooltip>
    </Box>
  );
}

function AppContent() {
  const location = useLocation();
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: 'primary.main' }}
      >
        <Toolbar>
          <img src={companyLogo} alt="Encompass MSP Logo" style={{ height: 60, marginRight: 24 }} />
          <Typography variant="h5" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
            Encompass MSP Dashboard
          </Typography>
          <AuthUserMenu />
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box', backgroundColor: 'white' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {navItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  component={Link}
                  to={item.path}
                  selected={location.pathname === item.path || (item.path === '/' && location.pathname === '')}
                >
                  <ListItemIcon>
                    <InboxIcon />
                  </ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}>
        <Toolbar />
        <ErrorBoundary>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/accounts" element={<ProtectedRoute><Accounts /></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          </Routes>
        </ErrorBoundary>
      </Box>
    </Box>
  );
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));

  const handleLogin = (tok) => {
    setToken(tok);
    localStorage.setItem('access_token', tok);
  };
  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('access_token');
  };

  const authContextValue = { token, handleLogin, handleLogout };

  return (
    <AuthContext.Provider value={authContextValue}>
      <Router>
        <AppContent />
      </Router>
    </AuthContext.Provider>
  );
}

export default App
