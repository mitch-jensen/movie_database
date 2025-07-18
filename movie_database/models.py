from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
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


class ShelfDimensions(models.Model):
    """Represents the dimensions of a shelf."""

    width = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    depth = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:  # noqa: D106
        verbose_name = "Shelf Dimensions"
        verbose_name_plural = "Shelf Dimensions"

    def __str__(self) -> str:  # noqa: D105
        return f"<ShelfDimensions: {self.width:.2f} x {self.height:.2f} x {self.depth:.2f}>"


class PhysicalMediaOrientation(models.TextChoices):
    """Choices for Physical Media orientation."""

    VERTICAL = "V", "Vertical"
    HORIZONTAL = "H", "Horizontal"


class Shelf(models.Model):
    """Represents a shelf in a bookcase."""

    position_from_top = models.PositiveSmallIntegerField()
    bookcase = models.ForeignKey("Bookcase", on_delete=models.CASCADE, related_name="shelves")
    dimensions = models.ForeignKey(
        ShelfDimensions,
        on_delete=models.PROTECT,
        related_name="shelf_dimensions",
    )
    orientation = models.CharField(
        max_length=1,
        choices=PhysicalMediaOrientation.choices,
        default=PhysicalMediaOrientation.VERTICAL,
    )

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

    def can_fit_media(self, media: "PhysicalMedia") -> bool:
        """Check if a single PhysicalMedia can physically fit on this shelf."""
        if self.orientation == PhysicalMediaOrientation.VERTICAL.value:
            return media.case_dimensions.height <= self.dimensions.height
        return media.case_dimensions.width <= self.dimensions.width

    def used_space(self) -> Decimal:
        """Return the amount of shelf space used up physical media."""
        # If there are no physical media on the shelf, there's no used space
        if not self.physicalmedia_set.exists():
            return Decimal(0)

        aggregation_field = f"case_dimensions__{'height' if self.orientation == PhysicalMediaOrientation.VERTICAL.value else 'width'}"
        used: dict[str, Decimal] = self.physicalmedia_set.select_related("case_dimensions").aggregate(used_space=models.Sum(aggregation_field))
        return used["used_space"]

    def available_space(self) -> Decimal:
        """Return remaining usable width (VERTICAL) or height (HORIZONTAL) in mm."""
        total_space = self.dimensions.height if self.orientation == PhysicalMediaOrientation.VERTICAL.value else self.dimensions.width
        return total_space - self.used_space()

    def can_accommodate(self, media: "PhysicalMedia") -> bool:
        """Check if a PhysicalMedia fits based on both dimensions and available space."""
        # If shelf physically cannot fit media, return early
        if not self.can_fit_media(media):
            return False

        available_space = self.available_space()

        if self.orientation == PhysicalMediaOrientation.VERTICAL.value:
            return media.case_dimensions.width <= available_space
        return media.case_dimensions.height <= available_space


class Bookcase(models.Model):
    """Represents a physical bookcase/shelf where movies are stored."""

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self) -> str:  # noqa: D105
        return f"<Bookcase: {self.name}>"


class Movie(models.Model):
    """Represents a movie linked to a TMDb profile."""

    title = models.CharField(max_length=255)
    release_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1888), MaxValueValidator(2100)])
    letterboxd_uri = models.URLField()
    watched = models.BooleanField(default=False)

    class Meta:  # noqa: D106
        constraints = (models.UniqueConstraint(fields=["title", "release_year", "letterboxd_uri"], name="unique_movie"),)

    def __str__(self) -> str:  # noqa: D105
        return f"<Movie: {self.title} ({self.release_year})>"


class TMDbProfile(models.Model):
    """Metadata from The Movie Database (TMDb)."""

    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, related_name="tmdb")
    tmdb_id = models.PositiveIntegerField(unique=True)

    def __str__(self) -> str:  # noqa: D105
        return f"<TMDbProfile: {self.tmdb_id} - {self.movie.title}>"


class Collection(models.Model):
    """Represents a collection of movies by a distributor."""

    name = models.CharField(max_length=255)

    def __str__(self) -> str:  # noqa: D105
        return f"<Collection: {self.name}>"

    @property
    def movies(self) -> models.QuerySet[Movie]:
        """Return a QuerySet of all movies associated with this collection."""
        return Movie.objects.filter(media_copies__collection=self)


class PhysicalMedia(models.Model):
    """A physical copy of one or more movies (e.g., a DVD, Blu-ray)."""

    movies = models.ManyToManyField(Movie, related_name="media_copies", blank=False)
    shelf = models.ForeignKey(Shelf, on_delete=models.SET_NULL, null=True, blank=True)
    position_on_shelf = models.PositiveSmallIntegerField(null=True, blank=True)
    case_dimensions = models.ForeignKey(
        MediaCaseDimensions,
        on_delete=models.PROTECT,
        related_name="media_dimensions",
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="physical_media",
    )
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
        return f"<PhysicalMedia: {movie_titles}>"
