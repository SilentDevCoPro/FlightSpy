from ..models import FlightData
from .services import get_or_create_aircraft, get_or_create_airline, get_or_create_airport
from .extractors import extract_aircraft_info, extract_callsign_info, extract_flight_data
import logging


def store_data(flight, adsbdb_aircraft_data, adsbdb_callsign_data):
    # Extract and validate all info with proper type checking
    aircraft_info = extract_aircraft_info(adsbdb_aircraft_data)
    if not isinstance(aircraft_info, dict):
        logging.error("Aircraft info is not a dictionary: %s", aircraft_info)
        return None

    callsign_info = extract_callsign_info(adsbdb_callsign_data)
    if not isinstance(callsign_info, dict):
        logging.error("Callsign info is not a dictionary: %s", callsign_info)
        return None

    # Safely get nested dictionary values with fallbacks
    flightroute_info = callsign_info.get('flightroute', {})
    if not isinstance(flightroute_info, dict):
        flightroute_info = {}

    airline_info = flightroute_info.get('airline', {})
    if not isinstance(airline_info, dict):
        airline_info = {}

    origin_info = flightroute_info.get('origin', {})
    if not isinstance(origin_info, dict):
        origin_info = {}

    destination_info = flightroute_info.get('destination', {})
    if not isinstance(destination_info, dict):
        destination_info = {}

    flight_fields = extract_flight_data(flight)

    # If flight data validation failed, skip storing
    if flight_fields is None:
        return None

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
