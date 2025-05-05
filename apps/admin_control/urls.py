from django.urls import path
from .views import ModelListView, ModelCreateView

urlpatterns = [
    path('', ModelListView.as_view(), name="model-list"),
    path('create/', ModelCreateView.as_view(), name="model-create"),
]