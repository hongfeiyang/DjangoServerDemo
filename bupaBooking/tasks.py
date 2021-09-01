from typing import Union
from demoServer.celery import app
from .booking import BupaBookingChecker, BupaBookingType, BupaLocation, BupaMedicalItem
from celery.utils.log import get_task_logger
from .models import Location, Slot
import datetime
from django.utils.timezone import make_aware

logger = get_task_logger(__name__)


@app.task(name='checkTimeSlotsForOne', ignore_result=True)
def checkTimeSlotsForOne(location: Union[Location, str]):
    taskSucceded = True
    print(f'{location} started')
    # celery needs result and args to be serializable, so we have to do a little hack here to serialize location to json and re-parse it
    if type(location) is str:
        _location = BupaLocation()
        _location.fromJson(location)
        location = _location
    locationObj, created = Location.objects.get_or_create(
        name=location.name, address=location.address, postcode=location.postcode)

    locationObj.slots.clear()
    checker = BupaBookingChecker(bookingType=BupaBookingType.INDIVIDUAL, medicalItems=[
        BupaMedicalItem.MedicalExamination, BupaMedicalItem.ChestXRay, BupaMedicalItem.HIVTest])

    try:
        times = checker.discoverTimesForLocation(location)
        for key, val in times.items():
            for time in val:
                _datetime = datetime.datetime.strptime(
                    f'{key} {time}', '%d/%m/%Y %I:%M %p')
                slot, created = Slot.objects.get_or_create(
                    slot=make_aware(_datetime)
                )
                locationObj.slots.add(slot)
    except:
        taskSucceded = False
    finally:
        checker.tearDown()

    print(f'{location} finished, succeed: {taskSucceded}')
    return taskSucceded


@app.task(name='discoverLocations')
def discoverLocations():
    print(f'discover locations started')
    checker = BupaBookingChecker(bookingType=BupaBookingType.INDIVIDUAL, medicalItems=[
                                 BupaMedicalItem.MedicalExamination, BupaMedicalItem.ChestXRay, BupaMedicalItem.HIVTest])

    locations = checker.discoverLocations(serialized=True)
    checker.tearDown()
    print(f'discover locations finished, found {len(locations)} locations')
    # map to tuples in the form of [(<json1>, ), (<json2>, )] becuase string is also iterable so it mess up with argument passing in celery chunks
    _tuples = list(map(lambda x: (x, ), locations))
    return _tuples


@app.task(name='checkTimeSlotsForAll', ignore_result=True)
def checkTimeSlotsForAll():
    # max concurrency is 4
    locations = discoverLocations()
    checkTimeSlotsForOne.chunks(locations, len(locations)).apply_async()
    return
