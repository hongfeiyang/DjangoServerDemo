from django.db.models import query
from django.shortcuts import render
from rest_framework import generics
from bupaBooking.models import Location, Slot
from .serializers import LocationSerializer, SlotSerializer


class LocationList(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class SlotList(generics.ListAPIView):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
