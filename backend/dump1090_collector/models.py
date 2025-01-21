from django.db import models

class Dump1090FlightData(models.Model):
    """
    Stores ADS-B flight information as broadcast by the aircraft 
    and received by Dump1090 .
    """
    hex_id = models.CharField(max_length=6, blank=True, null=True)
    squawk_code = models.IntegerField(blank=True, null=True)
    flight_callsign = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    valid_position = models.BooleanField(default=False)
    altitude = models.IntegerField(blank=True, null=True)
    vertical_rate = models.IntegerField(blank=True, null=True)
    track = models.IntegerField(blank=True, null=True)
    valid_track = models.BooleanField(default=False)
    speed_in_knots = models.IntegerField(default=0)
    messages_received = models.IntegerField(default=0)
    seen = models.IntegerField(default=0)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.flight_callsign or 'Unknown'} ({self.hex_id})"


class AdsbdbAircraftData(models.Model):
    """
    Stores additional details about an aircraft (https://www.adsbdb.com/).
    We make 'hex_id' the primary key, assuming each aircraft has a unique Mode S code.
    """
    aircraft_type = models.CharField(max_length=50, blank=True, null=True)
    icao_type = models.CharField(max_length=50, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    mode_s = models.CharField(max_length=10, blank=True, null=True)
    registration = models.CharField(max_length=20, blank=True, null=True)
    registered_owner_country_iso_name = models.CharField(max_length=10, blank=True, null=True)
    registered_owner_country_name = models.CharField(max_length=100, blank=True, null=True)
    registered_owner_operator_flag_code = models.CharField(max_length=20, blank=True, null=True)
    registered_owner = models.CharField(max_length=100, blank=True, null=True)
    url_photo = models.URLField(blank=True, null=True)
    url_photo_thumbnail = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Hex {self.hex_id} - {self.registration or 'Unknown'}"


class AdsbdbCallsignData(models.Model):
    """
    Stores callsign-related data for particular flights (https://www.adsbdb.com/).
    """
    callsign = models.CharField(max_length=20, blank=True, null=True)
    callsign_icao = models.CharField(max_length=20, blank=True, null=True)
    callsign_iata = models.CharField(max_length=20, blank=True, null=True)
    airline = models.CharField(max_length=100, blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    midpoint = models.CharField(max_length=100, blank=True, null=True)
    destination = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return (
            f"Callsign: {self.callsign or 'N/A'} "
            f"(Hex: {self.hex_id or 'Unknown'})"
        )
