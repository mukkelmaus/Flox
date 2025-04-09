# Floxari API Integration Guide

This guide provides detailed information about integrating the Floxari API with frontend applications, particularly React/TypeScript frontends. It covers authentication flows, state management suggestions, endpoint usage patterns, and real-time features.

## Authentication Flow

Floxari uses JWT (JSON Web Tokens) for authentication. Here's how to implement the authentication flow in your frontend:

### 1. User Registration

```typescript
// Example using axios and React hooks
import axios from 'axios';
import { useState } from 'react';

const RegisterForm = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/v1/users/', {
        email,
        username,
        password,
      });
      // Handle successful registration
      console.log('User registered:', response.data);
      // Redirect to login
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };
  
  return (
    <form onSubmit={handleRegister}>
      {/* Form fields */}
    </form>
  );
};
```

### 2. User Login

```typescript
import axios from 'axios';
import { useState } from 'react';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // Note: The login endpoint expects form data, not JSON
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await axios.post('/api/v1/login/access-token', formData);
      
      // Store the token
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('token_type', response.data.token_type);
      
      // Set default Authorization header for all requests
      axios.defaults.headers.common['Authorization'] = 
        `${response.data.token_type} ${response.data.access_token}`;
      
      // Redirect to dashboard
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };
  
  return (
    <form onSubmit={handleLogin}>
      {/* Form fields */}
    </form>
  );
};
```

### 3. Token Management

Create a utility for managing tokens:

```typescript
// src/utils/auth.ts
import axios from 'axios';

export const setAuthToken = (token: string, tokenType = 'Bearer') => {
  if (token) {
    localStorage.setItem('token', token);
    localStorage.setItem('token_type', tokenType);
    axios.defaults.headers.common['Authorization'] = `${tokenType} ${token}`;
  } else {
    localStorage.removeItem('token');
    localStorage.removeItem('token_type');
    delete axios.defaults.headers.common['Authorization'];
  }
};

export const getAuthToken = () => {
  return localStorage.getItem('token');
};

export const getTokenType = () => {
  return localStorage.getItem('token_type') || 'Bearer';
};

export const isAuthenticated = () => {
  return !!getAuthToken();
};

export const logout = () => {
  setAuthToken('');
  // Additional cleanup as needed
};
```

### 4. Protected Routes

Use a HOC (Higher Order Component) or custom hook to protect routes:

```typescript
// src/components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';

const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Usage in route config
<Route
  path="/dashboard"
  element={<ProtectedRoute><Dashboard /></ProtectedRoute>}
/>
```

## State Management

For optimal state management with the Floxari API, we recommend using a combination of React Context API for global state and React Query for data fetching and caching.

### 1. Authentication State

```typescript
// src/contexts/AuthContext.tsx
import { createContext, useContext, useEffect, useState } from 'react';
import { getAuthToken, isAuthenticated, logout, setAuthToken } from '../utils/auth';
import axios from 'axios';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  loading: boolean;
  login: (token: string, tokenType?: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  loading: true,
  login: () => {},
  logout: () => {},
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (isAuthenticated()) {
        try {
          const response = await axios.get('/api/v1/users/me');
          setUser(response.data);
        } catch (err) {
          // Token might be invalid or expired
          console.error('Auth error:', err);
          logout();
        }
      }
      setLoading(false);
    };
    
    checkAuth();
  }, []);
  
  const login = (token: string, tokenType = 'Bearer') => {
    setAuthToken(token, tokenType);
    // Fetch user data
    axios.get('/api/v1/users/me')
      .then(response => {
        setUser(response.data);
      })
      .catch(err => {
        console.error('Error fetching user data:', err);
      });
  };
  
  const handleLogout = () => {
    logout();
    setUser(null);
  };
  
  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!user,
        user,
        loading,
        login,
        logout: handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

### 2. Data Fetching with React Query

```typescript
// src/hooks/useTasks.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';

// Fetch all tasks
export const useTasks = ({ workspace_id, status, priority }) => {
  return useQuery(
    ['tasks', { workspace_id, status, priority }],
    async () => {
      const params = { workspace_id, status, priority };
      const response = await axios.get('/api/v1/tasks/', { params });
      return response.data;
    }
  );
};

// Fetch a single task
export const useTask = (taskId) => {
  return useQuery(
    ['task', taskId],
    async () => {
      const response = await axios.get(`/api/v1/tasks/${taskId}`);
      return response.data;
    },
    {
      // Don't fetch if no taskId is provided
      enabled: !!taskId,
    }
  );
};

// Create a new task
export const useCreateTask = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    async (taskData) => {
      const response = await axios.post('/api/v1/tasks/', taskData);
      return response.data;
    },
    {
      // Invalidate and refetch tasks after a new task is created
      onSuccess: () => {
        queryClient.invalidateQueries('tasks');
      },
    }
  );
};

// Update a task
export const useUpdateTask = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    async ({ taskId, data }) => {
      const response = await axios.put(`/api/v1/tasks/${taskId}`, data);
      return response.data;
    },
    {
      // Update the cache with the new data
      onSuccess: (data) => {
        queryClient.invalidateQueries('tasks');
        queryClient.invalidateQueries(['task', data.id]);
      },
    }
  );
};

// Delete a task
export const useDeleteTask = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    async (taskId) => {
      await axios.delete(`/api/v1/tasks/${taskId}`);
      return taskId;
    },
    {
      // Remove the task from the cache
      onSuccess: (taskId) => {
        queryClient.invalidateQueries('tasks');
        queryClient.removeQueries(['task', taskId]);
      },
    }
  );
};
```

## Endpoint Usage Patterns

Here are common usage patterns for key API endpoints:

### 1. Task Management

```typescript
// Creating a task
const createTask = async (taskData) => {
  try {
    const response = await axios.post('/api/v1/tasks/', {
      title: 'Complete project proposal',
      description: 'Write a proposal for the new client project',
      status: 'todo',
      priority: 'high',
      due_date: '2025-04-01T12:00:00Z',
      tags: ['work', 'proposal'],
      subtasks: [
        { title: 'Research client background', is_completed: false },
        { title: 'Draft outline', is_completed: false },
      ]
    });
    return response.data;
  } catch (error) {
    console.error('Error creating task:', error);
    throw error;
  }
};

// Updating a task status
const updateTaskStatus = async (taskId, newStatus) => {
  try {
    const response = await axios.patch(`/api/v1/tasks/${taskId}`, {
      status: newStatus
    });
    return response.data;
  } catch (error) {
    console.error('Error updating task status:', error);
    throw error;
  }
};

// Breaking down a task with AI
const breakDownTask = async (taskId) => {
  try {
    const response = await axios.post(`/api/v1/ai/tasks/${taskId}/breakdown`);
    return response.data;
  } catch (error) {
    console.error('Error breaking down task:', error);
    throw error;
  }
};
```

### 2. Focus Mode

```typescript
// Getting focus mode tasks
const getFocusTasks = async (context, timeAvailable, energyLevel) => {
  try {
    const response = await axios.get('/api/v1/tasks/focus-mode', {
      params: {
        context,
        time_available: timeAvailable,
        energy_level: energyLevel
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error getting focus tasks:', error);
    throw error;
  }
};
```

### 3. Workspace Management

```typescript
// Creating a workspace
const createWorkspace = async (name, description, isPrivate) => {
  try {
    const response = await axios.post('/api/v1/workspaces/', {
      name,
      description,
      is_private: isPrivate
    });
    return response.data;
  } catch (error) {
    console.error('Error creating workspace:', error);
    throw error;
  }
};

// Adding a member to a workspace
const addWorkspaceMember = async (workspaceId, userId, role) => {
  try {
    const response = await axios.post(`/api/v1/workspaces/${workspaceId}/members`, {
      user_id: userId,
      role: role
    });
    return response.data;
  } catch (error) {
    console.error('Error adding workspace member:', error);
    throw error;
  }
};
```

### 4. Third-Party Integrations

```typescript
// Connecting to Google Calendar
const connectGoogleCalendar = async () => {
  try {
    // Step 1: Get the authorization URL
    const authResponse = await axios.get('/api/v1/integrations/google_calendar/auth');
    const authUrl = authResponse.data.auth_url;
    
    // Step 2: Redirect user to the authorization URL
    // (This would typically be handled through a window.location or a popup)
    window.location.href = authUrl;
    
    // Step 3: The API will handle the callback and token exchange
    // Your frontend needs to handle the redirect back from Google
    
    return authResponse.data;
  } catch (error) {
    console.error('Error connecting to Google Calendar:', error);
    throw error;
  }
};

// Syncing with a connected integration
const syncCalendar = async (integrationId) => {
  try {
    const response = await axios.post(`/api/v1/integrations/${integrationId}/sync`);
    return response.data;
  } catch (error) {
    console.error('Error syncing calendar:', error);
    throw error;
  }
};
```

## Real-Time Features

For real-time features like notifications, consider using a WebSocket connection:

```typescript
// src/hooks/useNotifications.ts
import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';

export const useNotifications = () => {
  const { isAuthenticated, user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);
  
  useEffect(() => {
    if (isAuthenticated && user) {
      // Create WebSocket connection
      const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsUrl = `${wsProtocol}://${window.location.host}/api/v1/ws/notifications`;
      
      socketRef.current = new WebSocket(wsUrl);
      
      socketRef.current.onopen = () => {
        console.log('WebSocket connection established');
        setConnected(true);
        
        // Send authentication message
        socketRef.current.send(JSON.stringify({
          type: 'authenticate',
          token: localStorage.getItem('token')
        }));
      };
      
      socketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'notification') {
          setNotifications(prev => [data.notification, ...prev]);
        }
      };
      
      socketRef.current.onclose = () => {
        console.log('WebSocket connection closed');
        setConnected(false);
      };
      
      socketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      // Clean up on unmount
      return () => {
        if (socketRef.current) {
          socketRef.current.close();
        }
      };
    }
  }, [isAuthenticated, user]);
  
  // Fetch initial notifications
  useEffect(() => {
    if (isAuthenticated) {
      axios.get('/api/v1/notifications/')
        .then(response => {
          setNotifications(response.data);
        })
        .catch(error => {
          console.error('Error fetching notifications:', error);
        });
    }
  }, [isAuthenticated]);
  
  const markAsRead = async (notificationId) => {
    try {
      await axios.patch(`/api/v1/notifications/${notificationId}`, {
        read: true
      });
      
      // Update local state
      setNotifications(prev => 
        prev.map(notification => 
          notification.id === notificationId 
            ? { ...notification, read: true }
            : notification
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };
  
  const markAllAsRead = async () => {
    try {
      await axios.post('/api/v1/notifications/mark-all-read');
      
      // Update local state
      setNotifications(prev => 
        prev.map(notification => ({ ...notification, read: true }))
      );
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };
  
  return {
    notifications,
    connected,
    markAsRead,
    markAllAsRead
  };
};
```

## View Modes

The API provides data structures that support multiple view modes in the frontend:

### 1. List View

Simply display tasks in a list format, sorted by priority or due date.

```typescript
// src/components/TaskList.tsx
import { useTasks } from '../hooks/useTasks';

const TaskList = ({ workspaceId }) => {
  const { data: tasks, isLoading, error } = useTasks({ workspace_id: workspaceId });
  
  if (isLoading) return <div>Loading tasks...</div>;
  if (error) return <div>Error loading tasks</div>;
  
  return (
    <div className="task-list">
      {tasks.map(task => (
        <div key={task.id} className="task-item">
          <h3>{task.title}</h3>
          <div>Status: {task.status}</div>
          <div>Priority: {task.priority}</div>
          {task.due_date && <div>Due: {new Date(task.due_date).toLocaleDateString()}</div>}
        </div>
      ))}
    </div>
  );
};
```

### 2. Card View (Kanban)

Group tasks by status and display them in columns.

```typescript
// src/components/KanbanBoard.tsx
import { useTasks } from '../hooks/useTasks';

const KanbanBoard = ({ workspaceId }) => {
  const { data: tasks, isLoading, error } = useTasks({ workspace_id: workspaceId });
  
  if (isLoading) return <div>Loading tasks...</div>;
  if (error) return <div>Error loading tasks</div>;
  
  // Group tasks by status
  const todoTasks = tasks.filter(task => task.status === 'todo');
  const inProgressTasks = tasks.filter(task => task.status === 'in_progress');
  const doneTasks = tasks.filter(task => task.status === 'done');
  
  return (
    <div className="kanban-board">
      <div className="kanban-column">
        <h2>To Do</h2>
        {todoTasks.map(task => (
          <div key={task.id} className="kanban-card">
            {task.title}
          </div>
        ))}
      </div>
      
      <div className="kanban-column">
        <h2>In Progress</h2>
        {inProgressTasks.map(task => (
          <div key={task.id} className="kanban-card">
            {task.title}
          </div>
        ))}
      </div>
      
      <div className="kanban-column">
        <h2>Done</h2>
        {doneTasks.map(task => (
          <div key={task.id} className="kanban-card">
            {task.title}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 3. Calendar View

Display tasks on a calendar based on their due dates.

```typescript
// src/components/CalendarView.tsx
import { useState } from 'react';
import { useTasks } from '../hooks/useTasks';
import Calendar from 'react-calendar'; // Example calendar library

const CalendarView = ({ workspaceId }) => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const { data: tasks, isLoading, error } = useTasks({ workspace_id: workspaceId });
  
  if (isLoading) return <div>Loading tasks...</div>;
  if (error) return <div>Error loading tasks</div>;
  
  // Get tasks for the selected date
  const selectedDateStr = selectedDate.toISOString().split('T')[0];
  const tasksForSelectedDate = tasks.filter(task => {
    if (!task.due_date) return false;
    return task.due_date.startsWith(selectedDateStr);
  });
  
  // Generate task markers for the calendar
  const getTileContent = ({ date }) => {
    const dateStr = date.toISOString().split('T')[0];
    const tasksForDate = tasks.filter(task => {
      if (!task.due_date) return false;
      return task.due_date.startsWith(dateStr);
    });
    
    if (tasksForDate.length > 0) {
      return <div className="task-marker">{tasksForDate.length}</div>;
    }
    
    return null;
  };
  
  return (
    <div className="calendar-view">
      <Calendar
        onChange={setSelectedDate}
        value={selectedDate}
        tileContent={getTileContent}
      />
      
      <div className="tasks-for-date">
        <h3>Tasks for {selectedDate.toLocaleDateString()}</h3>
        {tasksForSelectedDate.length === 0 ? (
          <p>No tasks for this date</p>
        ) : (
          <ul>
            {tasksForSelectedDate.map(task => (
              <li key={task.id}>{task.title}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};
```

## Error Handling

Implement consistent error handling:

```typescript
// src/utils/errorHandler.ts
import axios, { AxiosError } from 'axios';
import { logout } from './auth';

// Set up global error handling for Axios
export const setupAxiosInterceptors = () => {
  axios.interceptors.response.use(
    response => response,
    (error: AxiosError) => {
      // Handle specific error codes
      if (error.response) {
        const { status } = error.response;
        
        // Handle authentication errors
        if (status === 401) {
          logout();
          window.location.href = '/login?session_expired=true';
          return Promise.reject(error);
        }
        
        // Handle forbidden errors
        if (status === 403) {
          console.error('Permission denied');
          // Redirect to appropriate page or show notification
        }
        
        // Handle not found errors
        if (status === 404) {
          console.error('Resource not found');
          // Redirect to appropriate page or show notification
        }
        
        // Handle validation errors
        if (status === 422) {
          console.error('Validation error:', error.response.data);
          // Format and display validation errors
        }
        
        // Handle server errors
        if (status >= 500) {
          console.error('Server error:', error.response.data);
          // Show server error notification
        }
      } else if (error.request) {
        // The request was made but no response was received
        console.error('Network error - no response received');
        // Show network error notification
      } else {
        // Something happened in setting up the request
        console.error('Error setting up request:', error.message);
      }
      
      return Promise.reject(error);
    }
  );
};
```

## Data Visualization

For analytics features:

```typescript
// src/components/TaskAnalytics.tsx
import { useQuery } from 'react-query';
import axios from 'axios';
import { Chart } from 'react-chartjs-2'; // Example chart library

const TaskAnalytics = ({ userId }) => {
  const { data, isLoading, error } = useQuery(['task-analytics', userId], async () => {
    const response = await axios.get(`/api/v1/ai/productivity-insights`);
    return response.data;
  });
  
  if (isLoading) return <div>Loading analytics...</div>;
  if (error) return <div>Error loading analytics</div>;
  
  // Example: Chart of optimal productive hours
  const optimalHoursData = {
    labels: data.optimal_hours.map(h => `${h.start_hour}-${h.end_hour}`),
    datasets: [
      {
        label: 'Productivity Level',
        data: data.optimal_hours.map(h => {
          // Convert productivity_level to numeric value
          switch (h.productivity_level) {
            case 'high': return 100;
            case 'medium': return 60;
            case 'low': return 30;
            default: return 0;
          }
        }),
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };
  
  return (
    <div className="task-analytics">
      <h2>Productivity Insights</h2>
      
      <div className="optimal-hours">
        <h3>Your Most Productive Hours</h3>
        <Chart type="bar" data={optimalHoursData} />
      </div>
      
      <div className="productivity-pattern">
        <h3>Your Productivity Pattern</h3>
        <p>{data.productivity_pattern}</p>
      </div>
      
      <div className="focus-tips">
        <h3>Focus Tips</h3>
        <ul>
          {data.focus_tips.map((tip, index) => (
            <li key={index}>{tip}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};
```

## Conclusion

This integration guide covers the main patterns and approaches for working with the Floxari API. By following these patterns, you can create a robust, maintainable frontend application that takes full advantage of the API's capabilities.

For detailed information about specific endpoints, refer to the OpenAPI documentation available at `/docs` when the API is running.