from django.http import HttpResponse
from django.shortcuts import render
from .forms import ContactForm
from .models import EstimatedHours, TotalLoadOnSystemsInput
from .module_files.helper_functions import forcast_tool_output
from django.db import connection
import pandas as pd
import json
import datetime

# Create your views here.
def base(request):
    #return HttpResponse("ATC SCHEDULING")
    return render(request,'home1.html',{"bool_val":True,'developer':"DEVELOPED BY ARN TECH GROUP"})
def Home(request):
    #return HttpResponse("ATC SCHEDULING")
    return render(request,'test.html',{"bool_val":True,'developer':"DEVELOPED BY ARN TECH GROUP"})
def estimated_hours(request):
    return HttpResponse("PAGE IS UNDER CONSTRUCTION")

def contact(request):
    if request.method =='POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            print(name, email)
    return render(request,'form.html',{'form':form})

# def print_df(request):
#     if request.method =='POST':
#         cursor = connection.cursor()
#         start_dt = request.POST.get('start')
#         print(start_dt)
#         end_dt = request.POST.get('end')
        # df = pd.DataFrame(list(EstimatedHours.objects.all().values()))
        # df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
#         df['date']= pd.to_datetime(df['date'])
#         print(df.date)
#         df = df[(df['date']>=start_dt) & (df['date']<=end_dt)]
#         def convert_timestamp(item_date_object):
#             if isinstance(item_date_object, (datetime.date, datetime.datetime)):
#                 return item_date_object.strftime("%Y-%m-%d")
#         dict_ = df.reset_index().to_dict(orient ='records')
#         json_records = json.dumps(dict_, default=convert_timestamp)
#         data = []
#         data = json.loads(json_records)
#         context = {'d': data}
#         #schedule_estimatedhours
#         return render(request,'test_block.html',context)
#     else:
#         search = EstimatedHours.objects.all().values()
#         return render(request, 'test_block.html', {'d':search})

def print_df(request):
    if request.method =='POST':
        cursor = connection.cursor()
        start_dt = request.POST.get('start')
        print(start_dt)
        end_dt = request.POST.get('end')
        df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
        output = forcast_tool_output(df)
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
        output = forcast_tool_output(df)
        def convert_timestamp(item_date_object):
            if isinstance(item_date_object, (datetime.date, datetime.datetime)):
                return item_date_object.strftime("%Y-%m-%d")
        dict_ = output.reset_index().to_dict(orient ='records')
        json_records = json.dumps(dict_, default=convert_timestamp)
        data = []
        data = json.loads(json_records)
        print(data)
        context = {'d': data}
        return render(request, 'test_block.html', context)


"""
OLD LANGUAGE_CODE
"""
#df = pd.DataFrame(list(EstimatedHours.objects.all().values()))
#check = EstimatedHours.objects.all().values()
#print(check)
#def convert_timestamp(item_date_object):
#    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
#        return item_date_object.strftime("%Y-%m-%d")

#dict_ = df.reset_index().to_dict(orient ='records')#,date_format='iso',date_unit='s')
#json_records = json.dumps(dict_, default=convert_timestamp)

#data = []
#data = json.loads(json_records)
#context = {'d': data}

#return render(request, 'print.html', context)

#return HttpResponse(html_obj)


#query = """select * from schedule.EstimatedHours
#            where date between {} and {}""".format(start_dt,end_dt)
#search = EstimatedHours.objects.raw(query)
