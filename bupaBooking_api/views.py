from django.db.models import query
from django.shortcuts import render
from rest_framework import generics
from django.views import generic
from bupaBooking.models import Location, LocationSlot, MedicalItem, Slot, User
from .serializers import LocationSerializer, MedicalItemSerializer, SlotSerializer, UserSerializer


class LocationList(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class SlotList(generics.ListCreateAPIView):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer


class LocationSlotList(generics.ListCreateAPIView):
    queryset = LocationSlot.objects.all()
    serializer_class = LocationSerializer


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class MedicalItemList(generics.ListCreateAPIView):
    queryset = MedicalItem.objects.all()
    serializer_class = MedicalItemSerializer


class IndexView(generic.RedirectView):
    pattern_name = 'bupaBooking_api:locationList'
