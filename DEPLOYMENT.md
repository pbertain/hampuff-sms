# Hampuff SMS Deployment Guide

This document describes the deployment workflow and setup for the Hampuff SMS service.

## Branch Strategy

- **`main`** - Production branch, auto-deploys to `/opt/hampuff-sms`
- **`dev`** - Development branch, auto-deploys to `/opt/hampuff-sms-dev`
- **Feature branches** - Create from `dev`, merge back to `dev` when ready

## Workflow

1. **Feature Development:**
   ```bash
   git checkout dev
   git checkout -b feature/your-feature-name
   # Make changes
   git add .
   git commit -m "Add your feature"
   git push origin feature/your-feature-name
   # Create PR to dev branch
   ```

2. **Testing:**
   ```bash
   git checkout dev
   git merge feature/your-feature-name
   git push origin dev
   # This triggers GitHub Action to deploy to dev environment
   ```

3. **Production Deployment:**
   ```bash
   git checkout main
   git merge dev
   git push origin main
   # This triggers GitHub Action to deploy to production
   ```

## GitHub Actions

### Development Deployment (`deploy-dev.yml`)
- Triggers on push to `dev` branch
- Runs tests first
- Deploys to `/opt/hampuff-sms-dev` on `host74.nird.club`

### Production Deployment (`deploy-prod.yml`)
- Triggers on push to `main` branch
- Runs tests first
- Deploys to `/opt/hampuff-sms` on `host74.nird.club`

## Ansible Configuration

### Inventory
- **Host Group:** `hampuff-sms`
- **Host:** `host74.nird.club`
- **User:** `ansible`
- **SSH Key:** `~/.ssh/keys/nirdclub__id_ed25519`

### Secrets Management

1. **Create Ansible Vault:**
   ```bash
   ansible-vault create ansible/group_vars/hampuff-sms/vault.yml
   ```

2. **Edit secrets:**
   ```bash
   ansible-vault edit ansible/group_vars/hampuff-sms/vault.yml
   ```

3. **Set GitHub Secret:**
   - Go to GitHub repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Add secret: `ANSIBLE_VAULT_PASSWORD` with your vault password

### Required Secrets
```yaml
# Flask configuration
flask_secret_key: "your-secret-key-here"
flask_debug: false

# Twilio configuration
twilio_account_sid: "your-twilio-account-sid"
twilio_auth_token: "your-twilio-auth-token"

# Environment
environment: "production"  # or "development"
```

## Manual Deployment

### Development
```bash
ansible-playbook \
  --ask-vault-pass \
  -u ansible \
  --private-key ~/.ssh/keys/nirdclub__id_ed25519 \
  -i host74.nird.club, \
  -e "deploy_path=/opt/hampuff-sms-dev" \
  -e "environment=development" \
  ansible/main.yml
```

### Production
```bash
ansible-playbook \
  --ask-vault-pass \
  -u ansible \
  --private-key ~/.ssh/keys/nirdclub__id_ed25519 \
  -i host74.nird.club, \
  -e "deploy_path=/opt/hampuff-sms" \
  -e "environment=production" \
  ansible/main.yml
```

## Service Management

### Check Status
```bash
sudo systemctl status hampuff-sms
```

### View Logs
```bash
sudo journalctl -u hampuff-sms -f
```

### Restart Service
```bash
sudo systemctl restart hampuff-sms
```

## Environment Variables

The service uses the following environment variables (set via Ansible vault):

- `SECRET_KEY` - Flask secret key
- `FLASK_DEBUG` - Debug mode (true/false)
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `TWILIO_AUTH_TOKEN` - Twilio auth token
- `ENVIRONMENT` - Environment (production/development)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING)

## Testing

### Local Testing
```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
python test_ci.py

# Run the application
python app.py
```

### CI Testing
Tests run automatically on:
- Push to `dev` branch
- Push to `main` branch
- Pull requests to `dev` or `main`

## Monitoring

### Health Check
- **Endpoint:** `GET /health`
- **Response:** `{"status": "healthy", "service": "hampuff-sms"}`

### Registration System
- **Endpoint:** `GET /register` - Registration form
- **Endpoint:** `POST /register` - Process registration
- **Admin:** `GET /admin/registrations` - View all registrations

### SMS Endpoint
- **Endpoint:** `POST /sms` - Twilio webhook
- **Requires:** User must be registered and opted-in

## Troubleshooting

### Common Issues

1. **Service won't start:**
   - Check logs: `sudo journalctl -u hampuff-sms`
   - Verify Python dependencies: `pip list`
   - Check file permissions

2. **Database issues:**
   - Check SQLite file permissions
   - Verify database path in logs

3. **Twilio webhook issues:**
   - Verify webhook URL in Twilio console
   - Check if user is registered and opted-in
   - Review SMS service logs

### Log Locations
- **Service logs:** `sudo journalctl -u hampuff-sms`
- **Application logs:** Check Flask logging configuration
- **Database:** SQLite file in application directory

## Security Notes

- Ansible vault password should be strong and unique
- GitHub secrets should be rotated regularly
- SSH keys should have proper permissions (600)
- Service runs as non-root user (`hampuff-sms`)
- Database file has restricted permissions (600)
