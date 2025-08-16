#!/bin/bash
# Hampuff SMS Deployment Script

set -e

echo "🚀 Deploying Hampuff SMS Web Service..."

# Check if we're in the right directory
if [ ! -f "ansible/main.yml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if Ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo "❌ Error: Ansible is not installed. Please install it first."
    echo "   On macOS: brew install ansible"
    echo "   On Ubuntu: sudo apt install ansible"
    exit 1
fi

# Check if inventory is configured
if [ ! -f "ansible/inventory.yml" ] || grep -q "your-server-ip-here" ansible/inventory.yml; then
    echo "⚠️  Warning: Please configure ansible/inventory.yml with your server details first"
    echo "   Edit the file and replace placeholder values with your actual server information"
    exit 1
fi

# Deploy
echo "📦 Running Ansible deployment..."
cd ansible
ansible-playbook -i inventory.yml main.yml

echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Configure NGINX to proxy to 127.0.0.1:15015"
echo "   2. Set up TLS certificates"
echo "   3. Configure Twilio webhook URL"
echo ""
echo "🔍 Check service status:"
echo "   ssh your-server 'sudo systemctl status hampuff-sms'"
echo ""
echo "📝 View logs:"
echo "   ssh your-server 'sudo journalctl -u hampuff-sms -f'"
