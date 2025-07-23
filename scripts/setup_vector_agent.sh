#!/bin/bash

set -e

echo "🚀 Starting Vector agent setup..."

# 1. Ensure required folders are executable
echo "🔧 Setting execute permissions for Docker log paths..."
chmod +x /var/lib/docker
chmod +x /var/lib/docker/containers

# 2. Add 'vector' and 'vagrant' users to 'docker' group
echo "👥 Adding users to docker group..."
usermod -aG docker vector || echo "User 'vector' does not exist or already added."
usermod -aG docker vagrant || echo "User 'vagrant' does not exist or already added."

# 3. Add 'vector' user to 'systemd-journal' group for log access
echo "👥 Adding 'vector' user to 'systemd-journal' group..."
usermod -aG systemd-journal vector || echo "User 'vector' does not exist or already added."

# 4. Optional: create log buffer directory for Vector (if using disk buffer)
BUFFER_DIR="/var/lib/vector/buffer"
echo "📁 Ensuring buffer directory exists: $BUFFER_DIR"
mkdir -p "$BUFFER_DIR"
chown vector:vector "$BUFFER_DIR"
chmod 750 "$BUFFER_DIR"

# 5. Enable and restart Vector
echo "🌀 Restarting and enabling Vector agent..."
systemctl enable vector
systemctl restart vector

# 6. Remind user to re-login for group changes
echo -e "\n⚠️ Please log out and log back in (or run \`newgrp docker\`) for group changes to take effect."

echo -e "\n✅ Vector agent setup completed successfully!"
