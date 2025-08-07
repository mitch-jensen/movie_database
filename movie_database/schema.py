from typing import Annotated

from ninja import Field, FilterSchema, ModelSchema

import movie_database.models as movie_models

IContainsField = Annotated[str | None, Field(None, q="__icontains")]  # pyright: ignore[reportCallIssue]


class BookcaseBase(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Bookcase
        fields = ("name", "description", "location")


class BookcaseOut(BookcaseBase):  # noqa: D101
    id: int


class BookcaseIn(BookcaseBase):  # noqa: D101
    pass


class CollectionBase(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Collection
        fields = ("name",)


class CollectionOut(CollectionBase):  # noqa: D101
    id: int


class CollectionIn(CollectionBase):  # noqa: D101
    pass


class ShelfBase(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Shelf
        fields = ("position_from_top", "orientation")


class ShelfOut(ShelfBase):  # noqa: D101
    id: int


class ShelfIn(ShelfBase):  # noqa: D101
    pass


class MediaCaseDimensionBase(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.MediaCaseDimension
        fields = ("width", "height", "depth", "media_format", "description")


class MediaCaseDimensionOut(MediaCaseDimensionBase):  # noqa: D101
    id: int


class MediaCaseDimensionIn(MediaCaseDimensionBase):  # noqa: D101
    pass


class MediaCaseDimensionFilter(FilterSchema):  # noqa: D101
    title: IContainsField
    release_year: int | None = Field(None)


class ShelfDimensionBase(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.ShelfDimension
        fields = ("width", "height", "depth")


class ShelfDimensionOut(ShelfDimensionBase):  # noqa: D101
    id: int


class ShelfDimensionIn(ShelfDimensionBase):  # noqa: D101
    pass


class MovieBase(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.Movie
        fields = ("title", "release_year", "letterboxd_uri", "watched")


class MovieOut(MovieBase):  # noqa: D101
    id: int


class MovieIn(MovieBase):  # noqa: D101
    pass


class PhysicalMediaBase(ModelSchema):  # noqa: D101
    class Meta:  # noqa: D106
        model = movie_models.PhysicalMedia
        fields = ("position_on_shelf", "notes")


class PhysicalMediaOut(PhysicalMediaBase):  # noqa: D101
    id: int


class PhysicalMediaIn(PhysicalMediaBase):  # noqa: D101
    pass


class MovieFilter(FilterSchema):  # noqa: D101
    title: IContainsField
    release_year: Annotated[int | None, Field(None)]
    release_year_lt: Annotated[int | None, Field(None, q="release_year__lt")]
    release_year_gt: Annotated[int | None, Field(None, q="release_year__gt")]
    watched: bool | None = Field(None)
