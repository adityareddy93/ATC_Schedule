from django.contrib import admin
from .models import TotalLoadOnSystemsInput
from .models import DailyMachineHoursInput
from .models import QualityReportInput
# Register your models here.

admin.site.register(TotalLoadOnSystemsInput)
admin.site.register(DailyMachineHoursInput)
admin.site.register(QualityReportInput)
