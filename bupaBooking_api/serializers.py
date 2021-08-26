from rest_framework import serializers
from bupaBooking.models import Location, DateTimeSlot


class DateTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DateTimeSlot
        fields = ('slot',)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('name', 'address', 'postcode', 'slots')

    slots = DateTimeSerializer(read_only=True, many=True)
