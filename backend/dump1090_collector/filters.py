import django_filters
from django.db.models.functions import Trim
from .models import FlightData


class FlightDataFilter(django_filters.FilterSet):
    flight_callsign = django_filters.CharFilter(method='filter_callsign')

    aircraft__hex_id = django_filters.CharFilter(
        field_name='aircraft__hex_id',
        lookup_expr='iexact'
    )

    class Meta:
        model = FlightData
        fields = ['flight_callsign', 'aircraft__hex_id', 'timestamp']

    def filter_callsign(self, queryset, name, value):
        value = value.strip()
        return queryset.annotate(
            trimmed_callsign=Trim('flight_callsign')
        ).filter(trimmed_callsign__iexact=value)
