from django.urls import path
from . import views

app_name = 'bupaBooking'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('locations/', views.LocationsView.as_view(), name='locations'),
    path('location/<int:pk>', views.LocationDetailView.as_view(),
         name='locationDetails'),
    path('slots/', views.SlotsView.as_view(), name='slots'),
    path('slot/<int:pk>', views.SlotDetailView.as_view(), name='slotDetails'),
]
