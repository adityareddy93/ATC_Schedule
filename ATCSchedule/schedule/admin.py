from django.contrib import admin
from .models import EstimatedHours
from .models import DailyMachineHours
from .models import TotalLoadOnSystemsInput
from .models import DailyMachineHoursInput
from .models import QualityReportInput
# Register your models here.


admin.site.register(EstimatedHours)
admin.site.register(DailyMachineHours)

admin.site.register(TotalLoadOnSystemsInput)
admin.site.register(DailyMachineHoursInput)
admin.site.register(QualityReportInput)
