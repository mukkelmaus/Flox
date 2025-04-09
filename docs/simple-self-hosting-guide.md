# Simple Self-Hosting Guide for OneTask API

This guide will help you host the OneTask API on your own server, even if you don't have much technical experience. We'll go through the process step-by-step with clear explanations.

```
┌─────────────────────────────────────────────────┐
│                                                 │
│                  Your Server                    │
│                                                 │
│  ┌─────────────┐     ┌─────────────────────┐   │
│  │ PostgreSQL  │     │  OneTask API        │   │
│  │ Database    │◄────┤  (Python FastAPI)   │   │
│  └─────────────┘     └─────────────────────┘   │
│                             ▲                   │
│                             │                   │
└─────────────────────────────┼───────────────────┘
                              │
                   ┌──────────┴──────────┐
                   │     Internet        │
                   └─────────┬───────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │                 │
                    │  Your Browser   │
                    │                 │
                    └─────────────────┘
```

This guide will walk you through setting up both the OneTask API application and its PostgreSQL database on your server.

## What You'll Need

- A Linux server (like Ubuntu, Debian, or similar)
- Basic understanding of terminal commands
- A domain name (optional, but recommended)

## Step 1: Set Up Your Server

### Option A: Using a VPS Provider (Recommended)

1. **Sign up for a VPS service** like DigitalOcean, Linode, or AWS Lightsail.
2. **Create a new server** (often called a "Droplet," "Instance," or "VPS")
   - Choose Ubuntu 20.04 or newer
   - Select a plan with at least 1GB RAM
   - Follow their setup guide to access your server

### Option B: Using Your Own Computer

1. Make sure you have a stable internet connection and your computer can stay on
2. Consider the security implications of hosting from your home network

## Step 2: Connect to Your Server

1. **Access your server** using SSH:
   ```
   ssh username@your_server_ip
   ```
   (Your VPS provider will give you these details)

2. **Update your system**:
   ```
   sudo apt update
   sudo apt upgrade -y
   ```

## Step 3: Install Required Software

Run these commands to install everything you need:

```bash
# Install Python and required tools
sudo apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Step 4: Set Up the Database

1. **Switch to the PostgreSQL user**:
   ```
   sudo -i -u postgres
   ```

2. **Create a database and user**:
   ```
   createuser onetask_user
   createdb onetask_db
   psql -c "ALTER USER onetask_user WITH ENCRYPTED PASSWORD 'choose_a_secure_password';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE onetask_db TO onetask_user;"
   exit
   ```

## Step 5: Install the OneTask API

1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/onetask-api.git
   cd onetask-api
   ```

2. **Create a virtual environment**:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the application**:
   ```
   pip install .
   ```

## Step 6: Configure the Application

1. **Create environment file**:
   ```
   cp .env.example .env
   ```

2. **Edit the file** with a text editor:
   ```
   nano .env
   ```

3. **Update these important settings**:
   ```
   DATABASE_URL=postgresql://onetask_user:choose_a_secure_password@localhost/onetask_db
   SECRET_KEY=generate_a_random_string_here
   SESSION_SECRET=generate_another_random_string_here
   ENVIRONMENT=production
   SERVER_HOST=http://your_server_ip_or_domain
   ```

   To generate random strings, you can use:
   ```
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. Save and exit (Ctrl+X, then Y, then Enter in nano)

## Step 7: Run Initial Setup

1. **Run the setup script**:
   ```
   chmod +x ./prestart.sh
   ./prestart.sh
   ```

## Step 8: Test the Application

1. **Start the server manually** to test it:
   ```
   ./production_server.sh
   ```

2. **Check if it's working** by opening a new terminal and running:
   ```
   curl http://localhost:5000/health
   ```
   
   You should see `OK` as the response.

3. Press Ctrl+C to stop the server when finished testing

## Step 9: Set Up the Service to Run Automatically

1. **Create a service file**:
   ```
   sudo nano /etc/systemd/system/onetask.service
   ```

2. **Add this content** to the file:
   ```
   [Unit]
   Description=OneTask API
   After=network.target postgresql.service

   [Service]
   User=your_username
   Group=your_username
   WorkingDirectory=/path/to/onetask-api
   ExecStart=/path/to/onetask-api/production_server.sh
   Restart=always
   RestartSec=5
   Environment=PATH=/path/to/onetask-api/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

   [Install]
   WantedBy=multi-user.target
   ```

   Replace `your_username` with your actual username and `/path/to/onetask-api` with the actual path.

3. **Enable and start the service**:
   ```
   sudo systemctl daemon-reload
   sudo systemctl enable onetask
   sudo systemctl start onetask
   ```

4. **Check if it's running**:
   ```
   sudo systemctl status onetask
   ```

## Step 10: Set Up a Domain Name (Optional but Recommended)

1. **Get a domain name** if you don't have one (from Namecheap, GoDaddy, etc.)

2. **Point your domain to your server's IP address** using an A record (follow your domain provider's instructions)

3. **Install Nginx** as a reverse proxy:
   ```
   sudo apt install -y nginx
   ```

4. **Create an Nginx configuration**:
   ```
   sudo nano /etc/nginx/sites-available/onetask
   ```

5. **Add this content**:
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

   Replace `your_domain.com` with your actual domain.

6. **Enable the site**:
   ```
   sudo ln -s /etc/nginx/sites-available/onetask /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Set up HTTPS** (highly recommended):
   ```
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d your_domain.com
   ```

   Follow the prompts to complete the setup.

## Step 11: Keeping Your Server Updated

1. **To update the application** when changes are available:
   ```
   cd /path/to/onetask-api
   git pull
   source venv/bin/activate
   pip install .
   sudo systemctl restart onetask
   ```

2. **To update your server** regularly:
   ```
   sudo apt update
   sudo apt upgrade -y
   ```

## Common Issues and Solutions

### The application won't start

- Check logs with: `sudo journalctl -u onetask.service -n 50`
- Make sure the database is running: `sudo systemctl status postgresql`
- Verify your .env file has the correct settings

### Can't connect to the application

- Check if the service is running: `sudo systemctl status onetask`
- Check if port 5000 is blocked by a firewall: `sudo ufw status`
- If using a firewall, allow the port: `sudo ufw allow 80/tcp`

### Database connection issues

- Check your DATABASE_URL in the .env file
- Make sure the password and database name match what you created

## Getting Help

If you encounter issues that aren't covered here, please check:
- The project documentation in the `docs` folder
- Create an issue on our GitHub repository
- Join our community forum for additional support

Remember that self-hosting requires some maintenance. Set up regular backups of your database and keep your server updated to ensure security and stability.