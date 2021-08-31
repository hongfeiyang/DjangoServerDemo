from rest_framework import serializers
from bupaBooking.models import Location, LocationSlot, MedicalItem, Slot, User


class MedicalItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalItem
        fields = ('code', )


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ('slot',)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('name', 'address', 'postcode', 'slots')

    slots = SlotSerializer(read_only=True, many=True)


class LocationSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationSlot
        fields = ('location', 'slot')

    location = LocationSerializer(read_only=True, many=True)
    slot = SlotSerializer(read_only=True, many=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'locationSlots', 'medicalItems')

    locationSlots = LocationSlotSerializer(read_only=True, many=True)
    medicalItems = MedicalItemSerializer(read_only=True, many=True)
