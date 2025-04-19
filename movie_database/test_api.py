import pytest
from django.test import Client
from model_bakery import baker
from pytest_django import DjangoAssertNumQueries

from .models import Movie


class TestListMovies:
    """Test the list_movies API endpoint."""

    @pytest.mark.django_db
    def test_list_movies(self, client: Client, django_assert_num_queries: DjangoAssertNumQueries):
        """Test listing all movies."""
        # Create some test movies
        movie1 = baker.make(Movie, title="Movie 1", release_year="2021")
        movie2 = baker.make(Movie, title="Movie 2", release_year="2022")

        # Make a GET request to the list_movies endpoint
        with django_assert_num_queries(1):
            response = client.get("/api/v1/movies/")

        # Check the response status code
        assert response.status_code == 200

        # Check the response data
        data = response.json()
        assert len(data) == 2
        assert data == [
            {"id": movie1.id, "title": "Movie 1", "release_year": 2021},
            {"id": movie2.id, "title": "Movie 2", "release_year": 2022},
        ]
