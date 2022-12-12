from django.db import models

# Create your models here.

class EstimatedHours(models.Model):
    tool_info = models.CharField('Tool Info',max_length = 200,blank=True,null=True)
    insert = models.CharField('Insert', max_length = 200,blank=True,null=True)
    machine = models.CharField('Machines', max_length = 200,blank=True,null=True)
    estimated_hours = models.IntegerField('Estimated Hours',blank=True,null=True)
    date = models.DateField('Insertion Date',blank=True,null=True)
    #venue = models.ForeignKey(venue, blank = True, null=True, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.date)+' '+ self.tool_info + ' '+self.machine
class DailyMachineHours(models.Model):
    tool_info = models.CharField('Tool Info',max_length = 200,blank=True)
    insert = models.CharField('Insert', max_length = 200,blank=True)
    machine = models.CharField('Machines', max_length = 200,blank=True)
    daily_hours = models.IntegerField('Actual Machine Hours',blank=True,null=True)
    date = models.DateField('Insertion Date',blank=True,null=True)
    #venue = models.ForeignKey(venue, blank = True, null=True, on_delete = models.CASCADE)
    comments = models.TextField('Comments', blank=True,null=True,help_text='text')
    class Meta():
        db_table = "Daily_Machine_Hours"

    def __str__(self):
        return str(self.date)+' '+ self.tool_info + ' '+self.machine

# Creating input table for the total load on systems
class TotalLoadOnSystemsInput(models.Model):
    department = models.CharField('Department',max_length = 200,blank=True)
    tool_no = models.CharField('Tool Number',max_length = 200,blank=True)
    tool_name = models.CharField('Tool Name',max_length = 200,blank=True)
    insert = models.CharField('Insert',max_length = 200,blank=True)
    num_of_inserts = models.IntegerField('Number Of Inserts',blank=True,null=True)
    machines = models.CharField('Machines', max_length = 200,blank=True)
    estimated_hours = models.IntegerField('Estimated Hours',blank=True,null=True)
    buffer_hours = models.IntegerField('Buffer Hours',blank=True,null=True)
    insertion_date = models.DateField('Insertion Date',blank=True,null=True)
    #venue = models.ForeignKey(venue, blank = True, null=True, on_delete = models.CASCADE)

    class Meta():
        db_table = "TotalLoadOnSystemsInput"

    def __str__(self):
        return str(self.insertion_date)+' '+ self.tool_name + ' '+ self.machines

# Creating input table for the daily machine hours
class DailyMachineHoursInput(models.Model):
    department = models.CharField('Department',max_length = 200,blank=True)
    tool_no = models.CharField('Tool Number',max_length = 200,blank=True)
    tool_name = models.CharField('Tool Name',max_length = 200,blank=True)
    insert = models.CharField('Insert',max_length = 200,blank=True)
    machines = models.CharField('Machines', max_length = 200,blank=True)
    machine_insert_name = models.CharField('Machine Insert Name', max_length = 200,blank=True)
    num_of_hours = models.IntegerField('Number of Hours',blank=True,null=True)
    daily_date = models.DateField('Daily Date',blank=True,null=True)

    class Meta():
        db_table = "DailyMachineHoursInput"

    def __str__(self):
        return str(self.daily_date)+' '+ self.tool_name + ' '+self.machines

# Creating input table for the quality report
class QualityReportInput(models.Model):
    department = models.CharField('Department',max_length = 200,blank=True)
    tool_no = models.CharField('Tool Number',max_length = 200,blank=True)
    tool_name = models.CharField('Tool Name',max_length = 200,blank=True)
    machines = models.CharField('Machines', max_length = 200,blank=True)
    accuracy = models.CharField('Accuracy',max_length = 200,blank=True)
    num_of_rejects = models.IntegerField('Number of Rejects',blank=True,null=True)
    estimated_cost = models.IntegerField('Estimated Cost',blank=True,null=True)
    insertion_date = models.DateField('Insertion Date',blank=True,null=True)

    class Meta():
        db_table = "QualityReportInput"

    def __str__(self):
        return str(self.insertion_date)+' '+ self.tool_name + ' '+self.machines
