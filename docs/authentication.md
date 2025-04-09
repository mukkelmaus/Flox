# Floxari API Authentication

This document explains the authentication process for the Floxari API.

## Overview

Floxari uses JWT (JSON Web Tokens) for authentication. The authentication flow is as follows:

1. The client sends user credentials to the `/login/access-token` endpoint.
2. The server validates the credentials and returns an access token.
3. The client includes this token in the `Authorization` header for subsequent requests.

## Endpoints

### Login

**Endpoint:** `POST /api/v1/login/access-token`

**Request Body:**
```
{
  "username": "user@example.com",  // Can be email or username
  "password": "user_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Test Token

**Endpoint:** `POST /api/v1/login/test-token`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00",
  ...
}
```

## Using the Token

For all protected endpoints, include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Token Expiration

Tokens are valid for a limited time (default: 8 days). When a token expires, the client must obtain a new token by authenticating again.

## Frontend Integration

Here's how to integrate with a React/TypeScript frontend:

1. Store the token securely (e.g., in an HTTP-only cookie or localStorage).
2. Create an auth context/provider that:
   - Manages the authentication state
   - Provides login/logout functions
   - Automatically includes the token in API requests
   - Handles token expiration/refresh

### Example React Auth Hook

```typescript
import { useState, useEffect, useContext, createContext } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api/v1';

interface AuthContextType {
  user: any | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
      axios.post(`${API_URL}/login/test-token`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => {
          setUser(res.data);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await axios.post(`${API_URL}/login/access-token`, {
      username: email,
      password
    });
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    
    // Get user data
    const userResponse = await axios.post(`${API_URL}/login/test-token`, {}, {
      headers: { Authorization: `Bearer ${access_token}` }
    });
    setUser(userResponse.data);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### API Client Configuration

```typescript
import axios from 'axios';

const API_URL = 'http://localhost:5000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL
});

// Add a request interceptor to add the auth token to every request
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add a response interceptor to handle authentication errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Redirect to login page or show authentication error
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## Security Considerations

1. Always use HTTPS in production to protect token transmission.
2. Set appropriate token expiration times.
3. Consider implementing token refresh mechanisms for long-lived sessions.
4. Implement proper CORS configuration in production.