# Generated by Django 3.2.16 on 2023-01-11 04:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0012_alter_totalloadonsystemsinput_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='totalloadonsystemsinput',
            unique_together=set(),
        ),
    ]
