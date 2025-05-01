from django.db import models


class ParameterInModel(models.Model):
    parameter_in_model_id = models.AutoField(primary_key=True)
    parameter = models.ForeignKey(to="Parameter", on_delete=models.PROTECT)
    model = models.ForeignKey(to="Model", on_delete=models.PROTECT)
    value = models.FloatField()

class FeatureInModel(models.Model):
    feature_in_model_id = models.AutoField(primary_key=True)
    feature = models.ForeignKey(to="Feature", on_delete=models.PROTECT)
    model = models.ForeignKey(to="Model", on_delete=models.PROTECT)
    value = models.FloatField()