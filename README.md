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

## REST API Documentation

### JSON API (`/sms/api/v1/`)
The JSON API returns structured data and includes CORS headers for browser access. See `openapi.yaml` for complete OpenAPI specification.

**Interactive Documentation:**
- Swagger UI: Available at `/api-docs/swagger` (when configured)
- ReDoc: Available at `/api-docs/redoc` (when configured)

### Plain Text API (`/sms/curl/v1/`)
The plain text API returns responses identical to SMS format, ideal for shell scripts and cURL.

#### Get Help Information
```bash
curl https://sms.hampuff.com/sms/curl/v1/help
```

#### Get Propagation Data
```bash
# Get propagation data for Eastern Time
curl https://sms.hampuff.com/sms/curl/v1/propagation/EST

# Short alias
curl https://sms.hampuff.com/sms/curl/v1/prop/PDT

# All timezones supported (case-insensitive)
curl https://sms.hampuff.com/sms/curl/v1/prop/HST
curl https://sms.hampuff.com/sms/curl/v1/propagation/AKST
```

**Supported Timezones:**
- US Continental: EST, EDT, CST, CDT, MST, MDT, PST, PDT
- Alaska: AKST, AKDT
- Hawaii: HST
- Puerto Rico: AST
- Guam: ChST, GST
- Universal: UTC, GMT

#### Register New User
```bash
# Using JSON
curl -X POST https://sms.hampuff.com/sms/curl/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "call_sign": "W1ABC",
    "phone_number": "+15551234567",
    "opted_in": true
  }'

# Using form data
curl -X POST https://sms.hampuff.com/sms/curl/v1/register \
  -d "full_name=John Doe" \
  -d "call_sign=W1ABC" \
  -d "phone_number=+15551234567" \
  -d "opted_in=true"
```

**Note:** All fields are required for A2P 10DLC compliance. Phone numbers are automatically normalized to E.164 format.

#### Opt-In Existing User
```bash
# Opt-in a user who has already registered via web form
curl -X POST https://sms.hampuff.com/sms/curl/v1/start/+15551234567

# Alternative endpoint (alias)
curl -X POST https://sms.hampuff.com/sms/curl/v1/register/+15551234567
```

**Note:** This will return 404 if the user is not already registered. Users must register first at www.hampuff.com/register or via the `/register` API endpoint.

#### Opt-Out User
```bash
# Opt-out a user from SMS service
curl -X POST https://sms.hampuff.com/sms/curl/v1/stop/+15551234567

# Alternative endpoint (alias)
curl -X POST https://sms.hampuff.com/sms/curl/v1/unregister/+15551234567
```

**Note:** This works even if the user is not currently registered (returns success confirmation).

### Rate Limiting
All API endpoints are rate-limited per IP address:
- Help/Propagation endpoints: **100 requests/hour**
- Registration endpoint: **10 requests/hour**
- Opt-in/Out endpoints: **20 requests/hour**

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response.

### Error Responses
Errors follow a consistent format:
```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created (registration successful)
- `400` - Bad Request (invalid input, missing fields)
- `404` - Not Found (user not registered for opt-in)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

For complete API documentation, see the [OpenAPI specification](openapi.yaml) or visit the [API Help Page](api-help.html).

## SMS Commands

Send these commands via SMS to the HamPuff SMS number:

### Propagation Data
- **`prop [TIMEZONE]`**: Get solar propagation data (e.g., `prop EST`, `prop PDT`)
- **`propagation [TIMEZONE]`**: Same as above
- **`hampuffe`**: Legacy format - Eastern timezone
- **`hampuffp`**: Legacy format - Pacific timezone

**Supported Timezones:** EST, EDT, CST, CDT, MST, MDT, PST, PDT, AKST, AKDT, HST, AST, ChST, GST, UTC, GMT

### Registration Commands
- **`START`** or **`REGISTER`**: Opt-in to SMS service (if already registered via web)
- **`STOP`** or **`UNREGISTER`**: Opt-out from SMS service

### Help
- **`HELP`** or **`?`**: Show help message with all available commands

### Other
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
