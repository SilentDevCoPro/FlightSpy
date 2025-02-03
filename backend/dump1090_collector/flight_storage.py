from django.utils import timezone
import logging
from django.utils import timezone
from .models import FlightData

def get_or_create_aircraft(aircraft_info, flight_hex):
    """
    Retrieves and updates (or creates) the Aircraft record based on
    registration if possible, otherwise by hex_id.
    """
    from .models import Aircraft

    registration = (aircraft_info.get('registration') or '').strip()

    defaults = {
        'hex_id': flight_hex,
        'aircraft_type': aircraft_info.get('type', ''),
        'icao_type': aircraft_info.get('icao_type', ''),
        'manufacturer': aircraft_info.get('manufacturer', ''),
        'mode_s': aircraft_info.get('mode_s', ''),
        'registered_owner_country_iso_name': aircraft_info.get('registered_owner_country_iso_name', ''),
        'registered_owner_country_name': aircraft_info.get('registered_owner_country_name', ''),
        'registered_owner_operator_flag_code': aircraft_info.get('registered_owner_operator_flag_code', ''),
        'registered_owner': aircraft_info.get('registered_owner', ''),
        'url_photo': aircraft_info.get('url_photo', ''),
        'url_photo_thumbnail': aircraft_info.get('url_photo_thumbnail', ''),
    }

    if registration:
        aircraft_obj, _ = Aircraft.objects.update_or_create(
            registration=registration,
            defaults=defaults
        )
    else:
        aircraft_obj, _ = Aircraft.objects.update_or_create(
            hex_id=flight_hex,
            defaults={**defaults, 'registration': ''}
        )

    return aircraft_obj


def get_or_create_airline(airline_info):
    """
    Creates or retrieves the Airline based on icao + iata.
    If multiple Airline objects exist for the same icao and iata, a warning is logged
    and the first one is returned.
    """
    from .models import Airline

    airline_name = airline_info.get('name', '')
    airline_icao = airline_info.get('icao', '')
    airline_iata = airline_info.get('iata', '')

    qs = Airline.objects.filter(icao=airline_icao, iata=airline_iata)
    if qs.exists():
        if qs.count() > 1:
            logging.warning(
                "Multiple Airline objects found for icao=%s, iata=%s. Using the first one.",
                airline_icao,
                airline_iata
            )
        return qs.first()
    else:
        airline_obj = Airline.objects.create(
            icao=airline_icao,
            iata=airline_iata,
            name=airline_name,
            country=airline_info.get('country', ''),
            country_iso=airline_info.get('country_iso', ''),
            callsign=airline_info.get('callsign', '').strip(),
        )
        return airline_obj


def get_or_create_airport(airport_info):
    from .models import Airport
    from django.db.models import Q

    iata = airport_info.get('iata_code', '') or ''
    icao = airport_info.get('icao_code', '') or ''

    airport_qs = Airport.objects.filter(Q(iata_code=iata) | Q(icao_code=icao))
    airport = airport_qs.first()
    if airport:
        return airport

    return Airport.objects.create(
        iata_code=iata,
        icao_code=icao,
        name=airport_info.get('name', ''),
        country_iso_name=airport_info.get('country_iso_name', ''),
        country_name=airport_info.get('country_name', ''),
        elevation=airport_info.get('elevation', 0),
        latitude=airport_info.get('latitude', 0),
        longitude=airport_info.get('longitude', 0),
        municipality=airport_info.get('municipality', ''),
    )

def extract_aircraft_info(adsbdb_aircraft_data):
    """
    Returns a dictionary with the aircraft details extracted from the ADSBDB aircraft data.
    If the data is missing or invalid, returns an empty dict.
    """
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
    """
    Returns a dictionary with the callsign details extracted from the ADSBDB callsign data.
    If the data is missing or invalid, returns an empty dict.
    """
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

# Helper to extract flight data from the flight dict.
def extract_flight_data(flight):
    """
    Extracts the flight-related fields from the flight dictionary.
    """
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

def store_data(flight, adsbdb_aircraft_data, adsbdb_callsign_data):
    """
    Combines flight information with ADSBDB responses, creates or updates related models,
    and finally creates a FlightData record.
    """
    aircraft_info = extract_aircraft_info(adsbdb_aircraft_data)
    callsign_info = extract_callsign_info(adsbdb_callsign_data)

    flightroute_info = callsign_info.get('flightroute') or {}
    airline_info = flightroute_info.get('airline', {}) or {}
    origin_info = flightroute_info.get('origin', {}) or {}
    destination_info = flightroute_info.get('destination', {}) or {}

    flight_fields = extract_flight_data(flight)

    aircraft_obj = get_or_create_aircraft(aircraft_info, flight_fields["flight_hex"])
    airline_obj = get_or_create_airline(airline_info)
    origin_airport = get_or_create_airport(origin_info)
    destination_airport = get_or_create_airport(destination_info)

    flight_data = FlightData.objects.create(
        squawk_code=flight_fields["squawk"],
        flight_callsign=flight_fields["flight_callsign"],
        latitude=flight_fields["lat"],
        longitude=flight_fields["lon"],
        valid_position=flight_fields["valid_position"],
        altitude=flight_fields["altitude"],
        vertical_rate=flight_fields["vertical_rate"],
        track=flight_fields["track"],
        valid_track=flight_fields["valid_track"],
        speed_in_knots=flight_fields["speed_in_knots"],
        messages_received=flight_fields["messages_received"],
        seen=flight_fields["seen"],
        timestamp=flight_fields["timestamp"],
        aircraft=aircraft_obj,
        airline=airline_obj,
        origin_airport=origin_airport,
        destination_airport=destination_airport,
    )

    return flight_data



