from django.http import HttpResponse
from django.shortcuts import render
from .forms import ContactForm, estimatedHoursForm
from .models import EstimatedHours, TotalLoadOnSystemsInput, DailyMachineHoursInput
from .module_files.helper_functions import forcast_tool_output, daily_report_output, total_load_on_systems_output
from django.http import HttpResponseRedirect
from django.db import connection
import pandas as pd
import json
import datetime

# Create your views here.
def base(request):
    return render(request,'home1.html',{"bool_val":True,'developer':"DEVELOPED BY ARN TECH GROUP"})
def estimated_hours(request):
    submit = False
    form = estimatedHoursForm()
    print("check1")
    if request.method == "POST":
        print("check 2")
        form = estimatedHoursForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/estimated_hours?submit=True')
        else:
            form = estimatedHoursForm()
            if 'submit' in request.GET:
                submit=True
    df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    print(df)
    df = df.loc[::-1]
    def convert_timestamp(item_date_object):
        if isinstance(item_date_object, (datetime.date, datetime.datetime)):
            return item_date_object.strftime("%Y-%m-%d")
    dict_ = df.reset_index().to_dict(orient ='records')
    json_records = json.dumps(dict_,default=convert_timestamp)
    data = []
    data = json.loads(json_records)
    print(data)
    return render(request,'form.html',{'d':data,'form':form,"Submit":submit})


def print_df(request):
     if request.method =='POST':
         cursor = connection.cursor()
         start_dt = request.POST.get('start')
         print(start_dt)
         end_dt = request.POST.get('end')
         df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
         output = total_load_on_systems_output(df)
         output = output[(output['insertion_date']>=start_dt) & (output['insertion_date']<=end_dt)]
         def convert_timestamp(item_date_object):
             if isinstance(item_date_object, (datetime.date, datetime.datetime)):
                 return item_date_object.strftime("%Y-%m-%d")
         dict_ = output.reset_index().to_dict(orient ='records')
         json_records = json.dumps(dict_, default=convert_timestamp)
         data = []
         data = json.loads(json_records)
         context = {'d': data}
         #schedule_estimatedhours
         return render(request,'test_block.html',context)
     else:
         # search = TotalLoadOnSystemsInput.objects.all().values()
         df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
         output = total_load_on_systems_output(df)
         print(output)
         def convert_timestamp(item_date_object):
             if isinstance(item_date_object, (datetime.date, datetime.datetime)):
                 return item_date_object.strftime("%Y-%m-%d")
         dict_ = output.reset_index().to_dict(orient ='records')
         json_records = json.dumps(dict_, default=convert_timestamp)
         data = []
         data = json.loads(json_records)
         print("else condition")
         context = {'d': data}
         return render(request, 'test_block.html', context)
r"""
def print_df(request):
    if request.method =='POST':
        cursor = connection.cursor()
        start_dt = request.POST.get('start')
        print(start_dt)
        end_dt = request.POST.get('end')
        daily_hours_input_df = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))
        output = daily_report_output(daily_hours_input_df)
        output = output[(output['daily_date']>=start_dt) & (output['daily_date']<=end_dt)]
        def convert_timestamp(item_date_object):
            if isinstance(item_date_object, (datetime.date, datetime.datetime)):
                return item_date_object.strftime("%Y-%m-%d")
        dict_ = output.reset_index().to_dict(orient ='records')
        json_records = json.dumps(dict_, default=convert_timestamp)
        data = []
        data = json.loads(json_records)
        context = {'d': data}
        #schedule_estimatedhours
        return render(request,'daily_report.html',context)
    else:
        # search = TotalLoadOnSystemsInput.objects.all().values()
        daily_hours_input_df = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))
        total_load_input_df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
        output = daily_report_output(total_load_input_df, daily_hours_input_df)
        def convert_timestamp(item_date_object):
            if isinstance(item_date_object, (datetime.date, datetime.datetime)):
                return item_date_object.strftime("%Y-%m-%d")
        dict_ = output.reset_index().to_dict(orient ='records')
        json_records = json.dumps(dict_, default=convert_timestamp)
        data = []
        data = json.loads(json_records)
        print(data)
        context = {'d': data}
        return render(request, 'daily_report.html', context)
r"""
