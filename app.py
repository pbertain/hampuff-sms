#!/usr/bin/env python3
"""
Hampuff SMS Web Service

A Flask-based web service that handles SMS requests from Twilio
and provides ham radio solar data responses.
"""

import os
from flask import Flask
from services.sms_service import SMSHandler
from config import Config


def create_app(config_class=Config):
    """Application factory pattern for Flask app creation."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize SMS handler
    sms_handler = SMSHandler()
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint for monitoring."""
        return {"status": "healthy", "service": "hampuff-sms"}
    
    @app.route("/sms", methods=["POST"])
    def sms_reply():
        """Handle incoming SMS requests from Twilio."""
        return sms_handler.handle_sms_request()
    
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
