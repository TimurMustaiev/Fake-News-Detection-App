from django import forms
from .models import Model, Parameter, Feature


class ModelCreateForm(forms.Form):
    name = forms.CharField(max_length=50, label='Назва')

class ModelFeaturesForm(forms.Form):
    feature = forms.ModelChoiceField(queryset=Feature.objects.all(), label='Ознака')

class ParameterInModelForm(forms.Form):
    parameter = forms.ModelChoiceField(queryset=Parameter.objects.all(), label='Параметр')
    value = forms.FloatField()

    def clean(self):
        cleaned_data = super().clean()
        param = cleaned_data.get("parameter")
        value = cleaned_data.get("value")

        if param and value is not None:
            if param.param_type == 'int':
                if not float(value).is_integer():
                    raise forms.ValidationError("Цей параметр приймає лише цілі значення.")
                cleaned_data["value"] = int(value)
            elif param.param_type == 'float':
                cleaned_data["value"] = float(value)

        return cleaned_data