from django.db import models
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
