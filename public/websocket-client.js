
class WebSocketClient {
  constructor(config) {
    this.config = config;
    this.token = null;
    this.connections = new Map();
    this.handlers = new Map();
  }

  setToken(token) {
    this.token = token;
  }

  connect(type, params = {}) {
    if (!this.token) throw new Error('No authentication token');
    
    let url;
    switch(type) {
      case 'notifications':
        url = `${this.config.WS_BASE}/notifications?token=${this.token}`;
        break;
      case 'tasks':
        if (!params.workspaceId) throw new Error('Workspace ID required');
        url = `${this.config.WS_BASE}/tasks/${params.workspaceId}?token=${this.token}`;
        break;
      case 'focus':
        if (!params.sessionId) throw new Error('Session ID required');
        url = `${this.config.WS_BASE}/focus-session/${params.sessionId}?token=${this.token}`;
        break;
    }

    const ws = new WebSocket(url);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const handlers = this.handlers.get(type) || [];
      handlers.forEach(handler => handler(data));
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error:`, error);
    };

    ws.onclose = () => {
      setTimeout(() => this.connect(type, params), 5000);
    };

    this.connections.set(type, ws);
  }

  on(type, handler) {
    const handlers = this.handlers.get(type) || [];
    handlers.push(handler);
    this.handlers.set(type, handlers);
  }

  disconnect(type) {
    const ws = this.connections.get(type);
    if (ws) {
      ws.close();
      this.connections.delete(type);
    }
  }

  disconnectAll() {
    for (const type of this.connections.keys()) {
      this.disconnect(type);
    }
  }
}

export default WebSocketClient;
