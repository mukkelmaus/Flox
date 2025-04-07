
const API_CONFIG = {
  BASE_URL: window.location.hostname.includes('replit.app') 
    ? `https://${window.location.host}/api/v1`
    : 'http://0.0.0.0:5000/api/v1',
    
  WS_BASE: window.location.hostname.includes('replit.app')
    ? `wss://${window.location.host}/ws`
    : `ws://${window.location.host}/ws`,

  endpoints: {
    login: '/login/access-token',
    refresh: '/login/refresh-token',
    users: '/users',
    tasks: '/tasks',
    workspaces: '/workspaces',
    notifications: '/notifications'
  },

  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

export const createAuthHeader = (token) => ({
  'Authorization': `Bearer ${token}`
});

export default API_CONFIG;
