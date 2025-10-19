"""
Geocoding utilities for converting addresses to latitude/longitude coordinates.
Supports multiple geocoding providers with fallback support.
"""
import requests
import time
from typing import Optional, Tuple
from django.conf import settings


class GeocodingService:
    """
    A robust geocoding service that uses API-based geocoding providers.
    Supports Nominatim (OpenStreetMap), OpenCage, and Positionstack.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MovieStore/1.0 (Django Application)'
        })
        
    def geocode_nominatim(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode using OpenStreetMap's Nominatim API (free, no API key required).
        Rate limit: 1 request per second.
        
        Args:
            address: Full address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        try:
            # Respect Nominatim's rate limit
            time.sleep(1)
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
            
            return None
            
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Nominatim geocoding error: {e}")
            return None
    
    def geocode_opencage(self, address: str, api_key: str) -> Optional[Tuple[float, float]]:
        """
        Geocode using OpenCage API (requires API key).
        Free tier: 2,500 requests/day.
        
        Args:
            address: Full address string to geocode
            api_key: OpenCage API key
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        url = "https://api.opencagedata.com/geocode/v1/json"
        params = {
            'q': address,
            'key': api_key,
            'limit': 1,
            'no_annotations': 1
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                geometry = data['results'][0]['geometry']
                lat = float(geometry['lat'])
                lon = float(geometry['lng'])
                return (lat, lon)
            
            return None
            
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"OpenCage geocoding error: {e}")
            return None
    
    def geocode_positionstack(self, address: str, api_key: str) -> Optional[Tuple[float, float]]:
        """
        Geocode using Positionstack API (requires API key).
        Free tier: 25,000 requests/month.
        
        Args:
            address: Full address string to geocode
            api_key: Positionstack API key
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        url = "http://api.positionstack.com/v1/forward"
        params = {
            'access_key': api_key,
            'query': address,
            'limit': 1
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                result = data['data'][0]
                lat = float(result['latitude'])
                lon = float(result['longitude'])
                return (lat, lon)
            
            return None
            
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Positionstack geocoding error: {e}")
            return None
    
    def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Main geocoding method that tries multiple providers based on settings.
        
        Args:
            address: Full address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if all providers fail
        """
        # Try OpenCage if API key is available
        opencage_key = getattr(settings, 'OPENCAGE_API_KEY', None)
        if opencage_key:
            result = self.geocode_opencage(address, opencage_key)
            if result:
                return result
        
        # Try Positionstack if API key is available
        positionstack_key = getattr(settings, 'POSITIONSTACK_API_KEY', None)
        if positionstack_key:
            result = self.geocode_positionstack(address, positionstack_key)
            if result:
                return result
        
        # Fall back to Nominatim (free, no API key required)
        return self.geocode_nominatim(address)


# Create a singleton instance
_geocoding_service = None

def get_geocoding_service() -> GeocodingService:
    """Get or create the geocoding service singleton."""
    global _geocoding_service
    if _geocoding_service is None:
        _geocoding_service = GeocodingService()
    return _geocoding_service


def geocode_address(city: str, state: Optional[str] = None, 
                   country: Optional[str] = None) -> Optional[Tuple[float, float]]:
    """
    Convenience function to geocode an address.
    
    Args:
        city: City name
        state: State/province name (optional)
        country: Country name (optional)
        
    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    if not city:
        return None
    
    # Build full address
    address_parts = [city]
    if state:
        address_parts.append(state)
    if country:
        address_parts.append(country)
    
    full_address = ", ".join(address_parts)
    
    # Get geocoding service and geocode
    service = get_geocoding_service()
    return service.geocode(full_address)

