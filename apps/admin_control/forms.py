from django import forms
from .models import Model, Parameter, Feature


class ModelCreateForm(forms.Form):
    name = forms.CharField(max_length=50)

class ModelFeaturesForm(forms.Form):
    feature = forms.ModelChoiceField(queryset=Feature.objects.all())

class ParameterInModelForm(forms.Form):
    parameter = forms.ModelChoiceField(queryset=Parameter.objects.all())
    value = forms.FloatField()