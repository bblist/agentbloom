#!/bin/bash
# ============================================================
# AgentBloom Production Deployment Script
# Deploys to bloom.nobleblocks.com on Lightsail (52.1.31.54)
# ============================================================
set -euo pipefail

DOMAIN="bloom.nobleblocks.com"
SERVER="52.1.31.54"
SSH_USER="ubuntu"
SSH_KEY="${SSH_KEY:-~/.ssh/lightsail-admasterpro.pem}"
APP_DIR="/home/ubuntu/agentbloom"
REPO_URL="https://github.com/bblist/agentbloom.git"

echo "=== AgentBloom Deployment to $DOMAIN ==="

ssh_cmd() {
    ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER" "$@"
}

scp_cmd() {
    scp -o StrictHostKeyChecking=no -i "$SSH_KEY" "$@"
}

# ─── Step 1: Clone or pull repo ──────────────
echo "[1/8] Syncing code..."
ssh_cmd "if [ -d $APP_DIR ]; then cd $APP_DIR && git pull origin main; else git clone $REPO_URL $APP_DIR; fi"

# ─── Step 2: Upload .env file ───────────────
echo "[2/8] Uploading .env..."
if [ ! -f ".env.production" ]; then
    echo "ERROR: .env.production file not found in project root!"
    echo "Create it from .env.example and fill in production values."
    exit 1
fi
scp_cmd ".env.production" "$SSH_USER@$SERVER:$APP_DIR/.env"

# ─── Step 3: Set up Nginx (HTTP first) ──────
echo "[3/8] Configuring Nginx..."
scp_cmd "deploy/nginx/bloom-http-only.conf" "$SSH_USER@$SERVER:/tmp/bloom.conf"
ssh_cmd "sudo cp /tmp/bloom.conf /etc/nginx/sites-available/bloom.nobleblocks.com && \
         sudo ln -sf /etc/nginx/sites-available/bloom.nobleblocks.com /etc/nginx/sites-enabled/ && \
         sudo rm -f /etc/nginx/sites-enabled/default && \
         sudo mkdir -p /var/www/certbot && \
         sudo nginx -t && sudo systemctl reload nginx"

# ─── Step 4: Open firewall ports ────────────
echo "[4/8] Configuring firewall..."
ssh_cmd "sudo ufw allow 80/tcp 2>/dev/null; sudo ufw allow 443/tcp 2>/dev/null; echo 'Firewall OK'"

# ─── Step 5: Build and start Docker ─────────
echo "[5/8] Building and starting Docker services..."
ssh_cmd "cd $APP_DIR && docker compose -f docker-compose.prod.yml up --build -d"

# ─── Step 6: Wait for services and run migrations ──
echo "[6/8] Running migrations..."
ssh_cmd "cd $APP_DIR && sleep 10 && \
         docker compose -f docker-compose.prod.yml exec -T backend python manage.py makemigrations --noinput && \
         docker compose -f docker-compose.prod.yml exec -T backend python manage.py migrate --noinput"

# ─── Step 7: SSL Certificate ────────────────
echo "[7/8] Obtaining SSL certificate..."
ssh_cmd "sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@nobleblocks.com --redirect"

# Copy full SSL nginx config after certbot modifies it
# (certbot --nginx auto-updates the config)

# ─── Step 8: Final verification ─────────────
echo "[8/8] Verifying deployment..."
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo "   Site:     https://$DOMAIN"
    echo "   API:      https://$DOMAIN/api/v1/"
    echo "   Admin:    https://$DOMAIN/admin/"
else
    echo ""
    echo "⚠️  Site returned HTTP $HTTP_CODE — check logs:"
    echo "   ssh -i $SSH_KEY $SSH_USER@$SERVER"
    echo "   cd $APP_DIR && docker compose -f docker-compose.prod.yml logs --tail=50"
fi

echo ""
echo "=== Post-deploy commands ==="
echo "Create superuser:"
echo "  ssh -i $SSH_KEY $SSH_USER@$SERVER 'cd $APP_DIR && docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser'"
echo ""
echo "View logs:"
echo "  ssh -i $SSH_KEY $SSH_USER@$SERVER 'cd $APP_DIR && docker compose -f docker-compose.prod.yml logs -f --tail=50'"
