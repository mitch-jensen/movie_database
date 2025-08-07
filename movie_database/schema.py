from typing import Annotated

from ninja import Field, FilterSchema, ModelSchema

import movie_database.models as movie_models

IContainsField = Annotated[str | None, Field(None, q="__icontains")]  # pyright: ignore[reportCallIssue]


class BookcaseOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Bookcase
        fields = ("id", "name", "description", "location")


class BookcaseIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Bookcase
        fields = ("name", "description", "location")


class CollectionOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Collection
        fields = ("id", "name")


class CollectionIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Collection
        fields = ("name",)


class ShelfOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Shelf
        fields = ("id", "position_from_top", "orientation")


class MediaCaseDimensionOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.MediaCaseDimensions
        fields = ("id", "width", "height", "depth", "media_format", "description")


class MediaCaseDimensionIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.MediaCaseDimensions
        fields = ("width", "height", "depth", "media_format", "description")


class MediaCaseDimensionFilter(FilterSchema):  # noqa: D101
    title: IContainsField
    release_year: int | None = Field(None)


class ShelfDimensionOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.MediaCaseDimensions
        fields = ("id", "width", "height", "depth")


class ShelfDimensionIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.MediaCaseDimensions
        fields = ("width", "height", "depth")


class MovieOut(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Movie
        fields = ("id", "title", "release_year", "letterboxd_uri", "watched")


class MovieIn(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Movie
        fields = ("title", "release_year", "letterboxd_uri", "watched")


class PhysicalMedia(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.PhysicalMedia
        fields = ("position_on_shelf", "notes")


class MovieFilter(FilterSchema):  # noqa: D101
    title: IContainsField
    release_year: Annotated[int | None, Field(None)]
    release_year_lt: Annotated[int | None, Field(None, q="release_year__lt")]
    release_year_gt: Annotated[int | None, Field(None, q="release_year__gt")]
    watched: bool | None = Field(None)
