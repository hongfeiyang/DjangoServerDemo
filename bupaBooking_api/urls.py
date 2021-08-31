from django.urls import path
from .views import LocationList, LocationSlotList, MedicalItemList, SlotList, UserList, IndexView
app_name = 'bupaBooking_api'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('locations/', LocationList.as_view(), name='locationList'),
    path('slots/', SlotList.as_view(), name='slotList'),
    path('users/', UserList.as_view(), name='userList'),
    path('medicalItems/', MedicalItemList.as_view(), name='medicalItemList'),
    path('locationSlots/', LocationSlotList.as_view(), name='locationSlotList')

]
