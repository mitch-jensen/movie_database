from collections.abc import Awaitable
from decimal import Decimal
from typing import Protocol

import pytest

from movie_database.models import Bookcase, MediaCaseDimensions, MediaFormat, Movie


class BookcaseCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        name: str,
        description: str = ...,
        location: str = ...,
    ) -> Awaitable[Bookcase]: ...


class MediaCaseDimensionCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        media_format: MediaFormat,
        description: str,
        width: Decimal,
        height: Decimal,
        depth: Decimal,
    ) -> Awaitable[MediaCaseDimensions]: ...


class MovieCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        title: str,
        release_year: str,
        letterboxd_uri: str = ...,
        watched: bool = ...,  # noqa: FBT001
    ) -> Awaitable[Movie]: ...


@pytest.fixture
@pytest.mark.django_db
async def make_bookcase() -> BookcaseCreator:
    """Make a bookcase.

    Returns:
        BookcaseCreator: a factory function to create a Bookcase object.

    """

    async def _make_bookcase(name: str, description: str = "", location: str = "") -> Bookcase:
        return await Bookcase.objects.acreate(name=name, description=description, location=location)

    return _make_bookcase


@pytest.fixture
@pytest.mark.django_db
async def make_media_case_dimensions() -> MediaCaseDimensionCreator:
    """Make a MediaCaseDimensions object.

    Returns:
        MediaCaseDimensionCreator: a factory function to create a MediaCaseDimensions object.

    """

    async def _make_media_case_dimensions(media_format: MediaFormat, description: str, width: Decimal, height: Decimal, depth: Decimal) -> MediaCaseDimensions:
        return await MediaCaseDimensions.objects.acreate(media_format=media_format, description=description, width=width, height=height, depth=depth)

    return _make_media_case_dimensions


@pytest.fixture
@pytest.mark.django_db
async def make_movie() -> MovieCreator:
    """Make a movie.

    Returns:
        MovieCreator: a factory function to create a Movie object.

    """

    async def _make_movie(title: str, release_year: str, letterboxd_uri: str = "", watched: bool = False) -> Movie:  # noqa: FBT001, FBT002
        return await Movie.objects.acreate(title=title, release_year=release_year, letterboxd_uri=letterboxd_uri, watched=watched)

    return _make_movie
