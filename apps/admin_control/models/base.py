from django.db import models


class Model(models.Model):
    model_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    location = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)

class Feature(models.Model):
    feature_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField()

class Parameter(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)