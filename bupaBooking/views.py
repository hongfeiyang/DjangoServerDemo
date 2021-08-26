from django.http.response import HttpResponse
from django.shortcuts import render

from .models import Location
# Create your views here.


def indexView(request):
    results = Location.objects.get(postcode="5000").slots
    a = results.values()
    return HttpResponse(a)
