# Generated by Django 3.2.6 on 2021-08-29 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bupaBooking', '0007_rename_datetimeslot_slot'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('email', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('slots', models.ManyToManyField(related_name='users', to='bupaBooking.Slot')),
            ],
            options={
                'ordering': ['name', 'email'],
            },
        ),
    ]