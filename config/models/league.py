from django.db import models

class League(models.Model):
    server = models.CharField(max_length=50)
    