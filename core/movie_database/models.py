from django.db import models


class Movie(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    title = models.TextField()
    release_year = models.DateField()


class Collection(models.Model):
    name = models.TextField()
    movies = models.ManyToManyField(Movie)
