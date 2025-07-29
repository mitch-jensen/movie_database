from typing import Annotated

from django.http import HttpRequest
from ninja import Query, Router
from ninja.pagination import paginate

from .models import Movie
from .schema import MovieFilterSchema, MovieSchema

router = Router()


@router.get("/movies", response=list[MovieSchema])
@paginate
async def list_movies(request: HttpRequest, filters: Annotated[MovieFilterSchema, Query()]) -> list[MovieSchema]:  # noqa: ARG001
    """List all movies in the database."""
    movies = Movie.objects.all()
    movies = filters.filter(movies)
    return [MovieSchema.from_orm(movie) async for movie in movies]
