from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class MediaFormat(models.TextChoices):
    """Choices for Physical Media formats."""

    DVD = "DVD", "DVD"
    BLURAY = "BD", "Blu-ray"
    VHS = "VHS", "VHS"
    UHD_4K = "4K", "4K UHD"


class Dimension(models.Model):
    """Abstract model representing anything with a width, height and depth."""

    width = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    depth = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:  # noqa: D106
        abstract = True


class MediaCaseDimensions(Dimension):
    """Represents the dimensions of a media case."""

    id: int
    media_format = models.CharField(max_length=3, choices=MediaFormat.choices)
    description = models.CharField(max_length=255, blank=False)
    physical_media_set: "RelatedManager['PhysicalMedia']"

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride] # noqa: D106
        verbose_name = "Media Case Dimensions"
        verbose_name_plural = "Media Case Dimensions"

    def __repr__(self) -> str:  # noqa: D105
        return f"<MediaCaseDimensions ({self.media_format}): {self.width:.2f}W x {self.height:.2f}H x {self.depth:.2f}D>"

    def __str__(self) -> str:  # noqa: D105
        return f"{self.width:.2f}W x {self.height:.2f}H x {self.depth:.2f}D"


class ShelfDimensions(Dimension):
    """Represents the dimensions of a shelf."""

    id: int
    shelves: "RelatedManager['Shelf']"

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride] # noqa: D106
        verbose_name = "Shelf Dimensions"
        verbose_name_plural = "Shelf Dimensions"

    def __repr__(self) -> str:  # noqa: D105
        return f"<ShelfDimensions: {self.width:.2f} x {self.height:.2f} x {self.depth:.2f}>"

    def __str__(self) -> str:  # noqa: D105
        return f"{self.width:.2f} x {self.height:.2f} x {self.depth:.2f}"


class PhysicalMediaOrientation(models.TextChoices):
    """Choices for Physical Media orientation."""

    VERTICAL = "V", "Vertical"
    HORIZONTAL = "H", "Horizontal"


class Shelf(models.Model):
    """Represents a shelf in a bookcase."""

    id: int
    position_from_top = models.PositiveSmallIntegerField()
    bookcase_id: int
    bookcase = models.ForeignKey["Bookcase"](
        "Bookcase",
        on_delete=models.CASCADE,
        related_name="shelves",
    )
    dimensions_id: int
    dimensions = models.ForeignKey["ShelfDimensions"](
        "ShelfDimensions",
        on_delete=models.PROTECT,
        related_name="shelves",
    )
    orientation = models.CharField(
        max_length=1,
        choices=PhysicalMediaOrientation.choices,
        default=PhysicalMediaOrientation.VERTICAL,
    )
    physical_media_set: "RelatedManager['PhysicalMedia']"

    class Meta:  # noqa: D106
        ordering = ("position_from_top",)
        constraints = (
            models.UniqueConstraint(
                fields=["bookcase", "position_from_top"],
                name="unique_shelf_position_from_top",
            ),
        )

    def __repr__(self) -> str:  # noqa: D105
        return f"<Shelf: {self.bookcase.name} - Shelf {self.position_from_top}>"

    def __str__(self) -> str:  # noqa: D105
        return f"{self.bookcase.name} - Shelf {self.position_from_top}"

    def can_fit_media(self, media: "PhysicalMedia") -> bool:
        """Check if a single PhysicalMedia can physically fit on this shelf."""
        if self.orientation == PhysicalMediaOrientation.VERTICAL.value:
            return media.case_dimensions.height <= self.dimensions.height
        return media.case_dimensions.width <= self.dimensions.width

    async def used_space(self) -> Decimal:
        """Return the amount of shelf space used up physical media."""
        # If there are no physical media on the shelf, there's no used space
        if not await self.physical_media_set.aexists():
            return Decimal(0)

        aggregation_field = f"case_dimensions__{'height' if self.orientation == PhysicalMediaOrientation.VERTICAL.value else 'width'}"
        used: dict[str, Decimal] = await self.physical_media_set.select_related("case_dimensions").aaggregate(used_space=models.Sum(aggregation_field))
        return used["used_space"]

    async def available_space(self) -> Decimal:
        """Return remaining usable width (VERTICAL) or height (HORIZONTAL) in mm."""
        total_space = self.dimensions.height if self.orientation == PhysicalMediaOrientation.VERTICAL.value else self.dimensions.width
        return total_space - await self.used_space()

    async def can_accommodate(self, media: "PhysicalMedia") -> bool:
        """Check if a PhysicalMedia fits based on both dimensions and available space."""
        # If shelf physically cannot fit media, return early
        if not self.can_fit_media(media):
            return False

        available_space: Decimal = await self.available_space()

        if self.orientation == PhysicalMediaOrientation.VERTICAL.value:
            return media.case_dimensions.width <= available_space
        return media.case_dimensions.height <= available_space


class Bookcase(models.Model):
    """Represents a physical bookcase/shelf where movies are stored."""

    id: int
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    shelves: "RelatedManager['Shelf']"

    def __repr__(self) -> str:  # noqa: D105
        return f"<Bookcase: {self.name}>"

    def __str__(self) -> str:  # noqa: D105
        return self.name


class Movie(models.Model):
    """Represents a movie linked to a TMDb profile."""

    id: int
    title = models.CharField(max_length=255)
    release_year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1888),
            MaxValueValidator(2100),
        ],
    )
    letterboxd_uri = models.URLField()
    watched = models.BooleanField(default=False)
    physical_media_set: "RelatedManager['PhysicalMedia']"

    class Meta:  # noqa: D106
        constraints = (
            models.UniqueConstraint(
                fields=[
                    "title",
                    "release_year",
                    "letterboxd_uri",
                ],
                name="unique_movie",
            ),
        )
        ordering = (
            "release_year",
            "title",
        )

    def __lt__(self, other: "Movie") -> bool:  # noqa: D105
        return (self.release_year, self.title.lower()) < (other.release_year, other.title.lower())

    def __repr__(self) -> str:  # noqa: D105
        return f"<Movie: {self.title} ({self.release_year})>"

    def __str__(self) -> str:  # noqa: D105
        return f"{self.title} ({self.release_year})"


class TMDbProfile(models.Model):
    """Metadata from The Movie Database (TMDb)."""

    id: int
    movie_id: int
    movie = models.OneToOneField["Movie"](
        "Movie",
        on_delete=models.CASCADE,
        related_name="tmdb",
    )
    tmdb_id = models.PositiveIntegerField(unique=True)

    def __repr__(self) -> str:  # noqa: D105
        return f"<TMDbProfile: {self.tmdb_id} - {self.movie.title}>"

    def __str__(self) -> str:  # noqa: D105
        return self.movie.title


class Collection(models.Model):
    """Represents a collection of movies by a distributor."""

    id: int
    name = models.CharField(max_length=255)
    physical_media_set: "RelatedManager['PhysicalMedia']"

    def __repr__(self) -> str:  # noqa: D105
        return f"<Collection: {self.name}>"

    def __str__(self) -> str:  # noqa: D105
        return self.name

    def get_movies(self) -> models.QuerySet[Movie]:
        """Return a QuerySet of all movies associated with this collection."""
        return Movie.objects.filter(physical_media_set__collection=self).distinct()


class PhysicalMedia(models.Model):
    """A physical copy of one or more movies (e.g., a DVD, Blu-ray)."""

    id: int
    movies = models.ManyToManyField["Movie", models.Model](
        "Movie",
        related_name="physical_media_set",
        blank=False,
    )
    shelf_id: int | None
    shelf = models.ForeignKey["Shelf"](
        "Shelf",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="physical_media_set",
    )
    position_on_shelf = models.PositiveSmallIntegerField(null=True, blank=True)
    case_dimensions_id: int
    case_dimensions = models.ForeignKey["MediaCaseDimensions"](
        "MediaCaseDimensions",
        on_delete=models.PROTECT,
        related_name="physical_media_set",
    )
    collection_id: int | None
    collection = models.ForeignKey["Collection"](
        "Collection",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="physical_media_set",
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

    def __repr__(self) -> str:  # noqa: D105
        movie_titles = ", ".join(f"{m.title} ({m.release_year})" for m in self.movies.all())
        return f"<PhysicalMedia: {movie_titles}>"

    def __str__(self) -> str:  # noqa: D105
        return ", ".join(f"{m.title} ({m.release_year})" for m in self.movies.all())
