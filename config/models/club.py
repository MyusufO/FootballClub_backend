from django.db import models

class Club(models.Model):
    name = models.CharField(max_length=100)
    server = models.CharField(max_length=50)
    league = models.CharField(max_length=100)
    rating = models.FloatField()
    budget = models.FloatField()