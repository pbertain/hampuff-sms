#!/usr/bin/env python3
"""
Hampuff SMS Web Service

A Flask-based web service that handles SMS requests from Twilio
and provides ham radio solar data responses.
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from services.sms_service import SMSHandler
from models import RegistrationDatabase
from config import Config


def get_version():
    """Get the current application version."""
    try:
        # Try to read version from environment-specific file first
        env = os.environ.get('ENVIRONMENT', 'production')
        version_file = f"version.{env}.txt" if env in ['development', 'production'] else "version.txt"
        
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        elif os.path.exists("version.txt"):
            with open("version.txt", 'r') as f:
                return f.read().strip()
        else:
            return "unknown"
    except Exception:
        return "unknown"


def create_app(config_class=Config):
    """Application factory pattern for Flask app creation."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable sessions for flash messages
    app.secret_key = app.config.get('SECRET_KEY', 'dev-secret-key')
    
    # Initialize SMS handler and database
    sms_handler = SMSHandler()
    db = RegistrationDatabase()
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy", 
            "service": "hampuff-sms",
            "version": get_version(),
            "environment": os.environ.get('ENVIRONMENT', 'production')
        }
    
    @app.route("/sms", methods=["POST"])
    def sms_reply():
        """Handle incoming SMS requests from Twilio."""
        return sms_handler.handle_sms_request()
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        """Temporary registration endpoint - will be moved to main website."""
        return {"message": "Registration service moved to www.hampuff.com/register", "status": "moved"}, 301
    
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = "0"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"]
    )
