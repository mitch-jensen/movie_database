from typing import Annotated

from ninja import Field, FilterSchema, ModelSchema

from .models import Movie

IContainsField = Annotated[str | None, Field(None, q="__icontains")]  # pyright: ignore[reportCallIssue]


class MovieSchema(ModelSchema):
    """Schema for the Movie model."""

    class Meta:
        """Meta class for MovieSchema."""

        model = Movie
        fields = ("id", "title", "release_year", "letterboxd_uri", "watched")


class MovieFilterSchema(FilterSchema):
    """Schema for filtering movies."""

    title: IContainsField
    release_year: int | None = Field(None)
    watched: bool | None = Field(None)
