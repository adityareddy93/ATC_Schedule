from django import forms
from django.forms import ModelForm
from .models import DailyMachineHours,TotalLoadOnSystemsInput
#widget
class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField(label = 'E-Mail')
#category  = forms.ChoiceField(choices=[('question','Answer'),('other','Other')])


# create a forms
class estimatedHoursForm(ModelForm):
    Unit_choice=(
        ("unit 1","unit 1"),
        ("unit 2","unit 2"),
        ("unit 3","unit 3"),
        ("unit 4","unit 4"),
    )
    machine_choice = (
        ("turning","turning"),
        ("milling","milling"),
        ("edm","edm"),
        ("wire cut","wire cut"),
    )

    department = forms.ChoiceField(choices = Unit_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    tool_no = forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    tool_name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    insert = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100px'}))
    num_of_inserts = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:120px'}))
    machines = forms.ChoiceField(choices = machine_choice,widget=forms.Select(attrs={'style': 'width:100px'}))
    estimated_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:150px'}))
    buffer_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    insertion_date = forms.DateField(widget=forms.DateInput(attrs={'style': 'width:100px'}))
    class Meta:
        model  =  TotalLoadOnSystemsInput
        fields = "__all__"
        #fields = ('tool_info','date')
