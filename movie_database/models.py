from django.db import models


class MediaFormat(models.TextChoices):
    """Choices for Physical Media formats."""

    DVD = "DVD", "DVD"
    BLURAY = "BD", "Blu-ray"
    VHS = "VHS", "VHS"
    UHD_4K = "4K", "4K UHD"


class MediaCaseDimensions(models.Model):
    """Represents the dimensions of a media case."""

    media_format = models.CharField(max_length=3, choices=MediaFormat.choices)
    description = models.CharField(max_length=255, blank=False)
    width = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    depth = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:  # noqa: D106
        verbose_name = "Media Case Dimensions"
        verbose_name_plural = "Media Case Dimensions"

    def __str__(self) -> str:  # noqa: D105
        return f"<MediaCaseDimensions ({self.media_format}): {self.width:.2f} x {self.height:.2f} x {self.depth:.2f}>"


class Shelf(models.Model):
    """Represents a shelf in a bookcase."""

    position_from_top = models.PositiveSmallIntegerField()
    bookcase = models.ForeignKey("Bookcase", on_delete=models.CASCADE, related_name="shelves")

    class Meta:  # noqa: D106
        ordering = ("position_from_top",)
        constraints = (
            models.UniqueConstraint(
                fields=["bookcase", "position_from_top"],
                name="unique_shelf_position_from_top",
            ),
        )

    def __str__(self) -> str:  # noqa: D105
        return f"<Shelf: {self.bookcase.name} - {self.position_from_top}>"


class Bookcase(models.Model):
    """Represents a physical bookcase/shelf where movies are stored."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:  # noqa: D105
        return f"<Bookcase: {self.name}>"


class Movie(models.Model):
    """Represents a movie linked to a TMDb profile."""

    title = models.CharField(max_length=255)
    release_year = models.DateField()

    def __str__(self) -> str:  # noqa: D105
        return f"<Movie: {self.title} ({self.release_year})>"


class Collection(models.Model):
    """Represents a collection of movies by a distributor."""

    name = models.CharField(max_length=255)
    movies = models.ManyToManyField(Movie)

    def __str__(self) -> str:  # noqa: D105
        return f"<Collection: {self.name}>"


class PhysicalMedia(models.Model):
    """A physical copy of one or more movies (e.g., a DVD, Blu-ray)."""

    movies = models.ManyToManyField(Movie, related_name="media_copies")
    shelf = models.ForeignKey(Shelf, on_delete=models.SET_NULL, null=True, blank=True)
    position_on_shelf = models.PositiveSmallIntegerField(null=True, blank=True)
    media_format = models.CharField(max_length=3, choices=MediaFormat.choices)
    notes = models.TextField(blank=True)

    class Meta:  # noqa: D106
        ordering = ("shelf__position_from_top", "position_on_shelf")
        verbose_name = "Physical Media"
        verbose_name_plural = "Physical Media"
        constraints = (
            models.UniqueConstraint(
                fields=["shelf", "position_on_shelf"],
                name="unique_position_on_shelf",
            ),
        )

    def __str__(self) -> str:  # noqa: D105
        movie_titles = ", ".join(m.title for m in self.movies.all())
        return f"{self.media_format} - {movie_titles}"
