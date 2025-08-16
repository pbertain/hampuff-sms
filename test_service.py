#!/usr/bin/env python3
"""
Test script for the Hampuff SMS Web Service.

This script tests the service locally without requiring Twilio.
"""

import requests
import json
from app import create_app


def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    
    with create_app().test_client() as client:
        response = client.get('/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        print()


def test_sms_endpoint():
    """Test the SMS endpoint with various inputs."""
    print("Testing SMS endpoint...")
    
    test_cases = [
        ("hampuffe", "Hampuff request for Eastern timezone"),
        ("hampuffp", "Hampuff request for Pacific timezone"),
        ("KJFK", "4-character airport code"),
        ("hello", "Generic message"),
        ("fuck", "Profanity test"),
        ("shit", "Profanity test"),
    ]
    
    with create_app().test_client() as client:
        for message, description in test_cases:
            print(f"Testing: {description} - '{message}'")
            
            # Simulate Twilio POST request
            response = client.post('/sms', data={'Body': message})
            print(f"Status: {response.status_code}")
            print(f"Response: {response.data.decode('utf-8')[:100]}...")
            print()


if __name__ == "__main__":
    print("Hampuff SMS Service Test")
    print("=" * 40)
    print()
    
    test_health_endpoint()
    test_sms_endpoint()
    
    print("Test completed!")
