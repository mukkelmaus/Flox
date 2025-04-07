
const API_CONFIG = {
  BASE_URL: process.env.API_BASE_URL || 'http://0.0.0.0:5000/api/v1',
  WS_BASE: process.env.WS_BASE_URL || 'ws://0.0.0.0:5000/ws',

  endpoints: {
    login: '/login/access-token',
    refresh: '/login/refresh-token',
    users: '/users',
    tasks: '/tasks',
    workspaces: '/workspaces',
    notifications: '/notifications',
    ai: '/ai',
    integrations: '/integrations',
    gamification: '/gamification'
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
