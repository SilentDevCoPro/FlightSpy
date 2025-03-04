import logging
from django.utils import timezone
from datetime import timedelta
from ..models import FlightData


def extract_aircraft_info(adsbdb_aircraft_data):
    if not isinstance(adsbdb_aircraft_data, dict):
        logging.error("adsbdb_aircraft_data is not a dict: %s", adsbdb_aircraft_data)
        return {}
    aircraft_response = adsbdb_aircraft_data.get('response')
    if not isinstance(aircraft_response, dict):
        if aircraft_response in (None, "unknown aircraft"):
            logging.debug("Received aircraft response: %s", aircraft_response)
            return {}
        else:
            logging.error("adsbdb_aircraft_data['response'] is not a dict: %s", aircraft_response)
            return {}
    return aircraft_response.get('aircraft', {})


def extract_callsign_info(adsbdb_callsign_data):
    """Extract callsign information, ensuring a dictionary is always returned."""
    if not isinstance(adsbdb_callsign_data, dict):
        logging.error("adsbdb_callsign_data is not a dict: %s", adsbdb_callsign_data)
        return {}
    
    response = adsbdb_callsign_data.get('response')
    if not isinstance(response, dict):
        if response is not None:
            logging.debug("Received non-dict callsign response: %s", response)
        return {}
        
    return response


def should_process_flight_data(flight, flight_hex):
    """
    Validate if the flight data should be processed based on position validity
    and duplicate detection.
    """
    # Check for valid position data
    lat = flight.get('lat', 0.0)
    lon = flight.get('lon', 0.0)
    valid_position = bool(flight.get('validposition', 0))
    
    if not valid_position or lat == 0.0 or lon == 0.0:
        logging.debug("Skipping flight %s: Invalid position data", flight_hex)
        return False

    # Check for recent duplicates
    recent_duplicate = FlightData.objects.filter(
        aircraft__hex_id=flight_hex,
        latitude=lat,
        longitude=lon,
        timestamp__gte=timezone.now() - timedelta(seconds=5)
    ).exists()

    if recent_duplicate:
        logging.debug("Skipping flight %s: Recent duplicate position", flight_hex)
        return False

    return True


def extract_flight_data(flight):
    flight_hex = flight.get('hex', '').strip()
    
    # Validate the flight data before processing
    if not should_process_flight_data(flight, flight_hex):
        return None

    return {
        "flight_hex": flight_hex,
        "squawk": flight.get('squawk', 0),
        "flight_callsign": flight.get('flight', '').strip(),
        "lat": flight.get('lat', 0.0),
        "lon": flight.get('lon', 0.0),
        "valid_position": bool(flight.get('validposition', 0)),
        "altitude": flight.get('altitude', 0),
        "vertical_rate": flight.get('vert_rate', 0),
        "track": flight.get('track', 0),
        "valid_track": bool(flight.get('validtrack', 0)),
        "speed_in_knots": flight.get('speed', 0),
        "messages_received": flight.get('messages', 0),
        "seen": flight.get('seen', 0),
        "timestamp": timezone.now(),
    }
