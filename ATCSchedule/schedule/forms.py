from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TotalLoadOnSystemsInput, DailyMachineHoursInput, QualityReportInput
from .constants import Unit_choice, machines_choice, machine_name_choice
#widget
class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField(label = 'E-Mail')
#category  = forms.ChoiceField(choices=[('question','Answer'),('other','Other')])


# create a forms
class estimatedHoursForm(ModelForm):

    unit = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    tool_no = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    tool_name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    insert = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    num_of_inserts = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:120px'}))
    machine = forms.ChoiceField(choices = machine_name_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    estimated_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:150px'}))
    buffer_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    insertion_date = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    class Meta:
        model  =  TotalLoadOnSystemsInput
        fields = "__all__"
        #fields = ('tool_info','date')

# create a form for daily machine hours
class dailyMachineHoursForm(ModelForm):

    unit = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px','id':'department'}))
    tool_no = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    tool_name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    insert = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    machine = forms.ChoiceField(choices = machine_name_choice,widget=forms.Select(attrs={'style': 'width:100px','id':'machine'}))
    machine_name = forms.ChoiceField(choices = machines_choice,widget=forms.Select(attrs={'style': 'width:100px','id':'machine_id'}))
    num_of_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    daily_date = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    class Meta:
        model  =  DailyMachineHoursInput
        fields = "__all__"

# create a form for daily machine hours
class accuracyInputForm(ModelForm):

    unit = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    tool_no = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    tool_name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    insert = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    turning = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    milling = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    edm = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    wire_cut = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    num_of_rejects = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    insertion_date = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    class Meta:
        model  =  QualityReportInput
        fields = "__all__"

class CreateRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
