from django.urls import path
from .views import LocationList, DateTimeSlotList
app_name = 'bupaBooking_api'

urlpatterns = [
    path('locations/', LocationList.as_view(), name='locationList'),
    path('slots/', DateTimeSlotList.as_view(), name='dateTimeSlotList')
]
