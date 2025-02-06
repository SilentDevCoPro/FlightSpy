import logging
from ..models import Aircraft, Airline, Airport

def get_or_create_aircraft(aircraft_info, flight_hex):
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
        qs = Aircraft.objects.filter(registration=registration)
        count = qs.count()
        if count > 1:
            logging.warning("Multiple Aircraft objects found for registration=%s. Using the first one.", registration)
            aircraft_obj = qs.first()
            for key, value in defaults.items():
                setattr(aircraft_obj, key, value)
            aircraft_obj.save()
            return aircraft_obj
        else:
            aircraft_obj, _ = Aircraft.objects.update_or_create(
                registration=registration,
                defaults=defaults
            )
            return aircraft_obj
    else:
        qs = Aircraft.objects.filter(hex_id=flight_hex)
        count = qs.count()
        if count > 1:
            logging.warning("Multiple Aircraft objects found for hex_id=%s. Using the first one.", flight_hex)
            aircraft_obj = qs.first()
            for key, value in defaults.items():
                setattr(aircraft_obj, key, value)
            aircraft_obj.registration = ''
            aircraft_obj.save()
            return aircraft_obj
        else:
            aircraft_obj, _ = Aircraft.objects.update_or_create(
                hex_id=flight_hex,
                defaults={**defaults, 'registration': ''}
            )
            return aircraft_obj

def get_or_create_airline(airline_info):
    airline_name = airline_info.get('name', '')
    airline_icao = airline_info.get('icao', '')
    airline_iata = airline_info.get('iata', '')
    qs = Airline.objects.filter(icao=airline_icao, iata=airline_iata)
    if qs.exists():
        if qs.count() > 1:
            logging.warning("Multiple Airline objects found for icao=%s, iata=%s. Using the first one.", airline_icao, airline_iata)
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
