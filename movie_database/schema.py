from typing import Annotated

from ninja import Field, FilterSchema, ModelSchema

from .models import Bookcase, Collection, MediaCaseDimensions, Movie, PhysicalMedia, Shelf

IContainsField = Annotated[str | None, Field(None, q="__icontains")]  # pyright: ignore[reportCallIssue]


class BookcaseSchemaOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = Bookcase
        fields = ("id", "name", "description", "location")


class BookcaseSchemaIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = Bookcase
        fields = ("name", "description", "location")


class CollectionSchemaOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = Collection
        fields = ("id", "name")


class CollectionSchemaIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = Collection
        fields = ("name",)


class ShelfSchemaOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = Shelf
        fields = ("id", "position_from_top", "orientation")


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


class ShelfDimensionSchemaOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = MediaCaseDimensions
        fields = ("id", "width", "height", "depth")


class ShelfDimensionSchemaIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = MediaCaseDimensions
        fields = ("width", "height", "depth")


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


class MovieFilterSchema(FilterSchema):  # noqa: D101
    title: IContainsField
    release_year: Annotated[int | None, Field(None)]
    release_year_lt: Annotated[int | None, Field(None, q="release_year__lt")]
    release_year_gt: Annotated[int | None, Field(None, q="release_year__gt")]
    watched: bool | None = Field(None)
