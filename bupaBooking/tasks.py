from demoServer.celery import app
from .booking import BupaBookingChecker, BupaBookingType, BupaBookingConfig, BupaEncoder, BupaLocation
from celery.utils.log import get_task_logger
import json
from .models import Location, DateTimeSlot
import datetime
from django.utils.timezone import make_aware

logger = get_task_logger(__name__)


@app.task(name='check_all_timeslots')
def check_all_timeslots():
    logger.info("Starting task: check_all_timeslots")

    config = BupaBookingConfig(BupaBookingType.INDIVIDUAL,
                               '5000', 'Adelaide', ['501', '502', '707'])
    checker = BupaBookingChecker(config)
    locations = checker.discoverLocations()
    checker.tearDown()

    resultDict = {}

    for location in locations:
        locationObj, created = Location.objects.get_or_create(
            name=location.name, address=location.address, postcode=location.postcode)

        locationObj.slots.clear()

        print(f'{location} started')
        checker = BupaBookingChecker(config)
        times = checker.discoverTimesForLocation(location)
        checker.tearDown()
        for key, val in times.items():
            for time in val:
                _datetime = datetime.datetime.strptime(
                    f'{key} {time}', '%d/%m/%Y %I:%M %p')
                slot, created = DateTimeSlot.objects.get_or_create(
                    slot=make_aware(_datetime)
                )
                locationObj.slots.add(slot)

        print(f'{location} finished')
        resultDict[location.__str__()] = times
    jsonString = json.dumps(resultDict, cls=BupaEncoder,
                            sort_keys=True)
    logger.info("Finished task: check_all_timeslots")
    return jsonString
