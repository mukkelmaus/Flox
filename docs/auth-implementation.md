# Authentication System Implementation

This document provides details on the authentication system implementation for the OneTask API.

## Overview

The OneTask API uses JWT (JSON Web Tokens) for stateless authentication. This provides several benefits:

- Tokens can be verified without database access
- Reduced server load compared to session-based auth
- Well-suited for API authentication
- Compatible with microservices architecture

## Backend Implementation

### Core Components

The authentication system is implemented with these key components:

1. **Security Module** (`app/core/security.py`):
   - Password hashing with bcrypt
   - JWT token creation and validation
   - User extraction from token

2. **Login Endpoints** (`app/api/api_v1/endpoints/login.py`):
   - Token generation endpoint
   - Token verification endpoint

3. **User Model** (`app/models/user.py`):
   - User database schema
   - Fields for authentication (username, email, password_hash)

4. **User Schemas** (`app/schemas/user.py`):
   - Data validation for user operations
   - Control over which fields are exposed

5. **User Endpoints** (`app/api/api_v1/endpoints/users.py`):
   - User registration
   - User profile management
   - Password change

### Authentication Flow

1. **Registration**: 
   - Client sends user data (email, username, password) to `/api/v1/users/`
   - Server validates data, hashes password, and stores user
   - Returns user data (without password)

2. **Login**:
   - Client sends credentials to `/api/v1/login/access-token`
   - Server verifies credentials
   - If valid, server generates JWT token and returns it
   - If invalid, server returns 401 Unauthorized

3. **Authenticated Requests**:
   - Client includes token in Authorization header: `Bearer <token>`
   - Server validates token and extracts user ID
   - Server retrieves user from database
   - If token is valid and user is active, request proceeds
   - If token is invalid or user is inactive, server returns 401 Unauthorized

4. **Token Verification**:
   - Client can verify token validity with `/api/v1/login/test-token`
   - Returns user data if token is valid

## Integration with Frontend

### Storing Tokens

The frontend should store the token securely:

1. **HTTP-only Cookies** (recommended for web apps):
   - More secure against XSS attacks
   - Requires CSRF protection
   - Server must set cookie with correct attributes

2. **localStorage**:
   - Simple to implement
   - Works well with SPAs
   - Vulnerable to XSS attacks

### Authentication Helpers

Implement these helpers in the frontend:

1. **Auth Provider/Context**:
   - Manages authentication state
   - Provides login/logout methods
   - Handles token storage and retrieval

2. **API Client**:
   - Automatically includes token in requests
   - Handles 401 responses (token expiration)
   - Redirects to login when needed

3. **Protected Routes**:
   - Prevent access to protected pages for unauthenticated users
   - Redirect to login page

### Example Integration Code

#### React/TypeScript Authentication Context

```typescript
// auth-context.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api/v1';

interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  [key: string]: any;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  // Check token validity on mount
  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await axios.post(
          `${API_URL}/login/test-token`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setUser(response.data);
      } catch (error) {
        console.error('Token validation failed', error);
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    validateToken();
  }, [token]);

  const login = async (email: string, password: string): Promise<void> => {
    try {
      const response = await axios.post(`${API_URL}/login/access-token`, {
        username: email, // API accepts email as username
        password,
      });

      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);

      // Get user data
      const userResponse = await axios.post(
        `${API_URL}/login/test-token`,
        {},
        { headers: { Authorization: `Bearer ${access_token}` } }
      );
      setUser(userResponse.data);
    } catch (error) {
      console.error('Login failed', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const isAuthenticated = () => !!user;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        logout,
        isAuthenticated,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

#### API Client Configuration

```typescript
// api-client.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_URL = 'http://localhost:5000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          // Handle unauthorized errors
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic request method
  public async request<T>(config: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.request(config);
    return response.data;
  }

  // Convenience methods
  public async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'get', url });
  }

  public async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'post', url, data });
  }

  public async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'put', url, data });
  }

  public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'delete', url });
  }
}

export default new ApiClient();
```

#### Protected Route Component

```typescript
// ProtectedRoute.tsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './auth-context';

const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated() ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;
```

## Security Considerations

### Token Security

1. **Token Expiration**: Set an appropriate expiration time (current default: 8 days)
2. **Secret Key**: Use a strong secret key stored in environment variables
3. **HTTPS**: Always use HTTPS in production to protect token transmission

### Password Security

1. **Hashing**: Passwords are hashed with bcrypt before storage
2. **Validation**: Password requirements enforced with Pydantic validators
3. **Rate Limiting**: Implement rate limiting for login attempts (to be added)

### Additional Protections

1. **CORS**: Configure proper CORS settings in production
2. **CSRF Protection**: Add CSRF protection if using cookie-based auth
3. **Security Headers**: Implement security headers in production

## Future Enhancements

- Add refresh token functionality
- Implement email verification
- Add Two-Factor Authentication (2FA)
- Add OAuth integration (Google, GitHub, etc.)
- Implement stricter rate limiting