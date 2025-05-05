from django import forms
from ..admin_control.models import Model

class NewsDetectionForm(forms.Form):
    text = forms.CharField()
    model = forms.ModelChoiceField(queryset=Model.objects.all())