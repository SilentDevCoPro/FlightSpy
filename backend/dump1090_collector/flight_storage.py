from django.utils import timezone


def get_or_create_aircraft(aircraft_info, flight_hex):
    """
    Creates or retrieves the Aircraft by registration if possible,
    otherwise by hex_id.
    """

    from .models import Aircraft

    registration = (aircraft_info.get('registration') or '').strip()

    if registration:
        # Use registration as the unique key
        aircraft_obj, _ = Aircraft.objects.get_or_create(
            registration=registration,
            defaults={
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
        )
    else:
        # Fall back to hex_id if no registration is available
        aircraft_obj, _ = Aircraft.objects.get_or_create(
            hex_id=flight_hex,
            defaults={
                'registration': '',
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
        )

    return aircraft_obj


def get_or_create_airline(airline_info):
    """
    Creates or retrieves the Airline based on icao+iata.
    """

    from .models import Airline

    airline_name = airline_info.get('name', '')
    airline_icao = airline_info.get('icao', '')
    airline_iata = airline_info.get('iata', '')

    airline_obj, _ = Airline.objects.get_or_create(
        icao=airline_icao,
        iata=airline_iata,
        defaults={
            'name': airline_name,
            'country': airline_info.get('country', ''),
            'country_iso': airline_info.get('country_iso', ''),
            'callsign': airline_info.get('callsign', ''),
        }
    )
    return airline_obj


def get_or_create_airport(airport_info):
    from .models import Airport
    from django.db.models import Q

    iata = airport_info.get('iata_code', '') or ''
    icao = airport_info.get('icao_code', '') or ''

    # 1. Attempt to find an existing record matching either code
    airport_qs = Airport.objects.filter(Q(iata_code=iata) | Q(icao_code=icao))
    airport = airport_qs.first()
    if airport:
        return airport

    # 2. Create if none found
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

    # 1. Extract data from the JSON/dicts
    aircraft_info = adsbdb_aircraft_data.get('response', {}).get('aircraft', {})
    callsign_info = adsbdb_callsign_data.get('response') or {}
    flightroute_info = callsign_info.get('flightroute') or {}
    airline_info = flightroute_info.get('airline', {}) or {}
    origin_info = flightroute_info.get('origin', {}) or {}
    destination_info = flightroute_info.get('destination', {}) or {}

    # Dump1090 flight fields
    flight_hex = flight.get('hex', '').strip()
    squawk = flight.get('squawk', 0)
    flight_callsign = flight.get('flight', '')
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

    # 2. Create or get related objects
    aircraft_obj = get_or_create_aircraft(aircraft_info, flight_hex)
    airline_obj = get_or_create_airline(airline_info)
    origin_airport = get_or_create_airport(origin_info)
    destination_airport = get_or_create_airport(destination_info)

    # 3. Create the FlightData record
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
