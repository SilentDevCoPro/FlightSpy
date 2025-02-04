import logging
from django.utils import timezone

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
    if not isinstance(adsbdb_callsign_data, dict):
        logging.error("adsbdb_callsign_data is not a dict: %s", adsbdb_callsign_data)
        return {}
    callsign_response = adsbdb_callsign_data.get('response')
    if not isinstance(callsign_response, dict):
        if callsign_response in (None, "unknown callsign"):
            logging.debug("Received callsign response: %s", callsign_response)
            return {}
        else:
            logging.error("adsbdb_callsign_data['response'] is not a dict: %s", callsign_response)
            return {}
    return callsign_response

def extract_flight_data(flight):
    return {
        "flight_hex": flight.get('hex', '').strip(),
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
