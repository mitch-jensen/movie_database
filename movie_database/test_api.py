import pytest
from django.test import Client
from model_bakery import baker
from pytest_django import DjangoAssertNumQueries

from .models import Movie


class TestListMovies:
    """Test the list_movies API endpoint."""

    @pytest.mark.django_db
    def test_no_movies(self, client: Client, django_assert_num_queries: DjangoAssertNumQueries):
        """Test listing movies when there are no movies in the database."""
        # Make a GET request to the list_movies endpoint
        with django_assert_num_queries(2) as captured:
            response = client.get("/api/v1/movie_database/movies")

        # Check the response status code
        assert response.status_code == 200

        # Check the response data
        data = response.json()
        assert data == {"items": [], "count": 0}
        assert len(captured) == 2

    @pytest.mark.django_db
    def test_multiple_movies(self, client: Client, django_assert_num_queries: DjangoAssertNumQueries):
        """Test listing all movies."""
        # Create some test movies
        movie1 = baker.make(Movie, title="Movie 1", release_year="2021")
        movie2 = baker.make(Movie, title="Movie 2", release_year="2022")
        movie3 = baker.make(Movie, title="Movie 3", release_year="2023")
        movie4 = baker.make(Movie, title="Movie 4", release_year="2024")
        movie5 = baker.make(Movie, title="Movie 5", release_year="2025")

        # Make a GET request to the list_movies endpoint
        with django_assert_num_queries(2):
            response = client.get("/api/v1/movie_database/movies")

        # Check the response status code
        assert response.status_code == 200

        # Check the response data
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
