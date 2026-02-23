#!/usr/bin/env bash
# AgentBloom — Initial server setup script for Ubuntu 24.04 (Lightsail)
# Run as root or with sudo

set -euo pipefail

echo "=== AgentBloom Server Setup ==="

# ─── System Updates ────────────────────────
echo "→ Updating system packages..."
apt-get update -y && apt-get upgrade -y

# ─── Install Dependencies ─────────────────
echo "→ Installing dependencies..."
apt-get install -y \
    nginx \
    certbot python3-certbot-nginx \
    docker.io docker-compose-v2 \
    git \
    curl \
    ufw

# ─── Docker Setup ─────────────────────────
echo "→ Configuring Docker..."
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# ─── Firewall ─────────────────────────────
echo "→ Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# ─── Clone Repository ─────────────────────
echo "→ Cloning repository..."
if [ ! -d /opt/agentbloom ]; then
    git clone https://github.com/bblist/agentbloom.git /opt/agentbloom
fi
cd /opt/agentbloom

# ─── SSL Certificate ─────────────────────
echo "→ Obtaining SSL certificate..."
certbot --nginx -d agentbloom.nobleblocks.com --non-interactive --agree-tos --email admin@nobleblocks.com || true

# ─── Nginx Config ─────────────────────────
echo "→ Setting up Nginx..."
cp deploy/nginx/agentbloom.conf /etc/nginx/sites-available/agentbloom
ln -sf /etc/nginx/sites-available/agentbloom /etc/nginx/sites-enabled/agentbloom
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# ─── Create .env file ─────────────────────
if [ ! -f /opt/agentbloom/backend/.env ]; then
    echo "→ Creating .env file (EDIT THIS!)..."
    cp /opt/agentbloom/backend/.env.example /opt/agentbloom/backend/.env
    echo "⚠️  IMPORTANT: Edit /opt/agentbloom/backend/.env with production values!"
fi

# ─── Docker Compose Up ────────────────────
echo "→ Starting services..."
cd /opt/agentbloom
docker compose up -d --build

echo ""
echo "=== Setup Complete ==="
echo "→ Site: https://agentbloom.nobleblocks.com"
echo "→ Edit: /opt/agentbloom/backend/.env"
echo "→ Logs: docker compose logs -f"
