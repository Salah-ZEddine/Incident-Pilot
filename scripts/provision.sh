#!/bin/bash

set -e

echo "[INFO] Starting provisioning for $(hostname)..."

# Update package index
sudo apt update -y
sudo apt install -y curl gnupg apt-transport-https lsb-release

### --- Install Vector if not installed ---
if ! command -v vector &> /dev/null; then
  echo "[INFO] Vector not found. Installing Vector..."
  bash -c "$(curl -L https://setup.vector.dev)"
  sudo apt-get install -y vector
  sudo systemctl enable vector
  sudo systemctl start vector
  echo "[INFO] Vector installed and started."
else
  echo "[INFO] Vector already installed."
fi

### --- Install Docker only on vector-node1 and vector-node2 ---
HOSTNAME=$(hostname)

if [[ "$HOSTNAME" == "vector-node1" || "$HOSTNAME" == "vector-node2" ]]; then
  if ! command -v docker &> /dev/null; then
    echo "[INFO] Docker not found. Installing Docker on $HOSTNAME..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker vagrant
    echo "[INFO] Docker installed on $HOSTNAME."
  else
    echo "[INFO] Docker already installed on $HOSTNAME."
  fi
else
  echo "[INFO] Skipping Docker install on $HOSTNAME."
fi
