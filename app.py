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
        return {"status": "healthy", "service": "hampuff-sms"}
    
    @app.route("/sms", methods=["POST"])
    def sms_reply():
        """Handle incoming SMS requests from Twilio."""
        return sms_handler.handle_sms_request()
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        """Handle user registration for SMS opt-in."""
        if request.method == "GET":
            return render_template("register.html")
        
        # Handle POST request
        try:
            # Get form data
            full_name = request.form.get("full_name", "").strip()
            call_sign = request.form.get("call_sign", "").strip().upper()
            phone_number = request.form.get("phone_number", "").strip()
            opted_in = request.form.get("opted_in") == "1"
            
            # Validate required fields
            if not all([full_name, call_sign, phone_number]):
                flash("Please fill in all required fields.", "error")
                return render_template("register.html")
            
            if not opted_in:
                flash("You must opt-in to receive SMS messages.", "error")
                return render_template("register.html")
            
            # Validate call sign format (basic validation)
            if len(call_sign) < 3 or len(call_sign) > 7:
                flash("Please enter a valid amateur radio call sign.", "error")
                return render_template("register.html")
            
            # Register user
            registration = db.register_user(
                full_name=full_name,
                call_sign=call_sign,
                phone_number=phone_number,
                opted_in=opted_in,
                ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent")
            )
            
            app.logger.info(f"New registration: {full_name} ({call_sign}) - {registration['phone_normalized']}")
            
            flash(f"Registration successful! You are now opted-in to receive SMS messages at {registration['phone_normalized']}", "success")
            return render_template("register.html")
            
        except ValueError as e:
            flash(str(e), "error")
            return render_template("register.html")
        except Exception as e:
            app.logger.error(f"Registration error: {str(e)}")
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("register.html")
    
    @app.route("/admin/registrations", methods=["GET"])
    def admin_registrations():
        """Admin endpoint to view all registrations."""
        # In production, you'd want proper authentication here
        registrations = db.get_all_registrations()
        return {
            "registrations": registrations,
            "total_count": len(registrations),
            "opted_in_count": len([r for r in registrations if r["opted_in"]])
        }
    
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
