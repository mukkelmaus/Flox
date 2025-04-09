# Simple Docker Deployment Guide for Floxari API

This guide will help you deploy Floxari API using Docker, which greatly simplifies the process and makes it accessible even if you have limited technical experience.

```
┌─────────────────────┐     ┌─────────────────────┐
│                     │     │                     │
│      Your Server    │     │   Floxari API       │
│                     │     │   Docker Container  │
│  ┌───────────────┐  │     │                     │
│  │ Docker        │  │     │  ┌───────────────┐  │
│  │               ├─────────▶│ FastAPI App    │  │
│  └───────────────┘  │     │  └───────────────┘  │
│                     │     │                     │
└─────────────────────┘     └─────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────────┐
                            │                     │
                            │   PostgreSQL        │
                            │   Database Container│
                            │                     │
                            └─────────────────────┘
```

Docker takes care of installing all the complex dependencies and setting up the environment, making deployment much easier for non-technical users.

## What You'll Need

- A server (VPS or your own computer)
- Docker and Docker Compose installed
- Basic familiarity with terminal commands

## Step 1: Install Docker and Docker Compose

### On Ubuntu/Debian:

```bash
# Install Docker
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add your user to the docker group so you don't have to use sudo
sudo usermod -aG docker $USER
```

Log out and log back in for the group change to take effect.

### On Windows:

1. Download and install Docker Desktop from [Docker's official website](https://www.docker.com/products/docker-desktop/).
2. Follow the installation instructions.
3. Start Docker Desktop after installation.

### On macOS:

1. Download and install Docker Desktop from [Docker's official website](https://www.docker.com/products/docker-desktop/).
2. Follow the installation instructions.
3. Start Docker Desktop after installation.

## Step 2: Download Floxari API

1. **Create a folder** for your project:
   ```bash
   mkdir floxari-api
   cd floxari-api
   ```

2. **Download the necessary files**:
   ```bash
   # Download docker-compose.yml and other files
   curl -O https://raw.githubusercontent.com/yourusername/floxari-api/main/docker-compose.yml
   curl -O https://raw.githubusercontent.com/yourusername/floxari-api/main/.env.production
   ```

## Step 3: Configure the Application

1. **Rename the environment file**:
   ```bash
   mv .env.production .env
   ```

2. **Edit the environment file**:
   ```bash
   nano .env
   ```

3. **Update these settings**:
   ```
   SECRET_KEY=generate_a_random_string_here
   SESSION_SECRET=generate_another_random_string_here
   ENVIRONMENT=production
   SERVER_HOST=http://your_server_ip_or_domain
   OPENAI_API_KEY=your_openai_key_if_using_ai_features
   ```

   To generate random strings, you can use this command:
   ```bash
   # On Linux/macOS
   openssl rand -base64 32
   
   # Or in Python
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Create a docker-compose.yml file** (if not already downloaded):
   ```bash
   nano docker-compose.yml
   ```

5. **Add the following content**:
   ```yaml
   version: '3'

   services:
     db:
       image: postgres:13
       volumes:
         - postgres_data:/var/lib/postgresql/data
       environment:
         - POSTGRES_PASSWORD=postgres
         - POSTGRES_USER=postgres
         - POSTGRES_DB=floxari
       restart: always
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U postgres"]
         interval: 5s
         timeout: 5s
         retries: 5
     
     api:
       image: ghcr.io/yourusername/floxari-api:latest
       # Or use build: . if deploying from source
       depends_on:
         db:
           condition: service_healthy
       ports:
         - "5000:5000"
       environment:
         - DATABASE_URL=postgresql://postgres:postgres@db/floxari
       env_file:
         - ./.env
       restart: always
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 20s

   volumes:
     postgres_data:
   ```

## Step 4: Start the Application

1. **Pull the images and start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Check if everything is running correctly**:
   ```bash
   docker-compose ps
   ```

   You should see both services (db and api) listed as "running".

3. **View the logs** to make sure everything started properly:
   ```bash
   docker-compose logs -f
   ```

   Press Ctrl+C to exit the logs view.

## Step 5: Test the Application

1. **Test the API**:
   ```bash
   curl http://localhost:5000/health
   ```

   You should see `OK` as the response.

2. Open a web browser and navigate to `http://localhost:5000/docs` to see the API documentation.

## Step 6: Set Up a Domain (Optional)

If you want to make your API accessible via a domain name:

1. **Point your domain to your server's IP** using your domain registrar.

2. **Install Nginx as a reverse proxy**:
   ```bash
   sudo apt install -y nginx
   ```

3. **Create an Nginx configuration**:
   ```bash
   sudo nano /etc/nginx/sites-available/floxari
   ```

4. **Add this content**:
   ```
   server {
       listen 80;
       server_name your_domain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

5. **Enable the site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/floxari /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **Set up HTTPS** (recommended):
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d your_domain.com
   ```

## Step 7: Managing Your Deployment

### To stop the application:
```bash
docker-compose down
```

### To restart the application:
```bash
docker-compose restart
```

### To update to a new version:
```bash
docker-compose pull
docker-compose down
docker-compose up -d
```

### To view logs:
```bash
docker-compose logs -f
```

### To backup your database:
```bash
docker-compose exec db pg_dump -U postgres floxari > backup.sql
```

## Testing Frontend Connectivity

After deploying the API with Docker, you'll want to verify frontend applications can connect properly:

1. **Access the Testing Tool**:
   ```bash
   # Copy the tester file to a convenient location
   docker cp floxari-api:/app/public/api_connection_test.html ./
   ```
   Then open `api_connection_test.html` in your browser and update the API URL to point to your deployed server.

2. **Run the Connection Tests**:
   - Test basic API connectivity
   - Create a test user
   - Test authentication
   - Verify protected endpoint access
   - Test WebSocket connectivity (if using real-time features)

3. **For Detailed Frontend Integration Instructions**:
   - See our [Frontend Connection Guide](./frontend-connection-guide.md)

## Common Issues and Solutions

### The Docker containers won't start

- Check logs with: `docker-compose logs`
- Make sure ports aren't already in use: `sudo lsof -i :5000`
- Verify Docker is running: `docker info`

### Can't connect to the application

- Check if the containers are running: `docker-compose ps`
- Check if a firewall is blocking access: `sudo ufw status`
- If using a firewall, allow the port: `sudo ufw allow 5000/tcp`

### Database connection issues

- Check logs for database errors: `docker-compose logs db`
- Make sure the DATABASE_URL in docker-compose.yml matches your configuration

### Frontend connection issues

- Check for CORS errors in your browser's developer console
- Make sure your API's `ALLOWED_ORIGINS` environment variable includes your frontend domain
- For WebSocket issues, ensure your proxy configuration supports WebSocket connections
- If using Nginx, verify it has WebSocket support configured correctly

## Data Persistence

Your database data is stored in a Docker volume called `postgres_data`. This ensures your data remains even if the containers are stopped or removed.

To see all volumes:
```bash
docker volume ls
```

## Getting Help

If you encounter issues that aren't covered here, please check:
- The project documentation in the `docs` folder
- Create an issue on our GitHub repository
- Join our community forum for additional support

Docker makes it much easier to deploy and manage your application, but it's still important to keep your system updated for security reasons.