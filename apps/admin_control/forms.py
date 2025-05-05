from django import forms
from .models import Model, Parameter, Feature


class ModelCreateForm(forms.Form):
    name = forms.CharField(max_length=50, label='Назва')

class ModelFeaturesForm(forms.Form):
    feature = forms.ModelChoiceField(queryset=Feature.objects.all(), label='Ознака')

class ParameterInModelForm(forms.Form):
    parameter = forms.ModelChoiceField(queryset=Parameter.objects.all(), label='Параметр')
    value = forms.FloatField()