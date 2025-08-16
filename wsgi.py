#!/usr/bin/env python3
"""
WSGI entry point for production deployment.

This file is used by WSGI servers like Gunicorn or uWSGI to serve the application.
"""

import os
from app import create_app

# Set environment for production
os.environ.setdefault('FLASK_ENV', 'production')

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    app.run()
