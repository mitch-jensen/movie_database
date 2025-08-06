from typing import Annotated

from ninja import Field, FilterSchema, ModelSchema

from .models import MediaCaseDimensions, Movie, PhysicalMedia

IContainsField = Annotated[str | None, Field(None, q="__icontains")]  # pyright: ignore[reportCallIssue]


class MediaCaseDimensionSchemaOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = MediaCaseDimensions
        fields = ("id", "width", "height", "depth", "media_format", "description")


class MediaCaseDimensionSchemaIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = MediaCaseDimensions
        fields = ("width", "height", "depth", "media_format", "description")


class MediaCaseDimensionFilterSchema(FilterSchema):  # noqa: D101
    title: IContainsField
    release_year: int | None = Field(None)


class MovieSchemaOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = Movie
        fields = ("id", "title", "release_year", "letterboxd_uri", "watched")


class MovieSchemaIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = Movie
        fields = ("title", "release_year", "letterboxd_uri", "watched")


class PhysicalMediaSchema(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = PhysicalMedia
        fields = ("position_on_shelf", "notes")


class MovieSchemaWithMedia(MovieSchemaOut):  # noqa: D101
    physical_media_set: list[PhysicalMediaSchema]


class MovieFilterSchema(FilterSchema):  # noqa: D101
    title: IContainsField
    release_year: Annotated[int | None, Field(None)]
    release_year_lt: Annotated[int | None, Field(None, q="release_year__lt")]
    release_year_gt: Annotated[int | None, Field(None, q="release_year__gt")]
    watched: bool | None = Field(None)
