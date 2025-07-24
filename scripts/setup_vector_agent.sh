#!/bin/bash

set -e

echo "🚀 Starting Vector agent setup..."

# 1. Create vector group if it doesn't exist
if ! getent group vector >/dev/null; then
    echo "➕ Creating 'vector' group..."
    groupadd --system vector
fi

# 2. Configure Docker directory permissions
echo "🔧 Setting up Docker log permissions..."
chmod +x /var/lib/docker
chmod +x /var/lib/docker/containers/
chown -R root:vector /var/lib/docker/containers/
find /var/lib/docker/containers/ -type d -exec chmod 2750 {} \;
find /var/lib/docker/containers/ -name "*-json.log" -exec chmod 640 {} \;

chmod -R g+r /var/lib/docker/containers/
chown -R root:vector /var/lib/docker/containers/

# 3. Configure users and groups
echo "👥 Configuring user permissions..."
usermod -aG vector vector 2>/dev/null || echo "ℹ️ User 'vector' not modified"
usermod -aG vector vagrant 2>/dev/null || echo "ℹ️ User 'vagrant' not modified"
usermod -aG docker vector 2>/dev/null || echo "ℹ️ Couldn't add vector to docker group"
usermod -aG systemd-journal vector 2>/dev/null || echo "ℹ️ Couldn't add vector to systemd-journal group"
usermod -aG vector,docker vector

# 4. Set up Vector's log directory
BUFFER_DIR="/var/log/vector"
echo "📁 Creating Vector buffer directory: $BUFFER_DIR"
mkdir -p "$BUFFER_DIR"
chown vector:vector "$BUFFER_DIR"
chmod 770 "$BUFFER_DIR"

# 5. Enable and restart Vector service
echo "🔄 Starting Vector service..."
systemctl enable --now vector 2>/dev/null || {
    echo "❌ Failed to enable Vector service"
    systemctl restart vector 2>/dev/null || echo "❌ Failed to restart Vector"
}

# 6. PROPER permission verification (checks as the vector user)
echo "🔍 Verifying permissions..."
sudo -u vector test -r /var/lib/docker/containers/ || echo "⚠️ Vector cannot read Docker containers"
sudo -u vector test -w "$BUFFER_DIR" || echo "⚠️ Vector cannot write to buffer directory"

# 7. Important reminder
echo -e "\n⚠️ Critical: Log out and back in (or run 'newgrp vector') for group changes to take effect!"
echo -e "\n✅ Vector agent setup completed!"

##if it didn't work, try to run these commands:
##sudo chmod -R g+r /var/lib/docker/containers/
## sudo chown -R root:vector /var/lib/docker/containers/
## usermod -aG vector,docker vector
## it worked when vector didn't catch containers message logs but only catches journald docker logs 
## restart vector service