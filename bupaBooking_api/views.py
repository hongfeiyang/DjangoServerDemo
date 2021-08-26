from django.db.models import query
from django.shortcuts import render
from rest_framework import generics
from bupaBooking.models import Location, DateTimeSlot
from .serializers import LocationSerializer, DateTimeSerializer


class LocationList(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class DateTimeSlotList(generics.ListAPIView):
    queryset = DateTimeSlot.objects.all()
    serializer_class = DateTimeSerializer
