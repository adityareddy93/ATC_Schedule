from django import forms
from django.forms import ModelForm
from .models import TotalLoadOnSystemsInput, DailyMachineHoursInput
from .constants import Unit_choice, machines_choice, turning_choice, milling_choice, edm_choice, wire_cut_choice
#widget
class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField(label = 'E-Mail')
#category  = forms.ChoiceField(choices=[('question','Answer'),('other','Other')])


# create a forms
class estimatedHoursForm(ModelForm):

    department = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
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

    department = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    tool_no = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    tool_name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    insert = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    machine = forms.ChoiceField(choices = machines_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    turning = forms.ChoiceField(choices = turning_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    milling = forms.ChoiceField(choices = milling_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    edm = forms.ChoiceField(choices = edm_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    wire_cut = forms.ChoiceField(choices = wire_cut_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    no_of_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    insertion_date = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    class Meta:
        model  =  DailyMachineHoursInput
        fields = "__all__"

# create a form for daily machine hours
class accuracyInputForm(ModelForm):

    department = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    tool_no = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    tool_name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    machines = forms.ChoiceField(choices = machines_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    accuracy = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    num_of_rejects = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    estimated_cost = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    insertion_date = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    class Meta:
        model  =  DailyMachineHoursInput
        fields = "__all__"
