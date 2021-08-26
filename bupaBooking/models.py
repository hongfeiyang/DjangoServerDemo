from django.db import models

# Create your models here.


class DateTimeSlot(models.Model):
    slot = models.DateTimeField(
        auto_now=False, auto_now_add=False)


class Location(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=4)
    slots = models.ManyToManyField(DateTimeSlot)

    class Meta:
        ordering = ['name', 'address', 'postcode']
        unique_together = ['name', 'address', 'postcode']
