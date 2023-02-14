import pandas as pd

from schedule.models import EstimatedHours

df = pd.DataFrame(list(EstimatedHours.objects.all().values()))

print(df)
