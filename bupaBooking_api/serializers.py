from rest_framework import serializers
from bupaBooking.models import Location, Slot


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ('slot',)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('name', 'address', 'postcode', 'slots')

    slots = SlotSerializer(read_only=True, many=True)
