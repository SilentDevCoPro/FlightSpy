from rest_framework import serializers
from .models import FlightData, Aircraft, Airline, Airport


class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = '__all__'


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = '__all__'


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'


class FlightDataSerializer(serializers.ModelSerializer):
    aircraft = AircraftSerializer(read_only=True)
    airline = AirlineSerializer(read_only=True)
    origin_airport = AirportSerializer(read_only=True)
    destination_airport = AirportSerializer(read_only=True)

    class Meta:
        model = FlightData
        fields = '__all__'
