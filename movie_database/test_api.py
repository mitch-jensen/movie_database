import pytest
from django.test import AsyncClient

from .models import Movie


@pytest.fixture
@pytest.mark.django_db
async def make_movie():
    async def _make_movie(title: str, release_year: str):
        return await Movie.objects.acreate(title=title, release_year=release_year)

    return _make_movie


class TestListMovies:
    """Test the list_movies API endpoint."""

    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_no_movies(self, async_client: AsyncClient):
        """Test listing movies when there are no movies in the database."""
        response = await async_client.get("/api/v1/movie_database/movies")

        assert response.status_code == 200

        data = response.json()
        assert data == {"items": [], "count": 0}

    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_multiple_movies(self, async_client: AsyncClient, make_movie):
        """Test listing all movies."""
        movie1 = await make_movie("Movie 1", "2021")
        movie2 = await make_movie("Movie 2", "2022")
        movie3 = await make_movie("Movie 3", "2023")
        movie4 = await make_movie("Movie 4", "2024")
        movie5 = await make_movie("Movie 5", "2025")

        response = await async_client.get("/api/v1/movie_database/movies")

        assert response.status_code == 200

        data = response.json()
        assert data == {
            "items": [
                {"id": movie1.pk, "title": "Movie 1", "release_year": 2021, "watched": movie1.watched, "letterboxd_uri": movie1.letterboxd_uri},
                {"id": movie2.pk, "title": "Movie 2", "release_year": 2022, "watched": movie2.watched, "letterboxd_uri": movie2.letterboxd_uri},
                {"id": movie3.pk, "title": "Movie 3", "release_year": 2023, "watched": movie3.watched, "letterboxd_uri": movie3.letterboxd_uri},
                {"id": movie4.pk, "title": "Movie 4", "release_year": 2024, "watched": movie4.watched, "letterboxd_uri": movie4.letterboxd_uri},
                {"id": movie5.pk, "title": "Movie 5", "release_year": 2025, "watched": movie5.watched, "letterboxd_uri": movie5.letterboxd_uri},
            ],
            "count": 5,
        }
