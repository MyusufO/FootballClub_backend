from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    position = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    club = models.CharField(max_length=100)
    rating = models.FloatField()
    potential = models.FloatField()

    class Meta:
        app_label = 'players'

    def __str__(self):
        return f'{self.name} ({self.club})'
