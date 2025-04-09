# Frontend Connection Testing Guide

After deploying the OneTask API, you'll need to ensure your frontend application can properly connect to it. This guide provides steps for testing the connection and troubleshooting common issues.

## Testing the Connection

### 1. CORS Configuration Check

The OneTask API includes CORS (Cross-Origin Resource Sharing) settings to allow connections from your frontend application. To verify the CORS settings:

1. Check the configuration in your deployed API:
   ```bash
   # Inspect the .env file
   cat .env
   ```

   Look for the `ALLOWED_ORIGINS` setting. It should include your frontend domain(s).

2. If you need to update the CORS settings, edit the `.env` file:
   ```bash
   nano .env
   ```

   Add your frontend domain to `ALLOWED_ORIGINS` (comma-separated list):
   ```
   ALLOWED_ORIGINS=https://your-frontend-domain.com,https://another-domain.com
   ```

3. Restart the API service after changing the settings:
   ```bash
   # If using systemd
   sudo systemctl restart onetask
   
   # If using Docker
   docker-compose restart
   ```

### 2. Basic API Connection Test

Create a simple HTML file to test the connection:

```html
<!DOCTYPE html>
<html>
<head>
    <title>OneTask API Connection Test</title>
</head>
<body>
    <h1>OneTask API Connection Test</h1>
    <button id="testButton">Test Connection</button>
    <div id="result"></div>

    <script>
        document.getElementById('testButton').addEventListener('click', async () => {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = 'Testing connection...';
            
            try {
                // Test the health endpoint
                const healthResponse = await fetch('https://your-api-domain.com/health', {
                    method: 'GET'
                });
                
                if (healthResponse.ok) {
                    const healthText = await healthResponse.text();
                    resultDiv.innerHTML = `Health check: ${healthText}<br>`;
                    
                    // Test the root endpoint
                    const rootResponse = await fetch('https://your-api-domain.com/', {
                        method: 'GET'
                    });
                    
                    if (rootResponse.ok) {
                        const rootData = await rootResponse.json();
                        resultDiv.innerHTML += `Root endpoint: ${JSON.stringify(rootData)}<br>`;
                        resultDiv.innerHTML += '<strong style="color:green">Connection successful!</strong>';
                    } else {
                        resultDiv.innerHTML += `Root endpoint error: ${rootResponse.status} ${rootResponse.statusText}`;
                    }
                } else {
                    resultDiv.innerHTML = `Health check failed: ${healthResponse.status} ${healthResponse.statusText}`;
                }
            } catch (error) {
                resultDiv.innerHTML = `Connection error: ${error.message}`;
            }
        });
    </script>
</body>
</html>
```

Replace `https://your-api-domain.com` with your actual API URL.

### 3. Authentication Test

Create another HTML file to test the authentication:

```html
<!DOCTYPE html>
<html>
<head>
    <title>OneTask API Authentication Test</title>
</head>
<body>
    <h1>OneTask API Authentication Test</h1>
    
    <div>
        <h2>Create Test User</h2>
        <button id="createUserButton">Create Test User</button>
        <div id="createUserResult"></div>
    </div>
    
    <div style="margin-top: 20px;">
        <h2>Get Token</h2>
        <button id="getTokenButton">Get Token</button>
        <div id="getTokenResult"></div>
    </div>
    
    <div style="margin-top: 20px;">
        <h2>Test Protected Endpoint</h2>
        <button id="testProtectedButton">Test Protected Endpoint</button>
        <div id="testProtectedResult"></div>
    </div>

    <script>
        // Configuration
        const API_URL = 'https://your-api-domain.com';
        const API_V1 = `${API_URL}/api/v1`;
        let accessToken = '';
        
        // Create a test user
        document.getElementById('createUserButton').addEventListener('click', async () => {
            const resultDiv = document.getElementById('createUserResult');
            resultDiv.innerHTML = 'Creating test user...';
            
            try {
                const response = await fetch(`${API_V1}/users/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email: 'test@example.com',
                        username: 'testuser',
                        password: 'Password123!',
                        full_name: 'Test User'
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    resultDiv.innerHTML = `User created successfully: ${JSON.stringify(data)}`;
                } else {
                    const error = await response.json();
                    resultDiv.innerHTML = `Error creating user: ${JSON.stringify(error)}`;
                }
            } catch (error) {
                resultDiv.innerHTML = `Connection error: ${error.message}`;
            }
        });
        
        // Get an access token
        document.getElementById('getTokenButton').addEventListener('click', async () => {
            const resultDiv = document.getElementById('getTokenResult');
            resultDiv.innerHTML = 'Getting token...';
            
            try {
                const response = await fetch(`${API_V1}/login/access-token`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({
                        'username': 'test@example.com',
                        'password': 'Password123!'
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    accessToken = data.access_token;
                    resultDiv.innerHTML = `Token received: ${accessToken.substring(0, 15)}...`;
                } else {
                    const error = await response.json();
                    resultDiv.innerHTML = `Error getting token: ${JSON.stringify(error)}`;
                }
            } catch (error) {
                resultDiv.innerHTML = `Connection error: ${error.message}`;
            }
        });
        
        // Test a protected endpoint
        document.getElementById('testProtectedButton').addEventListener('click', async () => {
            const resultDiv = document.getElementById('testProtectedResult');
            
            if (!accessToken) {
                resultDiv.innerHTML = 'Please get a token first';
                return;
            }
            
            resultDiv.innerHTML = 'Testing protected endpoint...';
            
            try {
                const response = await fetch(`${API_V1}/users/me`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    resultDiv.innerHTML = `Protected endpoint accessed successfully: ${JSON.stringify(data)}`;
                } else {
                    const error = await response.json();
                    resultDiv.innerHTML = `Error accessing protected endpoint: ${JSON.stringify(error)}`;
                }
            } catch (error) {
                resultDiv.innerHTML = `Connection error: ${error.message}`;
            }
        });
    </script>
</body>
</html>
```

Replace `https://your-api-domain.com` with your actual API URL.

### 4. WebSocket Connection Test

Create an HTML file to test WebSocket connections:

```html
<!DOCTYPE html>
<html>
<head>
    <title>OneTask API WebSocket Test</title>
</head>
<body>
    <h1>OneTask API WebSocket Test</h1>
    
    <div>
        <h2>1. Get Authentication Token</h2>
        <button id="getTokenButton">Get Token</button>
        <div id="getTokenResult"></div>
    </div>
    
    <div style="margin-top: 20px;">
        <h2>2. Connect to Notifications WebSocket</h2>
        <button id="connectNotificationsButton">Connect</button>
        <div id="notificationsStatus"></div>
    </div>
    
    <div style="margin-top: 20px;">
        <h2>3. Create Workspace for Task WebSocket Test</h2>
        <button id="createWorkspaceButton">Create Workspace</button>
        <div id="workspaceResult"></div>
    </div>
    
    <div style="margin-top: 20px;">
        <h2>4. Connect to Tasks WebSocket</h2>
        <button id="connectTasksButton">Connect</button>
        <div id="tasksStatus"></div>
    </div>

    <script>
        // Configuration
        const API_URL = 'https://your-api-domain.com';
        const WS_URL = 'wss://your-api-domain.com';
        const API_V1 = `${API_URL}/api/v1`;
        let accessToken = '';
        let workspaceId = '';
        let notificationsSocket = null;
        let tasksSocket = null;
        
        // Get an access token
        document.getElementById('getTokenButton').addEventListener('click', async () => {
            const resultDiv = document.getElementById('getTokenResult');
            resultDiv.innerHTML = 'Getting token...';
            
            try {
                const response = await fetch(`${API_V1}/login/access-token`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({
                        'username': 'test@example.com',
                        'password': 'Password123!'
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    accessToken = data.access_token;
                    resultDiv.innerHTML = `Token received: ${accessToken.substring(0, 15)}...`;
                } else {
                    const error = await response.json();
                    resultDiv.innerHTML = `Error getting token: ${JSON.stringify(error)}`;
                }
            } catch (error) {
                resultDiv.innerHTML = `Connection error: ${error.message}`;
            }
        });
        
        // Connect to notifications WebSocket
        document.getElementById('connectNotificationsButton').addEventListener('click', () => {
            const statusDiv = document.getElementById('notificationsStatus');
            
            if (!accessToken) {
                statusDiv.innerHTML = 'Please get a token first';
                return;
            }
            
            if (notificationsSocket) {
                notificationsSocket.close();
            }
            
            statusDiv.innerHTML = 'Connecting to notifications WebSocket...';
            
            notificationsSocket = new WebSocket(`${WS_URL}/ws/notifications?token=${accessToken}`);
            
            notificationsSocket.onopen = () => {
                statusDiv.innerHTML = 'Connected to notifications WebSocket<br>';
            };
            
            notificationsSocket.onmessage = (event) => {
                statusDiv.innerHTML += `Received message: ${event.data}<br>`;
            };
            
            notificationsSocket.onerror = (error) => {
                statusDiv.innerHTML += `Error: ${error}<br>`;
            };
            
            notificationsSocket.onclose = () => {
                statusDiv.innerHTML += 'Connection closed<br>';
            };
        });
        
        // Create a workspace for the tasks WebSocket test
        document.getElementById('createWorkspaceButton').addEventListener('click', async () => {
            const resultDiv = document.getElementById('workspaceResult');
            
            if (!accessToken) {
                resultDiv.innerHTML = 'Please get a token first';
                return;
            }
            
            resultDiv.innerHTML = 'Creating workspace...';
            
            try {
                const response = await fetch(`${API_V1}/workspaces/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: 'Test Workspace',
                        description: 'Test workspace for WebSocket testing'
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    workspaceId = data.id;
                    resultDiv.innerHTML = `Workspace created with ID: ${workspaceId}`;
                } else {
                    const error = await response.json();
                    resultDiv.innerHTML = `Error creating workspace: ${JSON.stringify(error)}`;
                }
            } catch (error) {
                resultDiv.innerHTML = `Connection error: ${error.message}`;
            }
        });
        
        // Connect to tasks WebSocket
        document.getElementById('connectTasksButton').addEventListener('click', () => {
            const statusDiv = document.getElementById('tasksStatus');
            
            if (!accessToken) {
                statusDiv.innerHTML = 'Please get a token first';
                return;
            }
            
            if (!workspaceId) {
                statusDiv.innerHTML = 'Please create a workspace first';
                return;
            }
            
            if (tasksSocket) {
                tasksSocket.close();
            }
            
            statusDiv.innerHTML = 'Connecting to tasks WebSocket...';
            
            tasksSocket = new WebSocket(`${WS_URL}/ws/tasks/${workspaceId}?token=${accessToken}`);
            
            tasksSocket.onopen = () => {
                statusDiv.innerHTML = 'Connected to tasks WebSocket<br>';
            };
            
            tasksSocket.onmessage = (event) => {
                statusDiv.innerHTML += `Received message: ${event.data}<br>`;
            };
            
            tasksSocket.onerror = (error) => {
                statusDiv.innerHTML += `Error: ${error}<br>`;
            };
            
            tasksSocket.onclose = () => {
                statusDiv.innerHTML += 'Connection closed<br>';
            };
        });
    </script>
</body>
</html>
```

Replace `https://your-api-domain.com` and `wss://your-api-domain.com` with your actual API URL (HTTPS and WSS respectively).

## Common Issues and Solutions

### 1. CORS Errors

**Issue**: Getting errors like "Access to fetch at '...' from origin '...' has been blocked by CORS policy"

**Solution**:
1. Check that your API's `ALLOWED_ORIGINS` setting includes your frontend domain
2. Make sure you're using the correct protocol (http/https)
3. Verify that your API server is correctly processing the CORS headers

### 2. WebSocket Connection Failures

**Issue**: WebSocket connections fail with errors like "WebSocket connection to 'wss://...' failed"

**Solution**:
1. Verify that your API server is properly configured for WebSockets
2. Check that your server's proxy (if any) is forwarding WebSocket connections
3. If using Nginx, ensure it has the proper WebSocket configuration:
   ```
   location /ws/ {
       proxy_pass http://localhost:5000;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_set_header Host $host;
   }
   ```

### 3. Authentication Issues

**Issue**: Unable to get an authentication token or access protected endpoints

**Solution**:
1. Verify you're using the correct credentials
2. Check that you're sending the token in the correct format (`Authorization: Bearer <token>`)
3. Ensure your token hasn't expired

## Integrating with Your Frontend Application

Once you've verified the API connection works, update your frontend application's configuration to point to your deployed API:

### React Example

```javascript
// src/config.js
const config = {
  apiUrl: process.env.REACT_APP_API_URL || 'https://your-api-domain.com',
  wsUrl: process.env.REACT_APP_WS_URL || 'wss://your-api-domain.com',
  apiPrefix: '/api/v1'
};

export default config;
```

### Vue Example

```javascript
// src/config.js
export default {
  apiUrl: process.env.VUE_APP_API_URL || 'https://your-api-domain.com',
  wsUrl: process.env.VUE_APP_WS_URL || 'wss://your-api-domain.com',
  apiPrefix: '/api/v1'
};
```

### Angular Example

```typescript
// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://your-api-domain.com',
  wsUrl: 'wss://your-api-domain.com',
  apiPrefix: '/api/v1'
};
```

## Additional Tips

1. **Use environment variables** to easily switch between development and production API endpoints
2. **Implement proper error handling** in your frontend to gracefully handle API connectivity issues
3. **Consider using a service worker** for offline functionality when the API is unavailable
4. **Monitor your API's performance** and implement retry logic for transient failures
5. **Test thoroughly in production environment** before going live with real users