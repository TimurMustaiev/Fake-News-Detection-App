from django.db import models


class Model(models.Model):
    model_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    location = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        features = self.featureinmodel_set.all().select_related("feature")
        parameters = self.parameterinmodel_set.all().select_related("parameter")

        feature_names = [f.feature.name for f in features]
        parameter_names = [f"{p.parameter.name}={p.value} - {p.parameter.description}" for p in parameters]

        return f'Модель "{self.name}" | Ознаки: {", ".join(feature_names)} | Параметри: {", ".join(parameter_names)}'

class Feature(models.Model):
    feature_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField()

    def __str__(self):
        return f'{self.name} | Опис: {self.description}'
    

class Parameter(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField()

    def __str__(self):
        return f'{self.name} | Опис: {self.description}'