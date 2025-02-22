# Generated by Django 3.2.16 on 2023-01-11 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0015_alter_totalloadonsystemsinput_unique_together'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='totalloadonsystemsinput',
            constraint=models.UniqueConstraint(fields=('unit', 'tool_no', 'tool_name', 'insert', 'machine'), name='unique'),
        ),
    ]
