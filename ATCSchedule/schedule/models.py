from django.db import models

# Create your models here.



# Creating input table for the total load on systems
class TotalLoadOnSystemsInput(models.Model):
    unit = models.CharField('unit',max_length = 200,blank=True)
    tool_no = models.CharField('Tool Number',max_length = 200,blank=True)
    tool_name = models.CharField('Tool Name',max_length = 200,blank=True)
    insert = models.CharField('Insert',max_length = 200,blank=True)
    num_of_inserts = models.IntegerField('Number Of Inserts',blank=True,null=True)
    machine = models.CharField('Machine', max_length = 200,blank=True)
    estimated_hours = models.IntegerField('Estimated Hours',blank=True,null=True)
    buffer_hours = models.IntegerField('Buffer Hours',blank=True,null=True)
    insertion_date = models.DateField('Insertion Date',blank=True,null=True)
    #venue = models.ForeignKey(venue, blank = True, null=True, on_delete = models.CASCADE)

    class Meta():
        db_table = "TotalLoadOnSystemsInput"

    def __str__(self):
        return str(self.insertion_date)+' '+ self.tool_name + ' '+ self.machine

# Creating input table for the daily machine hours
class DailyMachineHoursInput(models.Model):
    unit = models.CharField('unit',max_length = 200,blank=True)
    tool_no = models.CharField('Tool Number',max_length = 200,blank=True)
    tool_name = models.CharField('Tool Name',max_length = 200,blank=True)
    insert = models.CharField('Insert',max_length = 200,blank=True)
    machine = models.CharField('Machine', max_length = 200,blank=True)
    machine_name = models.CharField('Machine Name', max_length = 200,blank=True)
    num_of_hours = models.IntegerField('Number of Hours',blank=True,null=True)
    status = models.CharField('Status', max_length = 200,blank=True)
    daily_date = models.DateField('Daily Date',blank=True,null=True)
    class Meta():
        db_table = "DailyMachineHoursInput"

    def __str__(self):
        return str(self.daily_date)+' '+ self.tool_name + ' '+self.machine

# Creating input table for the quality report
class QualityReportInput(models.Model):
    unit = models.CharField('unit',max_length = 200,blank=True)
    tool_no = models.CharField('Tool Number',max_length = 200,blank=True)
    tool_name = models.CharField('Tool Name',max_length = 200,blank=True)
    insert = models.CharField('Insert',max_length = 200,blank=True)
    machine = models.CharField('Machine', max_length = 200,blank=True)
    # turning = models.CharField('Turning', max_length = 200,blank=True)
    # milling = models.CharField('Milling', max_length = 200,blank=True)
    # edm = models.CharField('EDM', max_length = 200,blank=True)
    # wire_cut = models.CharField('Wire Cut', max_length = 200,blank=True)
    deviation = models.IntegerField('Deviation',blank=True,null=True)
    num_of_rejects = models.IntegerField('Number of Rejects',blank=True,null=True)
    insertion_date = models.DateField('Insertion Date',blank=True,null=True)

    class Meta():
        db_table = "QualityReportInput"

    def __str__(self):
        return str(self.insertion_date)+' '+ self.tool_name
