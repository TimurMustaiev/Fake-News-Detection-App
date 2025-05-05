from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from .models import Model, Feature, FeatureInModel, ParameterInModel, Parameter
from .forms import ModelCreateForm, ModelFeaturesForm, ParameterInModelForm
from .classificator import ModelManager


class ModelListView(ListView):
    model = Model
    queryset = Model.objects.all()

    def get(self, request):
        models = self.get_queryset()
        return render(request, "model-list.html", {"model_list": models})
    
class ModelCreateView(View):
    def get(self, request):
        # request.session['features'] = []
        # request.session['parameters'] = []
        model_form = ModelCreateForm()
        feature_form = ModelFeaturesForm()
        parameter_form = ParameterInModelForm()
        return render(request, "model-create.html", {
            "model_form": model_form,
            "feature_form": feature_form,
            "parameter_form": parameter_form
        })
    
    def post(self, request):
        action = request.POST.get('action')
        if 'features' not in request.session:
            request.session['features'] = []
        if 'parameters' not in request.session:
            request.session['parameters'] = []

        if action == 'add_feature':
            feature_form = ModelFeaturesForm(request.POST)
            if feature_form.is_valid():
                feature = feature_form.cleaned_data['feature']
                request.session['features'].append({
                    'feature_id': feature.feature_id,
                    'name': feature.name,
                })
                print(request.session['features'])
                request.session.modified = True

        elif action == 'add_parameter':
            parameter_form = ParameterInModelForm(request.POST)
            if parameter_form.is_valid():
                parameter = parameter_form.cleaned_data['parameter']
                value = parameter_form.cleaned_data['value']
                request.session['parameters'].append({
                    'parameter_id': parameter.parameter_id,
                    'name': parameter.name,
                    'value': value
                })
                print(request.session['parameters'])
                request.session.modified = True

        elif action == 'create_model':
            model_form = ModelCreateForm(request.POST)
            if model_form.is_valid():
                model_name = model_form.cleaned_data.get("name")
                features = request.session['features']
                features_names = []
                for feature in features:
                    features_names.append(feature['name'])
                parameters = request.session['parameters']
                params = {}
                for parameter in parameters:
                    params.update({f"{parameter['name']}": parameter['value']})
                params.update({'objective': 'binary:logistic'})
                model_trainer = ModelManager()
                news = model_trainer.prepare_data()
                model_trainer.create_model(
                    model_name,
                    news,
                    features_names,
                    params
                )
                
                model = Model(name=model_name, location=f"{model_name}.json")
                model.save()
                for feature in features:
                    feature_in_model = FeatureInModel()
                    feature_in_model.feature = Feature.objects.get(pk=feature['feature_id'])
                    feature_in_model.model = model
                    feature_in_model.save()
                for parameter in parameters:
                    parameter_in_model = ParameterInModel()
                    parameter_in_model.parameter = Parameter.objects.get(pk=parameter['parameter_id'])
                    parameter_in_model.model = model
                    parameter_in_model.value = parameter['value']
                    parameter_in_model.save()
                return redirect("model-list")

        return redirect("model-create")

class ModelView(View):
    def get(self, request, model_id):
        model = Model.objects.get(pk=model_id)
        features = model.featureinmodel_set.all()
        parameters = model.parameterinmodel_set.all()
        return render(request, "model-info.html", {"model": model, "features_in_model": features, "parameters_in_model": parameters})