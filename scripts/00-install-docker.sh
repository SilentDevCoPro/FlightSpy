#!/bin/bash
set -euo pipefail

# Safety check to prevent running as root
if [[ $EUID -eq 0 ]]; then
    echo "ERROR: This script must NOT be run as root. Run it as a regular user with sudo privileges."
    exit 1
fi

# Install Docker
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=arm64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin

# Configure user permissions
sudo usermod -aG docker "$USER"

# Install Docker Compose system-wide
COMPOSE_VERSION="v2.23.3"
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL "https://github.com/docker/compose/releases/download/$COMPOSE_VERSION/docker-compose-linux-aarch64" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Verification steps
echo -e "\n\u001b[34mVerifying installations:\u001b[0m"
sudo docker --version
sudo docker compose version

# Test Docker functionality
echo -e "\n\u001b[34mTesting Docker:\u001b[0m"
sudo docker run --rm hello-world

# Create isolated test environment
TEST_DIR=$(mktemp -d)
trap 'sudo docker compose -f "$TEST_DIR/docker-compose.yml" down --volumes >/dev/null 2>&1 || true; rm -rf "$TEST_DIR"' EXIT

cat <<EOF > "$TEST_DIR/docker-compose.yml"
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
EOF

# Test Docker Compose
echo -e "\n\u001b[34mTesting Docker Compose:\u001b[0m"
pushd "$TEST_DIR" >/dev/null
sudo docker compose up -d
sleep 5  # Allow time for container to start
sudo docker compose ps
popd >/dev/null

echo -e "\n\u001b[32mSUCCESS: All tests completed successfully\u001b[0m"
echo "NOTE: Log out and back in to use Docker without 'sudo'"