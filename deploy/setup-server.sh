#!/bin/bash

# Django Gym Tracker - Server Setup Script
# Run this script on your VPS to set up the deployment environment

set -e

echo "🚀 Setting up Django Gym Tracker deployment environment..."

# Create gymtracker user if it doesn't exist
if ! id "gymtracker" &>/dev/null; then
    echo "Creating gymtracker user..."
    sudo useradd -m -s /bin/bash gymtracker
    sudo usermod -aG sudo gymtracker
else
    echo "gymtracker user already exists"
fi

# Create deployment directories
echo "Creating deployment directories..."
sudo mkdir -p /srv/gymtracker/app
sudo mkdir -p /srv/gymtracker/data
sudo mkdir -p /srv/gymtracker/backups
sudo mkdir -p /srv/gymtracker/logs

# Set ownership
sudo chown -R gymtracker:gymtracker /srv/gymtracker

# Install uv for the gymtracker user
echo "Installing uv for gymtracker user..."
sudo -u gymtracker bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
sudo -u gymtracker bash -c 'echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.bashrc'

# Enable systemd user services
echo "Enabling systemd user services..."
sudo -u gymtracker systemctl --user daemon-reload
sudo loginctl enable-linger gymtracker

# Copy systemd service file
echo "Installing systemd service..."
sudo cp deploy/gymtracker.service /home/gymtracker/.config/systemd/user/
sudo chown gymtracker:gymtracker /home/gymtracker/.config/systemd/user/gymtracker.service

# Reload systemd and enable service
sudo -u gymtracker systemctl --user daemon-reload
sudo -u gymtracker systemctl --user enable gymtracker

echo "✅ Server setup completed!"
echo ""
echo "Next steps:"
echo "1. Set up your environment variables in /home/gymtracker/.env"
echo "2. Deploy your application using the GitHub Actions workflow"
echo "3. The service will be available at http://your-vps-ip:8098"
echo ""
echo "Useful commands:"
echo "  sudo -u gymtracker systemctl --user status gymtracker"
echo "  sudo -u gymtracker systemctl --user start gymtracker"
echo "  sudo -u gymtracker systemctl --user stop gymtracker"
echo "  sudo -u gymtracker systemctl --user restart gymtracker"
