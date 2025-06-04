import asyncio
import os
import pandas as pd
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from .models import Model, Feature, FeatureInModel, ParameterInModel, Parameter
from .forms import ModelCreateForm, ModelFeaturesForm, ParameterInModelForm
from .classificator import ModelManager
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings


class ModelListView(LoginRequiredMixin, ListView):
    model = Model
    queryset = Model.objects.all()

    def get(self, request):
        models = self.get_queryset()
        return render(request, "model-list.html", {"model_list": models})
    

class ModelCreateView(LoginRequiredMixin, View):
    def get(self, request):
        action = request.GET.get('action')
        if action is None:
            request.session['features'] = []
            request.session['parameters'] = []
            model_form = ModelCreateForm()
        else:
            model_form = ModelCreateForm(initial={'name': request.GET.get('name')})

        feature_form = ModelFeaturesForm()
        parameter_form = ParameterInModelForm()

        if 'features' not in request.session:
            request.session['features'] = []
        if 'parameters' not in request.session:
            request.session['parameters'] = []

        if action == 'add_feature':
            feature_form = ModelFeaturesForm(request.GET)
            if feature_form.is_valid():
                feature = feature_form.cleaned_data['feature']
                request.session['features'].append({
                    'feature_id': feature.feature_id,
                    'name': feature.name,
                })
                print(request.session['features'])
                request.session.modified = True
        elif action == 'add_parameter':
            parameter_form = ParameterInModelForm(request.GET)
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

        new_feature_form = ModelFeaturesForm()
        new_parameter_form = ParameterInModelForm()

        return render(request, "model-create.html", {
            "model_form": model_form,
            "feature_form": new_feature_form,
            "parameter_form": new_parameter_form,
            "features": request.session.get("features", []),
            "parameters": request.session.get("parameters", [])
        })
    
    def post(self, request):
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
                asyncio.run(model_trainer.create_model(
                    model_name,
                    news.iloc[:1_500],
                    features_names,
                    params
                ))
                
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

        return redirect("model-create", {"features": request.session["features"], "parameters": request.session["parameters"]})


class ModelView(LoginRequiredMixin, View):
    def get(self, request, model_id):
        model = Model.objects.get(pk=model_id)
        features = model.featureinmodel_set.all()
        parameters = model.parameterinmodel_set.all()
        page_vars = {
            "model": model, 
            "features_in_model": features, 
            "parameters_in_model": parameters
        }
        if "edit_start" in request.session:
            page_vars.update({"edit_start": True})
        return render(request, "model-info.html", page_vars)


class ModelDeleteView(LoginRequiredMixin, View):
    def get(self, request, model_id):
        model = Model.objects.get(pk=model_id)
        path = settings.DETECTION_MODELS_PATH / f"{model.name}.json"
        model.delete()
        if os.path.isfile(path):
            os.remove(path)
        return redirect("model-list")
    

class FeatureUpdateView(LoginRequiredMixin, View):
    def get(self, request, model_id, feature_id):
        model = Model.objects.get(pk=model_id)
        form = ModelFeaturesForm()
        return render(request, "feature-upd.html", {"form": form})
    
    def post(self, request, model_id, feature_id):
        form = ModelFeaturesForm(request.POST)
        if form.is_valid():
            model = Model.objects.get(pk=model_id)
            feature_in_model = model.featureinmodel_set.get(feature_id=feature_id)
            new_feature = form.cleaned_data.get("feature")
            feature_in_model_obj = FeatureInModel.objects.get(feature=feature_in_model.feature, model=model)
            feature_in_model_obj.feature = new_feature
            feature_in_model_obj.save()
            request.session["edit_start"] = True
        return redirect("model-info", model_id)


class ParameterUpdateView(LoginRequiredMixin, View):
    def get(self, request, model_id, parameter_id):
        model = Model.objects.get(pk=model_id)
        form = ParameterInModelForm()
        return render(request, "parameter-upd.html", {"form": form})
    
    def post(self, request, model_id, parameter_id):
        form = ParameterInModelForm(request.POST)
        if form.is_valid():
            model = Model.objects.get(pk=model_id)
            new_parameter = form.cleaned_data.get("parameter")
            value = form.cleaned_data.get("value")
            parameter_in_model = model.parameterinmodel_set.get(parameter_id=parameter_id)
            parameter_in_model_obj = ParameterInModel.objects.get(parameter=parameter_in_model.parameter, model=model)
            parameter_in_model_obj.parameter = new_parameter
            parameter_in_model_obj.value = value
            parameter_in_model_obj.save()
            request.session["edit_start"] = True
        return redirect("model-info", model_id)


class ModelUpdateView(LoginRequiredMixin, View):
    def post(self, request, model_id):
        model = Model.objects.get(pk=model_id)
        file_path = os.path.join(settings.DETECTION_MODELS_PATH, model.location)
        os.remove(file_path)

        features_in_model = model.featureinmodel_set.all()
        features_names = []
        for feature_in_model in features_in_model:
            features_names.append(feature_in_model.feature.name)
        parameters_in_model = model.parameterinmodel_set.all()
        params = {}
        for parameter_in_model in parameters_in_model:
            params.update({f"{parameter_in_model.parameter.name}": parameter_in_model.value})
            params.update({'objective': 'binary:logistic'})
            model_trainer = ModelManager()
            news = model_trainer.prepare_data()
            model_trainer.create_model(
                model.name,
                news,
                features_names,
                params
            )
        del request.session["edit_start"]
        return redirect("model-info", model_id)


class ModelStatsView(LoginRequiredMixin, View):
    def get(self, request, model_id):
        generate = request.GET.get("generate")
        if generate:
            if request.session.get("scores") and request.session.get("plots"):
                del request.session["scores"]
                del request.session["plots"]
            df = pd.read_csv(settings.DATASET_PATH / "news.csv")
            df["text"] = df["text"].fillna('').astype(str)
            news = df[["text", "label"]]
            model_manager = ModelManager()
            scores, plots = model_manager.prepare_performance_data(news[:1000], model_id)
            request.session['scores'] = scores
            request.session['plots'] = plots
            return render(request, "model-performance.html", {
                "accuracy_score": scores["accuracy"],
                "precision_score": scores["precision"],
                "recall_score": scores["recall"],
                "f1_score": scores["f1"],
                "log_loss_score": scores["log_loss"],
                "precision_recall_curve": plots["precision_recall"],
                "roc_auc_curve": plots["roc_auc"],
                "t_sne_plot": plots["t_sne"]
            })
        else:
            scores = request.session["scores"]
            plots = request.session["plots"]
            return render(request, "model-performance.html", {
                "accuracy_score": scores["accuracy"],
                "precision_score": scores["precision"],
                "log_loss_score": scores["log_loss"],
                "precision_recall_curve": plots["precision_recall"],
                "roc_auc_curve": plots["roc_auc"],
                "t_sne_plot": plots["t_sne"]
            })