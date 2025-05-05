from django.urls import path
from .views import ModelListView, ModelCreateView, ModelView, ModelDeleteView

urlpatterns = [
    path('', ModelListView.as_view(), name="model-list"),
    path('create/', ModelCreateView.as_view(), name="model-create"),
    path('<int:model_id>/', ModelView.as_view(), name="model-info"),
    path('<int:model_id>/delete', ModelDeleteView.as_view(), name="model-delete")
]