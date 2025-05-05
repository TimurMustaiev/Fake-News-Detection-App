from django.contrib import admin
from .models import Model, Feature, Parameter, FeatureInModel, ParameterInModel


admin.site.register(Model)
admin.site.register(Feature)
admin.site.register(Parameter)
admin.site.register(FeatureInModel)
admin.site.register(ParameterInModel)