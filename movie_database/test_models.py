import pytest
from model_bakery import baker

from .models import Movie


@pytest.fixture
def movie():
    """Fixture for baked Movie model."""
    return baker.make(Movie)


@pytest.mark.django_db
def test_using_movie(movie: Movie):
    """Test function using fixture of baked model."""
    assert isinstance(movie, Movie)
