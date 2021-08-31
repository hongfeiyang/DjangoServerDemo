from django.db import models
from django.db.models.fields import related
from django.db.models.functions import Coalesce


# Create your models here.


class Slot(models.Model):
    slot = models.DateTimeField(
        auto_now=False, auto_now_add=False)


class Location(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=4)
    slots = models.ManyToManyField(Slot, related_name='locations')

    def __str__(self) -> str:
        return f'{self.name},\n{self.address},\n{self.postcode}'

    class Meta:
        ordering = ['name', 'address', 'postcode']
        unique_together = ['name', 'address', 'postcode']


class LocationSlot(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='locationSlots')
    slot = models.ForeignKey(
        Slot, on_delete=models.CASCADE, related_name='locationSlots')

    class Meta:
        ordering = ['location', 'slot']

    def __str__(self) -> str:
        return f'{self.location.__str__()},\n{self.slot.__str__()}'


class MedicalItem(models.Model):

    MEDICAL_ITEM_CHOICES = [
        (501, '501 Medical Examination'),
        (502, '502 Chest X-Ray'),
        (704, '704 Serum Creatinine'),
        (707, '707 HIV test'),
        (708, '708 Hepatitis B test'),
    ]
    code = models.IntegerField(choices=MEDICAL_ITEM_CHOICES, primary_key=True)


class User(models.Model):
    email = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    locationSlots = models.ManyToManyField(LocationSlot, related_name='users')
    medicalItems = models.ManyToManyField(MedicalItem, related_name='users')

    class Meta:
        ordering = ['name', 'email']
