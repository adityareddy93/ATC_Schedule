# Generated by Django 3.2.16 on 2023-01-01 01:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0010_qualityreportinput_insert'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DailyMachineHours',
        ),
        migrations.DeleteModel(
            name='EstimatedHours',
        ),
    ]
