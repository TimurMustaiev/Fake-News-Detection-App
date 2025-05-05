from django import forms
from ..admin_control.models import Model

class NewsDetectionForm(forms.Form):
    text = forms.CharField(label="Текст новини")
    model = forms.ModelChoiceField(queryset=Model.objects.all(), label="Модель класифікації")