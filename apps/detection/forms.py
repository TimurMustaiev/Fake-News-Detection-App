from django import forms
from ..admin_control.models import Model

class NewsDetectionForm(forms.Form):
    text = forms.CharField(label="Текст новини", widget=forms.Textarea(attrs={
            'rows': 10,
            'cols': 80,
            'class': 'form-control',
        }))
    model = forms.ModelChoiceField(queryset=Model.objects.all(), label="Модель класифікації")