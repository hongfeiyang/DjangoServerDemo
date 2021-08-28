from django.urls import path
from .views import LocationList, SlotList
app_name = 'bupaBooking_api'

urlpatterns = [
    path('locations/', LocationList.as_view(), name='locationList'),
    path('slots/', SlotList.as_view(), name='dateTimeSlotList')
]
