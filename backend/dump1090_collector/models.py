from django.db import models


class FlightData(models.Model):
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
    timestamp = models.DateTimeField(null=True, blank=True)

    aircraft = models.ForeignKey(
        'Aircraft',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='flights'
    )
    airline = models.ForeignKey(
        'Airline',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='flights'
    )
    origin_airport = models.ForeignKey(
        'Airport',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='origin_flights'
    )
    destination_airport = models.ForeignKey(
        'Airport',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='destination_flights'
    )

    def __str__(self):
        return f"{self.flight_callsign or 'Unknown'} ({self.aircraft.hex_id if self.aircraft else 'No AC'})"


class Aircraft(models.Model):
    hex_id = models.CharField(max_length=6, unique=False)
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
        return f"{self.registration or 'Unknown'} ({self.hex_id})"


class Airline(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    icao = models.CharField(max_length=10, blank=True, null=True)
    iata = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_iso = models.CharField(max_length=10, blank=True, null=True)
    callsign = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name or "Unknown Airline"


class Airport(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    country_iso_name = models.CharField(max_length=10, blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True)
    elevation = models.IntegerField(blank=True, null=True)
    iata_code = models.CharField(max_length=5, blank=True, null=True)
    icao_code = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    municipality = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name or 'Unknown'} ({self.iata_code or self.icao_code or 'NoCode'})"
