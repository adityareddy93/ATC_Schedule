# Generated by Django 3.2.16 on 2023-01-11 04:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0011_auto_20221231_1811'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='totalloadonsystemsinput',
            unique_together={('unit', 'tool_no', 'tool_name')},
        ),
    ]
