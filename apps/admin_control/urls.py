from django.urls import path
from .views import ModelListView, ModelCreateView, ModelView, ModelDeleteView, ModelUpdateView, FeatureUpdateView, ParameterUpdateView

urlpatterns = [
    path('', ModelListView.as_view(), name="model-list"),
    path('create/', ModelCreateView.as_view(), name="model-create"),
    path('<int:model_id>/', ModelView.as_view(), name="model-info"),
    path('<int:model_id>/delete', ModelDeleteView.as_view(), name="model-delete"),
    path('<int:model_id>/update', ModelUpdateView.as_view(), name="model-update"),
    path('<int:model_id>/features/<int:feature_id>/', FeatureUpdateView.as_view(), name="feature-update"),
    path('<int:model_id>/parameters/<int:parameter_id>/', ParameterUpdateView.as_view(), name="parameter-update"),
]