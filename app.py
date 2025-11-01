#!/usr/bin/env python3
"""
Hampuff SMS Web Service

A Flask-based web service that handles SMS requests from Twilio
and provides ham radio solar data responses.
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
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
    
    # Initialize rate limiter (needs to be available for decorators)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per hour", "50 per minute"],
        storage_uri="memory://",
        strategy="fixed-window"
    )
    # Store limiter in app context for access in routes
    app.limiter = limiter
    
    # Initialize CORS for API endpoints
    CORS(app, resources={
        r"/sms/api/*": {
            "origins": "*",
            "methods": ["GET"],
            "allow_headers": ["Content-Type"]
        }
    })
    
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
    
    # JSON API endpoints
    @app.route("/sms/api/v1/help", methods=["GET"])
    @limiter.limit("100 per hour")
    def api_help():
        """JSON API help endpoint."""
        logger = logging.getLogger(__name__)
        try:
            help_text = sms_handler._get_help_message()
            return jsonify({
                "help": help_text,
                "format": "text",
                "version": "v1"
            })
        except Exception as e:
            logger.error(f"Error in API help endpoint: {str(e)}")
            return jsonify({"error": "Failed to retrieve help information"}), 500
    
    @app.route("/sms/api/v1/propagation/<timezone>", methods=["GET"])
    @app.route("/sms/api/v1/prop/<timezone>", methods=["GET"])
    @limiter.limit("100 per hour")
    def api_propagation(timezone):
        """JSON API propagation endpoint."""
        logger = logging.getLogger(__name__)
        try:
            data = sms_handler.get_propagation_data_json(timezone.upper())
            return jsonify(data)
        except ValueError as e:
            logger.warning(f"Invalid timezone requested: {timezone} - {str(e)}")
            return jsonify({
                "error": "Invalid timezone code",
                "timezone": timezone,
                "message": str(e),
                "supported_timezones": [
                    "EST", "EDT", "CST", "CDT", "MST", "MDT", "PST", "PDT",
                    "AKST", "AKDT", "HST", "AST", "ChST", "GST", "UTC", "GMT"
                ]
            }), 400
        except Exception as e:
            logger.error(f"Error in API propagation endpoint: {str(e)}")
            return jsonify({"error": "Failed to retrieve propagation data"}), 500
    
    # Plain text (cURL-friendly) API endpoints
    @app.route("/sms/curl/v1/help", methods=["GET"])
    @limiter.limit("100 per hour")
    def curl_help():
        """Plain text help endpoint for cURL."""
        logger = logging.getLogger(__name__)
        try:
            help_text = sms_handler._get_help_message()
            response = app.response_class(
                response=help_text,
                status=200,
                mimetype='text/plain'
            )
            return response
        except Exception as e:
            logger.error(f"Error in curl help endpoint: {str(e)}")
            return app.response_class(
                response=f"Error: Failed to retrieve help information\n{str(e)}",
                status=500,
                mimetype='text/plain'
            )
    
    @app.route("/sms/curl/v1/propagation/<timezone>", methods=["GET"])
    @app.route("/sms/curl/v1/prop/<timezone>", methods=["GET"])
    @limiter.limit("100 per hour")
    def curl_propagation(timezone):
        """Plain text propagation endpoint for cURL (matches SMS format)."""
        logger = logging.getLogger(__name__)
        try:
            # Get propagation data (same format as SMS, without consent message)
            data = sms_handler.get_propagation_data(timezone.upper(), include_consent=False)
            response = app.response_class(
                response=data,
                status=200,
                mimetype='text/plain'
            )
            return response
        except ValueError as e:
            logger.warning(f"Invalid timezone requested: {timezone} - {str(e)}")
            error_msg = (
                f"Invalid timezone code: {timezone}\n"
                f"Supported timezones: EST, EDT, CST, CDT, MST, MDT, PST, PDT, "
                f"AKST, AKDT, HST, AST, ChST, GST, UTC, GMT"
            )
            return app.response_class(
                response=error_msg,
                status=400,
                mimetype='text/plain'
            )
        except Exception as e:
            logger.error(f"Error in curl propagation endpoint: {str(e)}")
            return app.response_class(
                response=f"Error: Failed to retrieve propagation data\n{str(e)}",
                status=500,
                mimetype='text/plain'
            )
    
    # Registration API endpoints (JSON)
    @app.route("/sms/api/v1/register", methods=["POST"])
    @limiter.limit("10 per hour")
    def api_register():
        """Register a new user via API (requires all fields for A2P 10DLC compliance)."""
        logger = logging.getLogger(__name__)
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "error": "Invalid request",
                    "message": "Request body must be JSON"
                }), 400
            
            # Validate required fields
            required_fields = ['full_name', 'call_sign', 'phone_number', 'opted_in']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    "error": "Missing required fields",
                    "missing_fields": missing_fields,
                    "required_fields": required_fields
                }), 400
            
            # Get IP address and user agent
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            # Register user
            try:
                result = db.register_user(
                    full_name=data['full_name'],
                    call_sign=data['call_sign'],
                    phone_number=data['phone_number'],
                    opted_in=bool(data['opted_in']),
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                logger.info(f"API registration successful: {result['phone_normalized']}")
                return jsonify({
                    "status": "success",
                    "message": "Registration successful",
                    "data": {
                        "id": result['id'],
                        "phone_normalized": result['phone_normalized'],
                        "opted_in": result['opted_in']
                    }
                }), 201
            except ValueError as e:
                logger.warning(f"API registration failed: {str(e)}")
                return jsonify({
                    "error": "Registration failed",
                    "message": str(e)
                }), 400
                
        except Exception as e:
            logger.error(f"Error in API registration endpoint: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "message": "Failed to process registration"
            }), 500
    
    @app.route("/sms/api/v1/start/<phone_number>", methods=["POST"])
    @app.route("/sms/api/v1/register/<phone_number>", methods=["POST"])
    @limiter.limit("20 per hour")
    def api_start(phone_number):
        """Opt-in an already registered user via API."""
        logger = logging.getLogger(__name__)
        try:
            # Check if user exists
            user = db.get_user_by_phone(phone_number)
            if not user:
                return jsonify({
                    "error": "User not found",
                    "message": "Phone number not registered. Please register first at www.hampuff.com/register",
                    "phone_number": phone_number
                }), 404
            
            # Opt them in
            success = db.update_opt_in_status(phone_number, True)
            if success:
                logger.info(f"API opt-in successful: {phone_number}")
                return jsonify({
                    "status": "success",
                    "message": "User opted in successfully",
                    "phone_normalized": user.get('phone_normalized'),
                    "opted_in": True
                }), 200
            else:
                return jsonify({
                    "error": "Update failed",
                    "message": "Failed to update opt-in status"
                }), 500
                
        except Exception as e:
            logger.error(f"Error in API opt-in endpoint: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "message": "Failed to process opt-in"
            }), 500
    
    @app.route("/sms/api/v1/stop/<phone_number>", methods=["POST"])
    @app.route("/sms/api/v1/unregister/<phone_number>", methods=["POST"])
    @limiter.limit("20 per hour")
    def api_stop(phone_number):
        """Opt-out a user via API."""
        logger = logging.getLogger(__name__)
        try:
            # Try to opt them out (works even if not registered)
            success = db.update_opt_in_status(phone_number, False)
            if success:
                logger.info(f"API opt-out successful: {phone_number}")
                return jsonify({
                    "status": "success",
                    "message": "User opted out successfully",
                    "opted_in": False
                }), 200
            else:
                # User not found, but we'll still confirm
                logger.info(f"API opt-out requested for unregistered number: {phone_number}")
                return jsonify({
                    "status": "success",
                    "message": "Phone number not currently registered. No action needed.",
                    "opted_in": False
                }), 200
                
        except Exception as e:
            logger.error(f"Error in API opt-out endpoint: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "message": "Failed to process opt-out"
            }), 500
    
    # Registration API endpoints (Plain text / cURL)
    @app.route("/sms/curl/v1/register", methods=["POST"])
    @limiter.limit("10 per hour")
    def curl_register():
        """Register a new user via plain text API."""
        logger = logging.getLogger(__name__)
        try:
            # Accept both JSON and form data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
                # Convert opted_in from string to bool
                if 'opted_in' in data:
                    data['opted_in'] = data['opted_in'].lower() in ['true', '1', 'yes']
            
            if not data:
                return app.response_class(
                    response="Error: Invalid request - no data provided",
                    status=400,
                    mimetype='text/plain'
                )
            
            # Validate required fields
            required_fields = ['full_name', 'call_sign', 'phone_number', 'opted_in']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return app.response_class(
                    response=f"Error: Missing required fields: {', '.join(missing_fields)}",
                    status=400,
                    mimetype='text/plain'
                )
            
            # Get IP address and user agent
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            # Register user
            try:
                result = db.register_user(
                    full_name=data['full_name'],
                    call_sign=data['call_sign'],
                    phone_number=data['phone_number'],
                    opted_in=bool(data['opted_in']),
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                logger.info(f"cURL registration successful: {result['phone_normalized']}")
                return app.response_class(
                    response=f"Registration successful\nPhone: {result['phone_normalized']}\nOpted in: {result['opted_in']}",
                    status=201,
                    mimetype='text/plain'
                )
            except ValueError as e:
                logger.warning(f"cURL registration failed: {str(e)}")
                return app.response_class(
                    response=f"Error: {str(e)}",
                    status=400,
                    mimetype='text/plain'
                )
                
        except Exception as e:
            logger.error(f"Error in cURL registration endpoint: {str(e)}")
            return app.response_class(
                response=f"Error: Failed to process registration\n{str(e)}",
                status=500,
                mimetype='text/plain'
            )
    
    @app.route("/sms/curl/v1/start/<phone_number>", methods=["POST"])
    @app.route("/sms/curl/v1/register/<phone_number>", methods=["POST"])
    @limiter.limit("20 per hour")
    def curl_start(phone_number):
        """Opt-in an already registered user via plain text API."""
        logger = logging.getLogger(__name__)
        try:
            # Check if user exists
            user = db.get_user_by_phone(phone_number)
            if not user:
                return app.response_class(
                    response=f"Error: Phone number not registered\nPlease register first at www.hampuff.com/register",
                    status=404,
                    mimetype='text/plain'
                )
            
            # Opt them in
            success = db.update_opt_in_status(phone_number, True)
            if success:
                logger.info(f"cURL opt-in successful: {phone_number}")
                return app.response_class(
                    response=f"User opted in successfully\nPhone: {user.get('phone_normalized')}\nOpted in: True",
                    status=200,
                    mimetype='text/plain'
                )
            else:
                return app.response_class(
                    response="Error: Failed to update opt-in status",
                    status=500,
                    mimetype='text/plain'
                )
                
        except Exception as e:
            logger.error(f"Error in cURL opt-in endpoint: {str(e)}")
            return app.response_class(
                response=f"Error: Failed to process opt-in\n{str(e)}",
                status=500,
                mimetype='text/plain'
            )
    
    @app.route("/sms/curl/v1/stop/<phone_number>", methods=["POST"])
    @app.route("/sms/curl/v1/unregister/<phone_number>", methods=["POST"])
    @limiter.limit("20 per hour")
    def curl_stop(phone_number):
        """Opt-out a user via plain text API."""
        logger = logging.getLogger(__name__)
        try:
            # Try to opt them out (works even if not registered)
            success = db.update_opt_in_status(phone_number, False)
            if success:
                logger.info(f"cURL opt-out successful: {phone_number}")
                return app.response_class(
                    response="User opted out successfully\nOpted in: False",
                    status=200,
                    mimetype='text/plain'
                )
            else:
                # User not found, but we'll still confirm
                logger.info(f"cURL opt-out requested for unregistered number: {phone_number}")
                return app.response_class(
                    response="Phone number not currently registered. No action needed.",
                    status=200,
                    mimetype='text/plain'
                )
                
        except Exception as e:
            logger.error(f"Error in cURL opt-out endpoint: {str(e)}")
            return app.response_class(
                response=f"Error: Failed to process opt-out\n{str(e)}",
                status=500,
                mimetype='text/plain'
            )
    
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
