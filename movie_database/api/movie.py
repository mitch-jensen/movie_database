from typing import Annotated

from django.http import HttpRequest
from django.shortcuts import aget_object_or_404
from ninja import Query
from ninja.pagination import RouterPaginated

import movie_database.schema as schemas
from movie_database.api.responses import DefaultPostSuccessResponse
from movie_database.models import Movie

router = RouterPaginated(tags=["Movie"])


@router.post("/")
async def create_movie(request: HttpRequest, payload: schemas.MovieIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    movie = await Movie.objects.acreate(**payload.dict())
    return {"id": movie.id}


@router.get("/", response=list[schemas.MovieOut])
async def list_movies(request: HttpRequest, filters: Annotated[schemas.MovieFilter, Query(...)]) -> list[schemas.MovieOut]:  # noqa: ARG001, D103
    movies = Movie.objects.all()
    movies = filters.filter(movies)
    return [schemas.MovieOut.from_orm(movie) async for movie in movies]


@router.get("/{movie_id}", response=schemas.MovieOut)
async def get_movie(request: HttpRequest, movie_id: int) -> Movie:  # noqa: ARG001, D103
    return await aget_object_or_404(Movie, id=movie_id)


@router.get("/{movie_id}/physical_media", response=list[schemas.PhysicalMediaOut], tags=["Movie", "Physical Media"])
async def get_movie_physical_media(request: HttpRequest, movie_id: int) -> list[schemas.PhysicalMediaOut]:  # noqa: ARG001, D103
    movie: Movie = await aget_object_or_404(Movie, id=movie_id)
    return [schemas.PhysicalMediaOut.from_orm(medium) async for medium in movie.physical_media_set.all()]
