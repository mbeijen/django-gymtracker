#!/bin/bash

# Django Gym Tracker - Server Setup Script
# Run this script on your VPS to set up the deployment environment

set -e

echo "🚀 Setting up Django Gym Tracker deployment environment..."

# Create gymtracker user if it doesn't exist
if ! id "gymtracker" &>/dev/null; then
    echo "Creating gymtracker user..."
    sudo useradd -m -s /bin/bash gymtracker
else
    echo "gymtracker user already exists"
fi

# Create deployment directories (assuming /srv/gymtracker exists and is owned by gymtracker)
echo "Creating deployment directories..."
mkdir -p /srv/gymtracker/app
mkdir -p /srv/gymtracker/data
mkdir -p /srv/gymtracker/backups
mkdir -p /srv/gymtracker/logs

# Install uv for the gymtracker user
echo "Installing uv for gymtracker user..."
sudo -u gymtracker bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
sudo -u gymtracker bash -c 'echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.bashrc'

# Enable systemd user services
echo "Enabling systemd user services..."
sudo -u gymtracker systemctl --user daemon-reload
sudo loginctl enable-linger gymtracker

# Copy systemd service file to user directory
echo "Installing systemd service..."
sudo -u gymtracker mkdir -p /home/gymtracker/.config/systemd/user/
sudo -u gymtracker cp deploy/gymtracker.service /home/gymtracker/.config/systemd/user/

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
