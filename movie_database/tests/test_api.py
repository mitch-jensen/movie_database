from typing import TYPE_CHECKING

import pytest
from django.test.client import AsyncClient

from movie_database.tests.conftest import MovieCreator

if TYPE_CHECKING:
    from django.http import HttpResponse

    from movie_database.models import Movie


class TestListMovies:
    """Test the list_movies API endpoint."""

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_no_movies(self, async_client: AsyncClient):
        """Test listing movies when there are no movies in the database."""
        response: HttpResponse = await async_client.get("/api/v1/movie_database/movies/?limit=100&offset=0")

        assert response.status_code == 200
        assert response.json() == {"items": [], "count": 0}

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_multiple_movies(self, async_client: AsyncClient, make_movie: MovieCreator):
        """Test listing all movies."""
        movie1: Movie = await make_movie("Movie 1", "2021")
        movie2: Movie = await make_movie("Movie 2", "2022")
        movie3: Movie = await make_movie("Movie 3", "2023")
        movie4: Movie = await make_movie("Movie 4", "2024")
        movie5: Movie = await make_movie("Movie 5", "2025")

        response: HttpResponse = await async_client.get("/api/v1/movie_database/movies/?limit=100&offset=0")

        assert response.status_code == 200

        assert response.json() == {
            "items": [
                {"id": movie1.pk, "title": "Movie 1", "release_year": 2021, "watched": movie1.watched, "letterboxd_uri": movie1.letterboxd_uri},
                {"id": movie2.pk, "title": "Movie 2", "release_year": 2022, "watched": movie2.watched, "letterboxd_uri": movie2.letterboxd_uri},
                {"id": movie3.pk, "title": "Movie 3", "release_year": 2023, "watched": movie3.watched, "letterboxd_uri": movie3.letterboxd_uri},
                {"id": movie4.pk, "title": "Movie 4", "release_year": 2024, "watched": movie4.watched, "letterboxd_uri": movie4.letterboxd_uri},
                {"id": movie5.pk, "title": "Movie 5", "release_year": 2025, "watched": movie5.watched, "letterboxd_uri": movie5.letterboxd_uri},
            ],
            "count": 5,
        }
