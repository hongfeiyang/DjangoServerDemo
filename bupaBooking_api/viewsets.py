from django.db.models import query
from rest_framework import viewsets
from bupaBooking.models import Location, User
from .serializers import LocationSerializer, UserSerializer
# ViewSets define the view behavior.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
