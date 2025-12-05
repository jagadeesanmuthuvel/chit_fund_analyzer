#!/bin/bash
# Production deployment script for Chit Fund Analyzer

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="chit-fund-analyzer"
APP_DIR="/opt/$APP_NAME"
USER="chit-fund"
SERVICE_NAME="$APP_NAME"

echo -e "${GREEN}🚀 Starting production deployment of Chit Fund Analyzer${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required system packages
print_status "Installing system dependencies..."
apt install -y python3.13 python3.13-venv python3-pip nginx git curl supervisor

# Create application user
print_status "Creating application user..."
if ! id "$USER" &>/dev/null; then
    useradd -r -s /bin/false -d "$APP_DIR" "$USER"
fi

# Create application directory
print_status "Setting up application directory..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Clone or update repository
if [ ! -d ".git" ]; then
    print_status "Cloning repository..."
    git clone https://github.com/jagadeesanmuthuvel/chit_fund_analyzer.git .
else
    print_status "Updating repository..."
    git pull origin main
fi

# Set up Python virtual environment
print_status "Creating Python virtual environment..."
python3.13 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set proper permissions
print_status "Setting file permissions..."
chown -R "$USER:$USER" "$APP_DIR"
chmod +x "$APP_DIR/run_app.py"

# Create systemd service file
print_status "Creating systemd service..."
cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=Chit Fund Analyzer Streamlit Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=STREAMLIT_SERVER_HEADLESS=true
Environment=STREAMLIT_SERVER_PORT=8501
Environment=STREAMLIT_SERVER_ADDRESS=0.0.0.0
Environment=STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ExecStart=$APP_DIR/venv/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
print_status "Configuring Nginx..."
cat > "/etc/nginx/sites-available/$APP_NAME" << EOF
server {
    listen 80;
    server_name _;  # Replace with your domain
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
        
        # Security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
    }
    
    # Health check endpoint
    location /_health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable Nginx site
ln -sf "/etc/nginx/sites-available/$APP_NAME" "/etc/nginx/sites-enabled/"
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Create log directory
mkdir -p /var/log/$APP_NAME
chown "$USER:$USER" /var/log/$APP_NAME

# Create supervisor configuration for monitoring
print_status "Setting up process monitoring..."
cat > "/etc/supervisor/conf.d/$APP_NAME.conf" << EOF
[program:$APP_NAME]
command=$APP_DIR/venv/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
directory=$APP_DIR
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/log/$APP_NAME/error.log
stdout_logfile=/var/log/$APP_NAME/output.log
environment=STREAMLIT_SERVER_HEADLESS=true,STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EOF

# Enable and start services
print_status "Starting services..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# Restart Nginx
systemctl enable nginx
systemctl restart nginx

# Start supervisor
systemctl enable supervisor
systemctl restart supervisor
supervisorctl reread
supervisorctl update

# Wait for service to start
sleep 5

# Check service status
print_status "Checking service status..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_status "✅ $SERVICE_NAME service is running"
else
    print_error "❌ $SERVICE_NAME service failed to start"
    systemctl status "$SERVICE_NAME"
    exit 1
fi

if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running"
else
    print_error "❌ Nginx failed to start"
    systemctl status nginx
    exit 1
fi

# Test application
print_status "Testing application..."
sleep 10
if curl -f -s http://localhost:8501/_stcore/health > /dev/null; then
    print_status "✅ Application health check passed"
else
    print_warning "⚠️ Application health check failed, but service may still be starting"
fi

# Create backup script
print_status "Creating backup script..."
cat > "/usr/local/bin/backup-$APP_NAME" << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/chit-fund-analyzer"
APP_DIR="/opt/chit-fund-analyzer"

mkdir -p "$BACKUP_DIR"

# Backup application
tar -czf "$BACKUP_DIR/app-backup-$DATE.tar.gz" \
    --exclude="venv" \
    --exclude="__pycache__" \
    --exclude=".git" \
    -C "$APP_DIR" .

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "app-backup-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/app-backup-$DATE.tar.gz"
EOF

chmod +x "/usr/local/bin/backup-$APP_NAME"

# Create daily backup cron job
echo "0 2 * * * /usr/local/bin/backup-$APP_NAME" | crontab -

# Create update script
print_status "Creating update script..."
cat > "/usr/local/bin/update-$APP_NAME" << EOF
#!/bin/bash
set -e

APP_DIR="$APP_DIR"
USER="$USER"
SERVICE_NAME="$SERVICE_NAME"

echo "🔄 Updating $APP_NAME..."

# Backup current version
/usr/local/bin/backup-$APP_NAME

# Stop service
systemctl stop "\$SERVICE_NAME"

# Update code
cd "\$APP_DIR"
sudo -u "\$USER" git pull origin main

# Update dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Test configuration
sudo -u "\$USER" python test_module.py

# Restart service
systemctl start "\$SERVICE_NAME"

# Wait and test
sleep 10
if curl -f -s http://localhost:8501/_stcore/health > /dev/null; then
    echo "✅ Update completed successfully"
else
    echo "❌ Update failed, check logs"
    systemctl status "\$SERVICE_NAME"
    exit 1
fi
EOF

chmod +x "/usr/local/bin/update-$APP_NAME"

# Set up log rotation
print_status "Setting up log rotation..."
cat > "/etc/logrotate.d/$APP_NAME" << EOF
/var/log/$APP_NAME/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    copytruncate
    su $USER $USER
}
EOF

# Create firewall rules (if UFW is available)
if command -v ufw >/dev/null 2>&1; then
    print_status "Configuring firewall..."
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
fi

print_status "🎉 Production deployment completed successfully!"
echo ""
echo -e "${GREEN}Application Details:${NC}"
echo "  - Service: $SERVICE_NAME"
echo "  - Directory: $APP_DIR"
echo "  - User: $USER"
echo "  - URL: http://$(curl -s ifconfig.me || echo 'your-server-ip')"
echo "  - Local URL: http://localhost"
echo ""
echo -e "${GREEN}Management Commands:${NC}"
echo "  - Check status: systemctl status $SERVICE_NAME"
echo "  - View logs: journalctl -u $SERVICE_NAME -f"
echo "  - Restart: systemctl restart $SERVICE_NAME"
echo "  - Update: /usr/local/bin/update-$APP_NAME"
echo "  - Backup: /usr/local/bin/backup-$APP_NAME"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "  1. Configure your domain name in /etc/nginx/sites-available/$APP_NAME"
echo "  2. Set up SSL certificate (Let's Encrypt recommended)"
echo "  3. Configure monitoring and alerting"
echo "  4. Test the application at http://your-server-ip"
echo ""
print_warning "Don't forget to secure your server and configure SSL for production use!"