# Hampuff SMS Ansible Deployment

This directory contains Ansible playbooks and configuration files for deploying the Hampuff SMS Web Service.

## Prerequisites

- Ansible 2.9+
- Target server running Ubuntu/Debian
- SSH access to target server
- Python 3.9+ on target server

## Configuration

1. Edit `inventory.yml` with your server details:
   - Replace `your-server-ip-here` with your actual server IP
   - Replace `your-ssh-user` with your SSH username
   - Update the SSH key path if needed

2. Ensure your SSH key has access to the target server

## Deployment

Run the deployment playbook:

```bash
ansible-playbook -i inventory.yml main.yml
```

## Service Management

After deployment, the service will be managed by systemd:

```bash
# Check status
sudo systemctl status hampuff-sms

# Start service
sudo systemctl start hampuff-sms

# Stop service
sudo systemctl stop hampuff-sms

# Restart service
sudo systemctl restart hampuff-sms

# View logs
sudo journalctl -u hampuff-sms -f
```

## Architecture

The service runs on `127.0.0.1:15015` and is designed to work behind an NGINX reverse proxy for TLS termination. The service:

- Listens only on localhost for security
- Runs as a dedicated system user
- Uses Gunicorn with 2 workers
- Automatically restarts on failure
- Logs to systemd journal

## NGINX Configuration

Configure NGINX to proxy requests to `127.0.0.1:15015` and handle TLS termination. The service expects POST requests to `/sms` from Twilio.

**Note**: NGINX configuration is handled by a separate Ansible playbook.
