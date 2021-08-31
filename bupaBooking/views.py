from bupaBooking.booking import BupaBookingChecker, BupaBookingType, BupaMedicalItem
from django.http.response import HttpResponse
from django.views import generic
from .tasks import checkTimeSlotsForAll

from .models import Location, Slot
# Create your views here.


class LocationDetailView(generic.DetailView):
    model = Location
    context_object_name = 'location'
    template_name = 'bupaBooking/locationDetails.html'


class LocationsView(generic.ListView):
    template_name = 'bupaBooking/locations.html'
    context_object_name = 'locations'
    queryset = Location.objects.all()

    def get_context_data(self, **kwargs):
        context = super(LocationsView, self).get_context_data(**kwargs)
        # context['test'] = 'a'
        return context


class SlotDetailView(generic.DetailView):
    model = Slot
    context_object_name = 'slot'
    template_name = 'bupaBooking/slotDetails.html'


class SlotsView(generic.ListView):
    template_name = 'bupaBooking/slots.html'
    context_object_name = 'slots'
    queryset = Slot.objects.all()
    ordering = 'slot'


class IndexView(generic.RedirectView):
    pattern_name = 'bupaBooking:locations'


def testView(request):

    return HttpResponse()
