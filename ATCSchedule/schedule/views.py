from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import ContactForm, estimatedHoursForm, dailyMachineHoursForm, accuracyInputForm, CreateRegisterForm
from .models import  TotalLoadOnSystemsInput, DailyMachineHoursInput, QualityReportInput
from .module_files.helper_functions import daily_report_output, total_load_on_systems_output, accuarcy_quality_report, overall_efficiency_report, usage_efficiency_report
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .decorator_ import userauthentication,allowed_users
from django.db import connection
import pandas as pd
import json
import datetime

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registerPage(request):
    form = CreateRegisterForm()
    if request.method == 'POST':
        form = CreateRegisterForm(request.POST)
        if form.is_valid():
            # print(form)
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request,"Account was created for {}".format(user))
            return redirect('/login')
    context={'form':form}
    return render(request,'register.html',context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def loginPage(request):
    if request.method=='POST':
        u_name = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=u_name, password = password)

        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            messages.info(request,"Username or Password is incorrect")

    context={}
    return render(request,'login.html',context)


@login_required#(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutpage(request):
    if request.method == "POST":
        logout(request)
    return redirect('/login')


@login_required(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# Create your views here.
def base(request):
    return render(request,'home1.html',{"bool_val":True,'developer':"DEVELOPED BY ARN TECH GROUP"})

# Input functions
def input_page_req_func(request, input_form, submit_req_str, df, html):
    submit = False
    form = input_form
    # print("check1")
    if request.method == "POST":
        # print("check 2")
        form = input_form(request.POST)
        #print(form.errors)
        # print("-----------------------------------------------------------")
        print(form)
        # print("-----------------------------------------------------------")
        if form.is_valid():
            # print("----------------------------------------------------------------")
            # print("success")
            # print("----------------------------------------------------------------")
            form.save()
            return HttpResponseRedirect(submit_req_str)
        else:
            form = input_form
            print("second part")
            if 'submit' in request.GET:
                submit=True
    # df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    df = df.loc[::-1]
    def convert_timestamp(item_date_object):
        if isinstance(item_date_object, (datetime.date, datetime.datetime)):
            return item_date_object.strftime("%Y-%m-%d")
    dict_ = df.reset_index().to_dict(orient ='records')
    json_records = json.dumps(dict_,default=convert_timestamp)
    data = []
    data = json.loads(json_records)
    return render(request,html ,{'d':data,'form':form,"Submit":submit})

@login_required(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# Input page creataion for estimated hours

def estimated_hours(request):
    df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    return input_page_req_func(request, estimatedHoursForm, '/estimated_hours?submit=True', df, 'form.html')


@login_required(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# Input page creataion for estimated hours
def daily_machine_hours(request):
    df = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))
    return input_page_req_func(request, dailyMachineHoursForm, '/daily_machine_hours?submit=True', df, 'daily_report_input.html')


@login_required(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
        output = output[(output['actual_start_date']>=start_dt) & (output['actual_start_date']<=end_dt)]
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
        # Extracting values from *args
        if args:
            if len(args) == 1:
                df1 = args[0]
            elif len(args) == 2:
                df1 = args[0]
                df2 = args[1]

        # df1 = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))

        # To convert pivoted tuple to dictionary
        def convert_tuple_dict_to_dict(output):
            lst = []
            for val in output:
                new_dict = {}
                for key, value in val.items():
                    new_dict[key[0] + '_' + key[1]] = value
                if 'index_' in new_dict:
                    new_dict.pop('index_')
                else:
                    continue
                lst.append(new_dict)
            return lst

        # need to add try catch exception
        #
        if (html == 'test_block.html'):
            output = total_load_on_systems_output(df)
        if (html == 'usage_efficiency_report_output.html'):
            output = usage_efficiency_report(df, df1)
        if (html == 'quality_report_output.html'):
            output = accuarcy_quality_report(df)
        if (html == 'overall_efficiency_output.html'):
            output = overall_efficiency_report(df, df1, df2)
        if (html == 'daily_report.html'):
            output = daily_report_output(df, df1)

        def convert_timestamp(item_date_object):
            if isinstance(item_date_object, (datetime.date, datetime.datetime)):
                return item_date_object.strftime("%Y-%m-%d")

        dict_ = output.reset_index().to_dict(orient ='records')
        if ((html == 'daily_report.html') | (html == 'usage_efficiency_report_output.html') | (html == 'overall_efficiency_output.html')):
            dict_ = convert_tuple_dict_to_dict(dict_)

        json_records = json.dumps(dict_, default=convert_timestamp)
        data = []
        data = json.loads(json_records)
        context = {'d': data}
        return render(request, html, context)

@login_required(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@allowed_users(allowed_roles=['admin'])
def total_load_on_sys_output(request):
    df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    return output_req_func(request, df, 'test_block.html')


@login_required(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@allowed_users(allowed_roles=['admin'])
def daily_report_hours_output(request):
    df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    df1 = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))
    return output_req_func(request, df, 'daily_report.html', df1)


@login_required(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@allowed_users(allowed_roles=['admin'])
def accuracy_output(request):
    # print(QualityReportInput.objects.all())
    df = pd.DataFrame(list(QualityReportInput.objects.all().values()))
    return output_req_func(request, df, 'quality_report_output.html')


@login_required(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@allowed_users(allowed_roles=['admin'])
def overall_effiency_output(request):
    df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    df1 = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))
    df2 = pd.DataFrame(list(QualityReportInput.objects.all().values()))
    return output_req_func(request, df, 'overall_efficiency_output.html', df1, df2)


@login_required(login_url='Login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@allowed_users(allowed_roles=['admin'])
def usage_efficiency_output(request):
    df = pd.DataFrame(list(TotalLoadOnSystemsInput.objects.all().values()))
    df1 = pd.DataFrame(list(DailyMachineHoursInput.objects.all().values()))
    return output_req_func(request, df, 'usage_efficiency_report_output.html', df1)
