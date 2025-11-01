#!/usr/bin/env python3
"""
Hampuff Library Module

Gathers band conditions and solar data to reply to SMS requests
with the latest ham radio conditions update.
"""

import datetime
import logging
import pytz
import requests
import xmltodict
from typing import Optional


class HampuffDataProvider:
    """Provides hampuff data by fetching and parsing solar data from hamqsl.com."""
    
    USER_AGENT = 'HamPuff/14.074/230926'
    BASE_URL = 'http://www.hamqsl.com/solarxml.php'
    
    # Timezone code mapping to pytz timezone objects
    TIMEZONE_MAP = {
        # US Continental timezones
        'EST': pytz.timezone('US/Eastern'),  # Eastern Standard Time
        'EDT': pytz.timezone('US/Eastern'),   # Eastern Daylight Time (same tz)
        'CST': pytz.timezone('US/Central'),  # Central Standard Time
        'CDT': pytz.timezone('US/Central'),  # Central Daylight Time (same tz)
        'MST': pytz.timezone('US/Mountain'),  # Mountain Standard Time
        'MDT': pytz.timezone('US/Mountain'), # Mountain Daylight Time (same tz)
        'PST': pytz.timezone('US/Pacific'),   # Pacific Standard Time
        'PDT': pytz.timezone('US/Pacific'),   # Pacific Daylight Time (same tz)
        # Alaska
        'AKST': pytz.timezone('US/Alaska'),  # Alaska Standard Time
        'AKDT': pytz.timezone('US/Alaska'),  # Alaska Daylight Time (same tz)
        # Hawaii
        'HST': pytz.timezone('US/Hawaii'),  # Hawaii Standard Time (no DST)
        # Puerto Rico
        'AST': pytz.timezone('America/Puerto_Rico'),  # Atlantic Standard Time (no DST)
        # Guam
        'ChST': pytz.timezone('Pacific/Guam'),  # Chamorro Standard Time (no DST)
        'GST': pytz.timezone('Pacific/Guam'),    # Guam Standard Time (alternative abbreviation)
        # UTC/GMT
        'UTC': pytz.UTC,  # Coordinated Universal Time
        'GMT': pytz.UTC,  # Greenwich Mean Time (same as UTC)
    }
    
    def __init__(self):
        """Initialize the hampuff data provider."""
        self.logger = logging.getLogger(__name__)
        self._solar_data = None
        self._last_update = None
    
    def get_hampuff_data(self, hampuff_args: str) -> str:
        """
        Get hampuff data for the given arguments (legacy format).
        
        Args:
            hampuff_args: String like 'hampuffe' or 'hampuffp' for timezone
            
        Returns:
            Formatted string with solar data
            
        Raises:
            ValueError: If arguments are invalid
        """
        try:
            # Validate input
            self._validate_hampuff_args(hampuff_args)
            
            # Get timezone
            timezone = self._get_timezone(hampuff_args)
            
            # Fetch and parse solar data
            solar_data = self._fetch_solar_data()
            
            # Format response
            return self._format_hampuff_response(solar_data, timezone)
            
        except Exception as e:
            self.logger.error(f"Error getting hampuff data: {str(e)}")
            raise
    
    def get_hampuff_data_for_timezone(self, timezone_code: str) -> str:
        """
        Get hampuff data for the given timezone code.
        
        Args:
            timezone_code: Timezone code like 'EST', 'PDT', 'CST', etc.
            
        Returns:
            Formatted string with solar data
            
        Raises:
            ValueError: If timezone code is invalid
        """
        try:
            # Validate and get timezone
            timezone = self._get_timezone_from_code(timezone_code)
            
            # Fetch and parse solar data
            solar_data = self._fetch_solar_data()
            
            # Format response
            return self._format_hampuff_response(solar_data, timezone)
            
        except Exception as e:
            self.logger.error(f"Error getting hampuff data: {str(e)}")
            raise
    
    def _get_timezone_from_code(self, timezone_code: str) -> pytz.timezone:
        """
        Get pytz timezone object from timezone code.
        
        Args:
            timezone_code: Timezone code (e.g., 'EST', 'PDT', 'CST', 'ChST')
            
        Returns:
            pytz timezone object
            
        Raises:
            ValueError: If timezone code is not supported
        """
        # Try exact match first (for codes like 'ChST' that have mixed case)
        if timezone_code in self.TIMEZONE_MAP:
            return self.TIMEZONE_MAP[timezone_code]
        
        # Try uppercase match for case-insensitive lookup
        code_upper = timezone_code.upper()
        # Create a case-insensitive lookup map
        upper_map = {k.upper(): v for k, v in self.TIMEZONE_MAP.items()}
        
        if code_upper in upper_map:
            return upper_map[code_upper]
        
        # Not found
        valid_codes = ', '.join(sorted(self.TIMEZONE_MAP.keys()))
        raise ValueError(
            f"Invalid timezone code '{timezone_code}'. "
            f"Supported codes: {valid_codes}"
        )
    
    def _validate_hampuff_args(self, hampuff_args: str) -> None:
        """Validate the hampuff arguments."""
        if not isinstance(hampuff_args, str):
            raise ValueError("Hampuff arguments must be a string")
        
        if len(hampuff_args) != 8:
            raise ValueError("Hampuff arguments must be exactly 8 characters")
        
        if not hampuff_args.lower().startswith('hampuff'):
            raise ValueError("Hampuff arguments must start with 'hampuff'")
    
    def _get_timezone(self, hampuff_args: str) -> pytz.timezone:
        """Get the timezone from hampuff arguments."""
        timezone_char = hampuff_args[7].lower()
        
        if timezone_char == 'e':
            return pytz.timezone('US/Eastern')
        elif timezone_char == 'p':
            return pytz.timezone('US/Pacific')
        else:
            raise ValueError(
                "Invalid timezone. Only 'e' (Eastern) and 'p' (Pacific) are supported"
            )
    
    def _fetch_solar_data(self) -> dict:
        """Fetch solar data from hamqsl.com."""
        try:
            headers = {'User-Agent': self.USER_AGENT}
            response = requests.get(self.BASE_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse XML response
            solar_data = xmltodict.parse(response.text)
            
            # Validate response structure
            if 'solar' not in solar_data or 'solardata' not in solar_data['solar']:
                raise ValueError("Invalid solar data response structure")
            
            return solar_data['solar']['solardata']
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching solar data: {str(e)}")
            raise ValueError(f"Failed to fetch solar data: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error parsing solar data: {str(e)}")
            raise ValueError(f"Failed to parse solar data: {str(e)}")
    
    def _format_hampuff_response(self, solar_data: dict, timezone: pytz.timezone) -> str:
        """Format the hampuff response with solar data."""
        try:
            # Parse update time
            update_time = self._parse_update_time(solar_data['updated'], timezone)
            
            # Get timezone name for display (use the zone name)
            tz_name = str(timezone).split('/')[-1] if '/' in str(timezone) else str(timezone)
            
            # Format the response
            response = (
                f"[Hampuff - {tz_name}] Updated: {update_time}\n"
                f"\tSolar Flux  = {solar_data.get('solarflux', 'N/A')}\n"
                f"\tA Index     = {solar_data.get('aindex', 'N/A')}\n"
                f"\tK Index     = {solar_data.get('kindex', 'N/A')}\n"
                f"\tSunspot #   = {solar_data.get('sunspots', 'N/A')}\n"
                f"\tMUF         = {solar_data.get('muf', 'N/A')}\n"
                f"\tXRay        = {solar_data.get('xray', 'N/A')}\n"
                f"\tSolar Winds = {solar_data.get('solarwind', 'N/A')}"
            )
            
            return response
            
        except KeyError as e:
            self.logger.error(f"Missing solar data field: {str(e)}")
            raise ValueError(f"Solar data is incomplete: missing {str(e)}")
    
    def _parse_update_time(self, update_str: str, timezone: pytz.timezone) -> str:
        """Parse and format the update time in the specified timezone."""
        try:
            # Parse the time format from hamqsl
            time_format = '%d %b %Y %H%M %Z'
            utc_time = datetime.datetime.strptime(update_str, time_format).replace(
                tzinfo=datetime.timezone.utc
            )
            
            # Convert to specified timezone
            local_time = utc_time.astimezone(timezone)
            
            # Format output
            output_format = '%a %d %b %H:%M'
            return local_time.strftime(output_format)
            
        except ValueError as e:
            self.logger.error(f"Error parsing update time: {str(e)}")
            raise ValueError(f"Invalid update time format: {str(e)}")


# Legacy function for backward compatibility
def hampuff_data(hampuff_args: str) -> str:
    """
    Legacy function for backward compatibility.
    
    Args:
        hampuff_args: String like 'hampuffe' or 'hampuffp'
        
    Returns:
        Formatted string with solar data
    """
    provider = HampuffDataProvider()
    return provider.get_hampuff_data(hampuff_args)