from django.db import models


class Movie(models.Model):
    """Represents a movie linked to a TMDb profile."""

    id = models.PositiveIntegerField(primary_key=True)
    title = models.TextField()
    release_year = models.DateField()

    def __str__(self) -> str:  # noqa: D105
        return f"<Movie: {self.title} ({self.release_year})>"


class Collection(models.Model):
    """Represents a collection of movies by a distributor."""

    name = models.TextField()
    movies = models.ManyToManyField(Movie)

    def __str__(self) -> str:  # noqa: D105
        return f"<Collection: {self.name}>"
