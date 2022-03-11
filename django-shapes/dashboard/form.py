from django.forms import ModelForm
from .models import *
from django import forms

class DateInput(forms.DateInput):
    input_type = 'date'

class AssesmentForm(ModelForm):
    class Meta:
        model = Assesment
        fields = '__all__'
        widgets ={
            "date": DateInput(),
        }

