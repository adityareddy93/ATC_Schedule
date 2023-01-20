from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import ContactForm, estimatedHoursForm, dailyMachineHoursForm, accuracyInputForm, CreateRegisterForm, UploadFile
from .models import  TotalLoadOnSystemsInput, DailyMachineHoursInput, QualityReportInput
from .module_files.helper_functions import daily_report_output, total_load_on_systems_output, accuarcy_quality_report, overall_efficiency_report, usage_efficiency_report
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .decorator_ import userauthentication,allowed_users
from django.db.models import Min
from django.db import connection
import pandas as pd
import json
import datetime

def handle_csv(file, html_page):
    df = pd.read_csv(file,delimiter=',')
    print(df.columns)

    if (html_page == 'form.html'):
        # print("total")
        df['Insertion date'] = pd.to_datetime(df['Insertion date'])
        df['Insertion date'] = df['Insertion date'].dt.strftime('%Y-%m-%d')
        csv_list = [list(row) for row in df.values]
        db = TotalLoadOnSystemsInput
        # columns = ['unit', 'tool_no','tool_name','insert','machine', 'estimated_hours', 'buffer_hours', 'insertion_date']
        for i in csv_list:
            db.objects.create(
                unit = i[0],
                tool_no = i[1],
                tool_name= i[2],
                insert= i[3],
                num_of_inserts= i[4],
                machine= i[5],
                estimated_hours= i[6],
                buffer_hours= i[7],
                insertion_date= i[8],
            )
    if (html_page == 'daily_report_input.html'):
        # print("daily")
        df['Daily date'] = pd.to_datetime(df['Daily date'])
        df['Daily date'] = df['Daily date'].dt.strftime('%Y-%m-%d')
        csv_list = [list(row) for row in df.values]
        db = DailyMachineHoursInput
        # columns = ['unit', 'tool_no','tool_name','insert','machine', 'machine_name', 'num_of_hours', 'daily_date']
        for i in csv_list:
            db.objects.create(
                unit = i[0],
                tool_no = i[1],
                tool_name= i[2],
                insert= i[3],
                machine= i[4],
                machine_name= i[5],
                num_of_hours= i[6],
                status= i[7],
                daily_date= i[8],
            )
    if (html_page == 'accuracy_input.html'):
        # print("quality")
        # print(df)
        df['Insertion date'] = pd.to_datetime(df['Insertion date'])
        df['Insertion date'] = df['Insertion date'].dt.strftime('%Y-%m-%d')
        # print(df)
        csv_list = [list(row) for row in df.values]
        db = QualityReportInput
        # columns = ['unit', 'tool_no','tool_name','insert','turning', 'milling', 'edm', 'wire_cut', 'insertion_date']
        for i in csv_list:
            # print("hello")
            # print(i)
            db.objects.create(
                unit = i[0],
                tool_no = i[1],
                tool_name= i[2],
                insert= i[3],
                turning= i[4],
                milling= i[5],
                edm= i[6],
                wire_cut= i[7],
                num_of_rejects= i[8],
                insertion_date= i[9],
            )



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

    if request.method == "POST":
        form = input_form(request.POST)
        form_file = UploadFile(request.POST)
        if request.method=='POST' and 'file' in request.POST:
            csv_file = request.FILES['file']
            handle_csv(csv_file, html)
            # *************&&&&&&&&&&&&&&&&&&&&&&&&*******************************************
            # min_ids = csv_upload_for_inputs(html)
            if (html == 'form.html'):
                min_id = TotalLoadOnSystemsInput.objects.values('unit', 'tool_no','tool_name','insert','machine').annotate(minid=Min('id'))
                min_ids = [obj['minid'] for obj in min_id]
                TotalLoadOnSystemsInput.objects.exclude(id__in=min_ids).delete()
            if (html == 'daily_report_input.html'):
                min_id = DailyMachineHoursInput.objects.values('unit', 'tool_no','tool_name','insert','machine', 'daily_date').annotate(minid=Min('id'))
                min_ids = [obj['minid'] for obj in min_id]
                DailyMachineHoursInput.objects.exclude(id__in=min_ids).delete()
            if (html == 'accuracy_input.html'):
                min_id = QualityReportInput.objects.values('unit', 'tool_no','tool_name','insert').annotate(minid=Min('id'))
                min_ids = [obj['minid'] for obj in min_id]
                QualityReportInput.objects.exclude(id__in=min_ids).delete()
            min_ids = [obj['minid'] for obj in min_id]
            # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            # print(csv_file)

            return HttpResponseRedirect(submit_req_str)
        else:
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(submit_req_str)
            else:
                form = input_form
                # print("second part")
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
                # print(val)
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
            # print(dict_)
        # print(dict_)
        json_records = json.dumps(dict_, default=convert_timestamp)
        data = []
        data = json.loads(json_records)
        context = {'d': data}
        # print(context)
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
    # df2 = pd.DataFrame(list(QualityReportInput.objects.all().values()))
    return output_req_func(request, df, 'usage_efficiency_report_output.html', df1)

def csv_upload(request):
    prompt = {order:"text"}
    if request.method== "GET":
        return render(request,'index.html',prompt)
    csv_file = request.FILES['file']

    if not csv_file.name.endswith('.csv'):
        messages.error(request,"This is not a csv file")
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringtIO(data_set)
    next(io_string)
    for column in csv.reader(io_string,delimiter=',',quotechar='|'):
        _, created = contact.objects.update_or_create()

    return True


def handler400(request,exception):
    return render(request,"handler400.html",status=400)


def handler403(request,exception):
    return render(request,"handler403.html",status=403)

def handler404(request,exception):
    print("went through")
    return render(request,"handler404.html",status=404)

def handler500(request):
    return render(request,"handler500.html",status=500)
