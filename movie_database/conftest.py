from collections.abc import Awaitable, Callable

import pytest

from movie_database.models import Movie

type MovieCreator = Callable[[str, str, str, bool], Awaitable[Movie]]


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
