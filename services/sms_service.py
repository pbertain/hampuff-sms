#!/usr/bin/env python3
"""
SMS Service Module

Handles SMS request processing and response generation for the Hampuff service.
"""

import logging
import sys
import os
from flask import request, current_app
from twilio.twiml.messaging_response import MessagingResponse

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hampuff_lib.hampuff_lib import HampuffDataProvider
from models import RegistrationDatabase


class SMSHandler:
    """Handles SMS requests and generates appropriate responses."""
    
    def __init__(self):
        """Initialize the SMS handler."""
        self.logger = logging.getLogger(__name__)
        self.hampuff_provider = HampuffDataProvider()
        self.db = RegistrationDatabase()
    
    def handle_sms_request(self):
        """Process incoming SMS request and return TwiML response."""
        try:
            # Get SMS body and sender phone number from request
            full_body = request.values.get('Body', '')
            sender_phone = request.values.get('From', '')
            
            if not full_body:
                return self._create_response("No message body received")
            
            # Clean and process the message
            body = full_body.strip()
            body_lower = body.lower()
            self.logger.info(f"Received SMS from {sender_phone}: {body}")
            
            # Handle STOP/UNREGISTER commands before checking opt-in status
            # These commands should work even if user is not opted-in
            if body_lower in ['stop', 'unregister']:
                try:
                    success = self.db.update_opt_in_status(sender_phone, False)
                    if success:
                        self.logger.info(f"User {sender_phone} opted out via {body_lower}")
                        return self._create_response(
                            "You have been unregistered from SMS service. "
                            "You will no longer receive messages. Reply START to re-register."
                        )
                    else:
                        # User not found, but we'll still confirm opt-out
                        self.logger.info(f"Opt-out requested for unregistered number {sender_phone}")
                        return self._create_response(
                            "You are not currently registered. No action needed."
                        )
                except Exception as e:
                    self.logger.error(f"Database error during opt-out: {str(e)}")
                    return self._create_response(
                        "Service temporarily unavailable. Please try again later."
                    )
            
            # Handle START/REGISTER commands before checking opt-in status
            if body_lower in ['start', 'register']:
                try:
                    # Check if user is already registered
                    user = self.db.get_user_by_phone(sender_phone)
                    if user:
                        # User exists, just opt them in
                        success = self.db.update_opt_in_status(sender_phone, True)
                        if success:
                            self.logger.info(f"User {sender_phone} opted in via {body_lower}")
                            return self._create_response(
                                "You have been registered for SMS service. "
                                "Send a ham radio propagation query to get started!"
                            )
                    else:
                        # User not registered, need to register via web
                        return self._create_response(
                            "You need to complete registration first. "
                            "Please visit www.hampuff.com/register to register with your name and call sign."
                        )
                except Exception as e:
                    self.logger.error(f"Database error during opt-in: {str(e)}")
                    return self._create_response(
                        "Service temporarily unavailable. Please try again later."
                    )
            
            # Handle HELP command - available to everyone
            if body_lower in ['help', '?']:
                return self._create_response(self._get_help_message())
            
            # Check if sender is registered and opted-in for other commands
            try:
                if not self.db.is_user_opted_in(sender_phone):
                    return self._create_response(
                        "You are not registered for SMS service. Please visit www.hampuff.com/register to opt-in."
                    )
            except Exception as e:
                self.logger.error(f"Database error checking registration: {str(e)}")
                # Fail closed - don't send SMS if we can't verify registration
                return self._create_response(
                    "Service temporarily unavailable. Please try again later."
                )
            
            # Generate appropriate response
            response_text = self._generate_response(body, body_lower)
            
            # Create and return TwiML response
            return self._create_response(response_text)
            
        except Exception as e:
            self.logger.error(f"Error processing SMS request: {str(e)}")
            return self._create_response("Sorry, an error occurred processing your request.")
    
    def _generate_response(self, body, body_lower):
        """Generate response text based on message content."""
        
        # Check for profanity
        if 'fuck' in body_lower:
            return "Go fuck yourself, too"
        
        if 'shit' in body_lower:
            return "Go shit your pants"
        
        # Check for 4-character messages (airport codes)
        if len(body_lower) == 4:
            return current_app.config["AIRPUFF_MESSAGE"]
        
        # Check for propagation requests (prop/propagation with timezone)
        # Examples: "prop EST", "propagation PDT", "prop CST"
        propagation_match = self._parse_propagation_command(body_lower)
        if propagation_match:
            timezone_code = propagation_match
            try:
                hampuff_data = self.hampuff_provider.get_hampuff_data_for_timezone(timezone_code)
                return f"{hampuff_data}\n\n{current_app.config['CONSENT_MESSAGE']}"
            except Exception as e:
                self.logger.error(f"Error getting hampuff data: {str(e)}")
                return f"Sorry, unable to retrieve hampuff data for timezone {timezone_code}. Supported timezones: EST, EDT, CST, CDT, MST, MDT, PST, PDT, AKST, AKDT, HST, AST, ChST, GST, UTC, GMT."
        
        # Check for legacy hampuff requests (hampuffe, hampuffp)
        if 'hampuff' in body_lower:
            try:
                hampuff_data = self.hampuff_provider.get_hampuff_data(body)
                return f"{hampuff_data}\n\n{current_app.config['CONSENT_MESSAGE']}"
            except Exception as e:
                self.logger.error(f"Error getting hampuff data: {str(e)}")
                return "Sorry, unable to retrieve hampuff data at this time."
        
        # Default response for unrecognized messages
        return current_app.config["DEFAULT_WRONG_NUMBER_MESSAGE"]
    
    def _parse_propagation_command(self, body_lower):
        """
        Parse propagation command and return timezone code if valid.
        
        Supports formats like:
        - "prop EST"
        - "propagation PDT"
        - "prop CST"
        
        Returns:
            Timezone code (e.g., "EST", "PDT") if valid, None otherwise
        """
        # Remove extra whitespace and split
        parts = body_lower.split()
        
        if len(parts) < 2:
            return None
        
        # Check if first part is "prop" or "propagation"
        if parts[0] not in ['prop', 'propagation']:
            return None
        
        # Get timezone code
        tz_code = parts[1].upper()
        
        # Validate timezone code
        valid_timezones = [
            'EST', 'EDT', 'CST', 'CDT', 'MST', 'MDT', 'PST', 'PDT',  # US Continental
            'AKST', 'AKDT',  # Alaska
            'HST',  # Hawaii
            'AST',  # Puerto Rico
            'ChST', 'GST',  # Guam (Chamorro/Guam Standard Time)
            'UTC', 'GMT'  # UTC/GMT (Universal Time)
        ]
        if tz_code in valid_timezones:
            return tz_code
        
        return None
    
    def _get_help_message(self):
        """Generate help message with available commands and timezones."""
        help_text = (
            "HamPuff SMS Commands:\n\n"
            "PROPAGATION:\n"
            "• prop [TIMEZONE] - Get solar propagation data\n"
            "• propagation [TIMEZONE] - Same as above\n"
            "• hampuffe - Legacy (Eastern time)\n"
            "• hampuffp - Legacy (Pacific time)\n\n"
            "REGISTRATION:\n"
            "• START or REGISTER - Opt-in to SMS service\n"
            "• STOP or UNREGISTER - Opt-out from SMS service\n\n"
            "SUPPORTED TIMEZONES:\n"
            "US Continental: EST, EDT, CST, CDT, MST, MDT, PST, PDT\n"
            "Alaska: AKST, AKDT\n"
            "Hawaii: HST\n"
            "Puerto Rico: AST\n"
            "Guam: ChST, GST\n"
            "Universal: UTC, GMT\n\n"
            "EXAMPLES:\n"
            "• prop EST\n"
            "• propagation PDT\n"
            "• prop HST\n\n"
            "HELP:\n"
            "• HELP or ? - Show this message"
        )
        return help_text
    
    def get_propagation_data(self, timezone_code: str, include_consent: bool = False) -> str:
        """
        Get propagation data for a timezone (without TwiML wrapper).
        
        Args:
            timezone_code: Timezone code (e.g., 'EST', 'PDT', 'CST')
            include_consent: Whether to include consent message
            
        Returns:
            Propagation data as plain text string
            
        Raises:
            ValueError: If timezone code is invalid
        """
        try:
            hampuff_data = self.hampuff_provider.get_hampuff_data_for_timezone(timezone_code)
            if include_consent:
                return f"{hampuff_data}\n\n{current_app.config['CONSENT_MESSAGE']}"
            return hampuff_data
        except Exception as e:
            self.logger.error(f"Error getting hampuff data: {str(e)}")
            raise
    
    def get_propagation_data_json(self, timezone_code: str) -> dict:
        """
        Get propagation data for a timezone as structured JSON.
        
        Args:
            timezone_code: Timezone code (e.g., 'EST', 'PDT', 'CST')
            
        Returns:
            Dictionary with structured propagation data
            
        Raises:
            ValueError: If timezone code is invalid
        """
        try:
            # Get the timezone object
            timezone = self.hampuff_provider._get_timezone_from_code(timezone_code)
            
            # Fetch solar data
            solar_data = self.hampuff_provider._fetch_solar_data()
            
            # Parse update time
            update_time = self.hampuff_provider._parse_update_time(
                solar_data['updated'], 
                timezone
            )
            
            # Return structured JSON
            return {
                "timezone": timezone_code.upper(),
                "timezone_name": str(timezone).split('/')[-1] if '/' in str(timezone) else str(timezone),
                "updated": update_time,
                "data": {
                    "solar_flux": solar_data.get('solarflux', 'N/A'),
                    "a_index": solar_data.get('aindex', 'N/A'),
                    "k_index": solar_data.get('kindex', 'N/A'),
                    "sunspots": solar_data.get('sunspots', 'N/A'),
                    "muf": solar_data.get('muf', 'N/A'),
                    "xray": solar_data.get('xray', 'N/A'),
                    "solar_winds": solar_data.get('solarwind', 'N/A')
                },
                "raw_updated_utc": solar_data.get('updated', 'N/A')
            }
        except Exception as e:
            self.logger.error(f"Error getting hampuff data JSON: {str(e)}")
            raise
    
    def _create_response(self, message_text):
        """Create a TwiML response with the given message."""
        resp = MessagingResponse()
        resp.message(message_text)
        return str(resp)
