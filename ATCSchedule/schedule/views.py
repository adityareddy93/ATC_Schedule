from django.http import HttpResponse
from django.shortcuts import render
from .forms import ContactForm, estimatedHoursForm, dailyMachineHoursForm, accuracyInputForm
from .models import EstimatedHours, TotalLoadOnSystemsInput, DailyMachineHoursInput, QualityReportInput
from .module_files.helper_functions import forcast_tool_output, daily_report_output, total_load_on_systems_output, accuarcy_quality_report
from django.http import HttpResponseRedirect
from django.db import connection
import pandas as pd
import json
import datetime

# Create your views here.
def base(request):
    return render(request,'home1.html',{"bool_val":True,'developer':"DEVELOPED BY ARN TECH GROUP"})

# Input functions
def input_page_req_func(request, input_form, submit_req_str, df, html):
    submit = False
    form = input_form
    print("check1")
    if request.method == "POST":
        print("check 2")
        form = input_form(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(submit_req_str)
        else:
            form = input_form
            if 'submit' in request.GET:
                submit=True
    # df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
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
    return render(request,html ,{'d':data,'form':form,"Submit":submit})

# Input page creataion for estimated hours
def estimated_hours(request):
    df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    return input_page_req_func(request, estimatedHoursForm, '/estimated_hours?submit=True', df, 'form.html')

# Input page creataion for estimated hours
def daily_machine_hours(request):
    df = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))
    return input_page_req_func(request, dailyMachineHoursForm, '/daily_machine_hours?submit=True', df, 'daily_report_input.html')

# Input page creataion for quality report quality report and accuracy are same.
def accuracy(request):
    df = pd.DataFrame(list(QualityReportInput.objects.all().values()))
    return input_page_req_func(request, accuracyInputForm, '/accuracy?submit=True', df, 'accuracy_input.html')

# Output functions
def output_req_func(request, df, html, *args):
    if request.method =='POST':
        cursor = connection.cursor()
        start_dt = request.POST.get('start')
        print(start_dt)
        end_dt = request.POST.get('end')
        # df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
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
        return render(request, html,context)
    else:
         # search = TotalLoadOnSystemsInput.objects.all().values()
        # df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
        df1 = df
        for arguments in args:
            df1 = arguments
        # df1 = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))
        if (html == 'test_block.html'):
            output = total_load_on_systems_output(df)
        if (html == 'daily_report.html'):
            output = daily_report_output(df, df1)
        if (html == 'accuracy_input.html'):
            output = accuarcy_quality_report(df)

        print(output)
        def convert_timestamp(item_date_object):
            if isinstance(item_date_object, (datetime.date, datetime.datetime)):
                return item_date_object.strftime("%Y-%m-%d")
        dict_ = output.reset_index().to_dict(orient ='records')
        json_records = json.dumps(dict_, default=convert_timestamp)
        data = []
        data = json.loads(json_records)
        context = {'d': data}
        return render(request, html, context)

def total_load_on_sys_output(request):
    df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    return output_req_func(request, df, 'test_block.html')


def daily_report_hours_output(request):
    df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    df1 = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))
    return output_req_func(request, df, 'daily_report.html', df1)

def accuracy_output(request):
    df = pd.DataFrame(list(accuracyInputForm.objects.all().values()))
    return output_req_func(request, df, 'quality_report_output.html')
