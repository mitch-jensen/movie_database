from django.http import HttpRequest
from ninja import Router

from .models import Movie
from .schema import MovieSchema

router = Router()


@router.get("/", response=list[MovieSchema])
def list_movies(request: HttpRequest) -> list[MovieSchema]:  # noqa: ARG001
    """List all movies in the database."""
    return Movie.objects.all()
