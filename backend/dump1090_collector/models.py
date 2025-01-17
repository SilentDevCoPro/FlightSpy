from django.db import models

class FlightData(models.Model):
    hex_id = models.CharField(max_length=6, blank=True)
    squawk_code = models.IntegerField(blank=True)
    flight_callsign = models.CharField(max_length=20, blank=True)
    latitude = models.FloatField(default=0.000000)
    longitude = models.FloatField(default=0.000000)
    valid_position = models.BinaryField()
    altitude = models.IntegerField(blank=True)
    vertical_rate = models.IntegerField(blank=True)
    track = models.IntegerField(blank=True)
    valid_track = models.BinaryField()
    speed_in_knots = models.IntegerField(default=0)
    messages_received = models.IntegerField(default=0)
    seen = models.IntegerField(default=0)

    def __str__(self):
        return f"Flight {self.hex_id} at {self.altitude} ft"