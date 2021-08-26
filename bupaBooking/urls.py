from django.urls import path
from . import views

app_name = 'bupaBooking'
urlpatterns = [
    path('', views.indexView, name='index'),
]
