from django import forms
from django.forms import ModelForm
from .models import TotalLoadOnSystemsInput, DailyMachineHoursInput
from .constants import Unit_choice, machines_choice, turning_choice, milling_choice, edm_choice, wire_cut_choice, machine_name_choice
#widget
class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField(label = 'E-Mail')
#category  = forms.ChoiceField(choices=[('question','Answer'),('other','Other')])


def get_my_choices(value):
    # you place some logic here
    if value == "turning":
        return turning_choice
    if value == "turning":
        return milling_choice
    if value == "turning":
        return edm_choice
    if value == "turning":
        return wire_cut_choice


# create a forms
class estimatedHoursForm(ModelForm):

    unit = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    tool_no = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    tool_name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    insert = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    num_of_inserts = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:120px'}))
    machines = forms.ChoiceField(choices = machines_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    estimated_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:150px'}))
    buffer_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    insertion_date = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    class Meta:
        model  =  TotalLoadOnSystemsInput
        fields = "__all__"
        #fields = ('tool_info','date')

# create a form for daily machine hours
class dailyMachineHoursForm(ModelForm):

    unit = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    tool_no = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    tool_name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    insert = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    machine = forms.ChoiceField(choices = machines_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    machine_name = forms.ChoiceField(choices = machines_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    no_of_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    daily_date = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    class Meta:
        model  =  DailyMachineHoursInput
        fields = "__all__"

# create a form for daily machine hours
class accuracyInputForm(ModelForm):

    unit = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    tool_no = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    tool_name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    insert = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    turning = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    milling = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    edm = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    wire_cut = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    num_of_rejects = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    insertion_date = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    class Meta:
        model  =  DailyMachineHoursInput
        fields = "__all__"
