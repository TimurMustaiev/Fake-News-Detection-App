from django.shortcuts import render
from django.views import View
from django.views.generic import ListView


class ModelListView(ListView):
    def get(self, request):
        return render(request, "model-list.html")
    
class ModelActionView(View):
    def get(self, request):
        return render(request, "model-create.html")