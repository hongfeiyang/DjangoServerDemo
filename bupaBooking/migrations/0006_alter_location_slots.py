# Generated by Django 3.2.6 on 2021-08-28 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bupaBooking', '0005_auto_20210825_0327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='slots',
            field=models.ManyToManyField(related_name='locations', to='bupaBooking.DateTimeSlot'),
        ),
    ]