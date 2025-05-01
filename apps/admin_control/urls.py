from django.urls import path
from .views import ModelListView, ModelActionView

urlpatterns = [
    path('', ModelListView.as_view(), name="model-list"),
    path('action/', ModelActionView.as_view(), name="model-action"),
]