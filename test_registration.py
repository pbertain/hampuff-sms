#!/usr/bin/env python3
"""
Test script for the registration system.
"""

from models import RegistrationDatabase


def test_phone_normalization():
    """Test phone number normalization."""
    db = RegistrationDatabase()
    
    test_numbers = [
        "+1-555-111-2222",
        "555 111-2222", 
        "(555) 111-2222",
        "5551112222",
        "555-111-2222",
        "+15551112222",
        "(555) 123-4567",  # Real test number
        "5551234567"       # Real test number
    ]
    
    print("Testing phone number normalization:")
    for number in test_numbers:
        try:
            normalized = db.normalize_phone_number(number)
            print(f"  {number:15} -> {normalized}")
        except ValueError as e:
            print(f"  {number:15} -> ERROR: {e}")
    
    print()


def test_registration():
    """Test user registration."""
    db = RegistrationDatabase()
    
    print("Testing user registration:")
    
    # Test valid registration
    try:
        result = db.register_user(
            full_name="John Doe",
            call_sign="W1ABC",
            phone_number="(555) 123-4567",
            opted_in=True
        )
        print(f"  Registration successful: {result}")
    except ValueError as e:
        print(f"  Registration failed: {e}")
    
    # Test duplicate phone number
    try:
        result = db.register_user(
            full_name="Jane Smith",
            call_sign="K2XYZ",
            phone_number="555-123-4567",  # Same number, different format
            opted_in=True
        )
        print(f"  Duplicate registration: {result}")
    except ValueError as e:
        print(f"  Duplicate registration correctly rejected: {e}")
    
    # Test opt-in check
    is_opted_in = db.is_user_opted_in("(555) 123-4567")
    print(f"  User opted-in status: {is_opted_in}")
    
    print()


def test_admin_functions():
    """Test admin functions."""
    db = RegistrationDatabase()
    
    print("Testing admin functions:")
    registrations = db.get_all_registrations()
    print(f"  Total registrations: {len(registrations)}")
    
    opted_in_users = db.get_opted_in_users()
    print(f"  Opted-in users: {len(opted_in_users)}")
    
    print()


if __name__ == "__main__":
    print("Hampuff SMS Registration System Test")
    print("=" * 40)
    
    test_phone_normalization()
    test_registration()
    test_admin_functions()
    
    print("Test completed!")
