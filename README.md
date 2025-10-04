# Hampuff SMS Web Service

A Flask-based web service that handles SMS requests from Twilio and provides ham radio solar data responses. The service is designed for production deployment with Ansible and runs behind NGINX for TLS termination.

## Features

- **SMS Processing**: Handles incoming SMS requests from Twilio
- **Ham Radio Data**: Provides solar flux, A/K indices, sunspots, and MUF data
- **Timezone Support**: Supports both Eastern and Pacific timezones
- **Production Ready**: Includes logging, error handling, and health checks
- **Ansible Deployment**: Complete automation for production deployment
- **Security**: Runs behind reverse proxy, includes security headers

## Architecture

```
┌─────────────┐    HTTPS    ┌─────────────┐    HTTP     ┌─────────────┐
│   Twilio    │ ──────────→ │    NGINX    │ ──────────→ │ Hampuff SMS │
│             │             │ (TLS Term)  │             │ (Port 15015)│
└─────────────┘             └─────────────┘             └─────────────┘
```

## Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the service**:
   ```bash
   python app.py
   ```

3. **Test the service**:
   ```bash
   python test_service.py
   ```

### Production Deployment

1. **Configure Ansible inventory**:
   ```bash
   cd ansible
   # Edit inventory.yml with your server details
   ```

2. **Deploy**:
   ```bash
   ansible-playbook -i inventory.yml main.yml
   ```

## API Endpoints

### POST /sms
Handles incoming SMS requests from Twilio.

**Request Body** (form-encoded):
- `Body`: The SMS message content

**Response**: TwiML formatted response for Twilio

**Example**:
```bash
curl -X POST http://localhost:15015/sms \
  -d "Body=hampuffe"
```

### GET /health
Health check endpoint for monitoring.

**Response**:
```json
{
  "status": "healthy",
  "service": "hampuff-sms"
}
```

## SMS Commands

- **`hampuffe`**: Get solar data in Eastern timezone
- **`hampuffp`**: Get solar data in Pacific timezone
- **4-character codes**: Redirect to Airpuff service
- **Profanity**: Returns humorous responses
- **Other**: Default "wrong number" message

## Configuration

The service uses environment variables for configuration:

- `HOST`: Service host (default: 0.0.0.0)
- `PORT`: Service port (default: 15015)
- `FLASK_DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

## Project Structure

```
hampuff-sms/
├── app.py                 # Main Flask application
├── wsgi.py               # WSGI entry point for production
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── test_service.py       # Local testing script
├── lib/
│   └── hampuff_lib.py   # Ham radio data provider
├── services/
│   └── sms_service.py   # SMS processing logic
└── ansible/              # Deployment automation
    ├── main.yml         # Main playbook
    ├── tasks/           # Task definitions
    ├── handlers/        # Service handlers
    └── files/           # Configuration files
```

## Dependencies

- **Flask**: Web framework
- **Twilio**: SMS processing
- **Requests**: HTTP client for solar data
- **xmltodict**: XML parsing
- **pytz**: Timezone handling
- **Gunicorn**: WSGI server for production

## Development

### Code Style
- Follows PEP 8 standards
- Type hints where appropriate
- Comprehensive docstrings
- Modular design for maintainability

### Testing
Run the test script to verify functionality:
```bash
python test_service.py
```

## Deployment

### System Requirements
- Ubuntu/Debian server
- Python 3.9+
- Systemd support
- NGINX (for reverse proxy)

### Service Management
```bash
# Check status
sudo systemctl status hampuff-sms

# View logs
sudo journalctl -u hampuff-sms -f

# Restart service
sudo systemctl restart hampuff-sms
```

## Security Considerations

- Service runs on localhost only (127.0.0.1)
- TLS termination handled by NGINX
- Dedicated system user for isolation
- Input validation and sanitization
- Security headers in responses

## Monitoring

The service includes:
- Health check endpoint (`/health`)
- Structured logging
- Systemd integration for process management
- Automatic restart on failure

## Contributing

1. Follow PEP 8 coding standards
2. Add type hints for new functions
3. Include docstrings for all public methods
4. Test changes with the test script
5. Update documentation as needed

## License

See LICENSE file for details.
# Trigger deployment Fri Oct  3 20:26:08 MDT 2025
