from django.utils import timezone
import logging


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

    # Try to filter existing Airline objects matching the provided icao and iata.
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
        # No matching record exists, so create a new one.
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


def store_data(flight, adsbdb_aircraft_data, adsbdb_callsign_data):
    """
    Called from poll_dump1090, which passes:
      - flight: dict from dump1090 (keys like 'hex', 'flight', 'lat', etc.)
      - adsbdb_aircraft_data: data from fetch_adsbdbAircraftData(hex)
      - adsbdb_callsign_data: data from fetch_adsbdbCallsignData(flight_code)

    1. Extract the relevant parts.
    2. Create or get the related models (Aircraft, Airline, Airport).
    3. Create the FlightData entry with foreign keys.
    """
    from .models import FlightData
    
    logging.debug("adsbdb_aircraft_data (type: %s): %s", type(adsbdb_aircraft_data), adsbdb_aircraft_data)

    if not isinstance(adsbdb_aircraft_data, dict) or 'response' not in adsbdb_aircraft_data:
        logging.error("adsbdb_aircraft_data is not a valid dict with 'response': %s", adsbdb_aircraft_data)
        aircraft_info = {}
    else:
        aircraft_info = adsbdb_aircraft_data.get('response', {}).get('aircraft', {})

    callsign_info = adsbdb_callsign_data.get('response') or {}
    flightroute_info = callsign_info.get('flightroute') or {}
    airline_info = flightroute_info.get('airline', {}) or {}
    origin_info = flightroute_info.get('origin', {}) or {}
    destination_info = flightroute_info.get('destination', {}) or {}
    flight_hex = flight.get('hex', '').strip()
    squawk = flight.get('squawk', 0)
    flight_callsign = flight.get('flight', '').strip()
    lat = flight.get('lat', 0.0)
    lon = flight.get('lon', 0.0)
    valid_position = bool(flight.get('validposition', 0))
    altitude = flight.get('altitude', 0)
    vertical_rate = flight.get('vert_rate', 0)
    track = flight.get('track', 0)
    valid_track = bool(flight.get('validtrack', 0))
    speed_in_knots = flight.get('speed', 0)
    messages_received = flight.get('messages', 0)
    seen = flight.get('seen', 0)
    timestamp = timezone.now()

    aircraft_obj = get_or_create_aircraft(aircraft_info, flight_hex)
    airline_obj = get_or_create_airline(airline_info)
    origin_airport = get_or_create_airport(origin_info)
    destination_airport = get_or_create_airport(destination_info)
    
    flight_data = FlightData.objects.create(
        squawk_code=squawk,
        flight_callsign=flight_callsign,
        latitude=lat,
        longitude=lon,
        valid_position=valid_position,
        altitude=altitude,
        vertical_rate=vertical_rate,
        track=track,
        valid_track=valid_track,
        speed_in_knots=speed_in_knots,
        messages_received=messages_received,
        seen=seen,
        timestamp=timestamp,
        aircraft=aircraft_obj,
        airline=airline_obj,
        origin_airport=origin_airport,
        destination_airport=destination_airport,
    )

    return flight_data