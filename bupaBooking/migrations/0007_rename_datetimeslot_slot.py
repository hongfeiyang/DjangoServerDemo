# Generated by Django 3.2.6 on 2021-08-28 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bupaBooking', '0006_alter_location_slots'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DateTimeSlot',
            new_name='Slot',
        ),
    ]