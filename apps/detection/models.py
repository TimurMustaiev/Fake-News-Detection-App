from django.db import models
from django.contrib.auth import get_user_model

class Attempt(models.Model):
    attempt_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    news_text = models.TextField()
    model = models.ForeignKey(to="admin_control.Model", on_delete=models.CASCADE)
    result = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
