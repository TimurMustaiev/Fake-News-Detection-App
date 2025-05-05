from django.shortcuts import render, redirect
from django.views import View
from .forms import NewsDetectionForm
from ..admin_control.classificator import ModelManager

class DetectionView(View):
    def get(self, request):
        form = NewsDetectionForm()
        return render(request, "index.html", {"form": form})
    
    def post(self, request):
        form = NewsDetectionForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data.get("text")
            model = form.cleaned_data.get("model")
            model_manager = ModelManager()
            result = model_manager.detect_fake(text, model)
            return render(request, "index.html", {"result": result[0]})

        return redirect("index")