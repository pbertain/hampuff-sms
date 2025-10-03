# Hampuff SMS Registration System

This document describes the registration system implemented for A2P 10DLC compliance with Twilio SMS services.

## Overview

The registration system allows users to opt-in to receive SMS messages from the Hampuff SMS service. This is required for A2P 10DLC compliance in the United States.

## Features

- **Web-based registration form** at `/register`
- **Phone number normalization** - handles multiple formats (E.164, US formats)
- **SQLite database** for storing registrations
- **Opt-in validation** - SMS responses only sent to registered users
- **Admin endpoint** at `/admin/registrations` for viewing all registrations

## Registration Form Fields

- **Full Name** (required)
- **Amateur Radio Call Sign** (required)
- **Phone Number** (required) - accepts various formats
- **Opt-in Checkbox** (required) - must be checked to register

## Phone Number Formats Supported

The system normalizes all these formats to E.164 format (`+15551234567`):

- `+1-555-111-2222`
- `555 111-2222`
- `(555) 111-2222`
- `5551112222`
- `555-111-2222`
- `+15551112222`

## Database Schema

```sql
CREATE TABLE registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    call_sign TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE,
    phone_normalized TEXT NOT NULL UNIQUE,
    opted_in BOOLEAN NOT NULL DEFAULT 0,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT
);
```

## API Endpoints

### GET /register
Displays the registration form.

### POST /register
Processes registration form submission.

**Form Data:**
- `full_name`: User's full name
- `call_sign`: Amateur radio call sign
- `phone_number`: Phone number
- `opted_in`: "1" if user opts in

**Responses:**
- Success: Registration confirmation message
- Error: Validation error messages

### GET /admin/registrations
Returns JSON with all registrations (admin only).

**Response:**
```json
{
    "registrations": [...],
    "total_count": 10,
    "opted_in_count": 8
}
```

## SMS Integration

The SMS service now checks if incoming messages are from registered users:

- **Registered users**: Receive normal hampuff responses
- **Unregistered users**: Receive message directing them to registration page

## Testing

Run the test script to verify functionality:

```bash
python test_registration.py
```

## Dependencies

- `phonenumbers==8.13.25` - For phone number validation and normalization
- `Flask` - Web framework (already included)

## Security Considerations

- The admin endpoint (`/admin/registrations`) should be protected with authentication in production
- Consider rate limiting for registration attempts
- IP addresses and user agents are logged for audit purposes

## Compliance Notes

This registration system helps ensure compliance with:
- **A2P 10DLC requirements** for US SMS messaging
- **TCPA compliance** by requiring explicit opt-in
- **Twilio's messaging policies** for registered users only
