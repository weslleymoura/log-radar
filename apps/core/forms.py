from django import forms
from .models import DataPoint

class DataPointForm(forms.ModelForm):
    class Meta:
        model = DataPoint
        fields = ['origin', 'destination', 'business_key', 'dim_1', 'dim_2']

