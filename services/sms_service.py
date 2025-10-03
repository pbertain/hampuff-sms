#!/usr/bin/env python3
"""
SMS Service Module

Handles SMS request processing and response generation for the Hampuff service.
"""

import logging
from flask import request, current_app
from twilio.twiml.messaging_response import MessagingResponse
from lib.hampuff_lib import HampuffDataProvider
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
            self.logger.info(f"Received SMS from {sender_phone}: {body}")
            
            # Check if sender is registered and opted-in
            if not self.db.is_user_opted_in(sender_phone):
                return self._create_response(
                    "You are not registered for SMS service. Please visit our registration page to opt-in: "
                    f"{request.url_root}register"
                )
            
            # Generate appropriate response
            response_text = self._generate_response(body)
            
            # Create and return TwiML response
            return self._create_response(response_text)
            
        except Exception as e:
            self.logger.error(f"Error processing SMS request: {str(e)}")
            return self._create_response("Sorry, an error occurred processing your request.")
    
    def _generate_response(self, body):
        """Generate response text based on message content."""
        body_lower = body.lower()
        
        # Check for profanity
        if 'fuck' in body_lower:
            return "Go fuck yourself, too"
        
        if 'shit' in body_lower:
            return "Go shit your pants"
        
        # Check for 4-character messages (airport codes)
        if len(body_lower) == 4:
            return current_app.config["AIRPUFF_MESSAGE"]
        
        # Check for hampuff requests
        if 'hampuff' in body_lower:
            try:
                hampuff_data = self.hampuff_provider.get_hampuff_data(body)
                return f"{hampuff_data}\n\n{current_app.config['CONSENT_MESSAGE']}"
            except Exception as e:
                self.logger.error(f"Error getting hampuff data: {str(e)}")
                return "Sorry, unable to retrieve hampuff data at this time."
        
        # Default response for unrecognized messages
        return current_app.config["DEFAULT_WRONG_NUMBER_MESSAGE"]
    
    def _create_response(self, message_text):
        """Create a TwiML response with the given message."""
        resp = MessagingResponse()
        resp.message(message_text)
        return str(resp)
