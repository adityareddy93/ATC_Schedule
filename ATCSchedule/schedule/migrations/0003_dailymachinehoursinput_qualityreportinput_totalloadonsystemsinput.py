# Generated by Django 3.2.16 on 2022-11-29 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20221111_0719'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyMachineHoursInput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(blank=True, max_length=200, verbose_name='Department')),
                ('tool_no', models.CharField(blank=True, max_length=200, verbose_name='Tool Number')),
                ('tool_name', models.CharField(blank=True, max_length=200, verbose_name='Tool Name')),
                ('insert', models.CharField(blank=True, max_length=200, verbose_name='Insert')),
                ('machines', models.CharField(blank=True, max_length=200, verbose_name='Machines')),
                ('num_of_hours', models.IntegerField(blank=True, null=True, verbose_name='Number of Hours')),
                ('daily_date', models.DateField(blank=True, null=True, verbose_name='Daily Date')),
            ],
        ),
        migrations.CreateModel(
            name='QualityReportInput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(blank=True, max_length=200, verbose_name='Department')),
                ('tool_no', models.CharField(blank=True, max_length=200, verbose_name='Tool Number')),
                ('tool_name', models.CharField(blank=True, max_length=200, verbose_name='Tool Name')),
                ('machines', models.CharField(blank=True, max_length=200, verbose_name='Machines')),
                ('accuracy', models.CharField(blank=True, max_length=200, verbose_name='Accuracy')),
                ('num_of_rejects', models.IntegerField(blank=True, null=True, verbose_name='Number of Rejects')),
                ('estimated_cost', models.IntegerField(blank=True, null=True, verbose_name='Estimated Cost')),
                ('insertion_date', models.DateField(blank=True, null=True, verbose_name='Insertion Date')),
            ],
        ),
        migrations.CreateModel(
            name='TotalLoadOnSystemsInput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(blank=True, max_length=200, verbose_name='Department')),
                ('tool_no', models.CharField(blank=True, max_length=200, verbose_name='Tool Number')),
                ('tool_name', models.CharField(blank=True, max_length=200, verbose_name='Tool Name')),
                ('insert', models.CharField(blank=True, max_length=200, verbose_name='Insert')),
                ('num_of_inserts', models.IntegerField(blank=True, null=True, verbose_name='Number Of Inserts')),
                ('machines', models.CharField(blank=True, max_length=200, verbose_name='Machines')),
                ('estimated_hours', models.IntegerField(blank=True, null=True, verbose_name='Estimated Hours')),
                ('buffer_hours', models.IntegerField(blank=True, null=True, verbose_name='Buffer Hours')),
                ('insertion_date', models.DateField(blank=True, null=True, verbose_name='Insertion Date')),
            ],
        ),
    ]
