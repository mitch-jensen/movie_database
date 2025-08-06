from typing import Annotated, Literal, TypedDict

from django.http import HttpRequest
from django.shortcuts import aget_object_or_404
from ninja import Query, Router
from ninja.pagination import paginate

from .models import MediaCaseDimensions, Movie
from .schema import MediaCaseDimensionSchemaIn, MediaCaseDimensionSchemaOut, MovieFilterSchema, MovieSchemaIn, MovieSchemaOut

router = Router()


class DefaultPostSuccessResponse(TypedDict):
    """The default success response body on a POST request."""

    id: int


class DefaultDeleteSuccessResponse(TypedDict):
    """The default success response body on a DELETE request."""

    success: Literal[True]


@router.post("/media_case_dimensions", tags=["media_case_dimensions"])
async def create_media_case_dimensions(request: HttpRequest, payload: MediaCaseDimensionSchemaIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    media_case_dimensions = await MediaCaseDimensions.objects.acreate(**payload.dict())
    return {"id": media_case_dimensions.id}


@router.get("/media_case_dimensions", response=list[MediaCaseDimensionSchemaOut], tags=["media_case_dimensions"])
@paginate
async def list_media_case_dimensions(request: HttpRequest) -> list[MediaCaseDimensionSchemaOut]:  # noqa: ARG001, D103
    media_case_dimensions = MediaCaseDimensions.objects.all()
    return [MediaCaseDimensionSchemaOut.from_orm(m) async for m in media_case_dimensions]


@router.get("/media_case_dimensions/{media_case_dimensions_id}", response=MediaCaseDimensionSchemaOut, tags=["media_case_dimensions"])
async def get_media_case_dimensions(request: HttpRequest, media_case_dimensions_id: int) -> MediaCaseDimensions:  # noqa: ARG001, D103
    media_case_dimensions: MediaCaseDimensions = await aget_object_or_404(MediaCaseDimensions, id=media_case_dimensions_id)  # pyright: ignore[reportUnknownVariableType]
    return media_case_dimensions  # pyright: ignore[reportUnknownVariableType]


@router.delete("/media_case_dimensions/{media_case_dimensions_id}", tags=["media_case_dimensions"])
async def delete_media_case_dimensions(request: HttpRequest, media_case_dimensions_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    media_case_dimensions: MediaCaseDimensions = await aget_object_or_404(MediaCaseDimensions, id=media_case_dimensions_id)  # pyright: ignore[reportUnknownVariableType]
    await media_case_dimensions.adelete()  # pyright: ignore[reportUnknownMemberType]
    return {"success": True}


@router.post("/movies", tags=["movies"])
async def create_movie(request: HttpRequest, payload: MovieSchemaIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    movie = await Movie.objects.acreate(**payload.dict())
    return {"id": movie.id}


@router.get("/movies", response=list[MovieSchemaOut], tags=["movies"])
@paginate
async def list_movies(request: HttpRequest, filters: Annotated[MovieFilterSchema, Query()]) -> list[MovieSchemaOut]:  # noqa: ARG001, D103
    movies = Movie.objects.all()
    movies = filters.filter(movies)
    return [MovieSchemaOut.from_orm(movie) async for movie in movies]


@router.get("/movies/{movie_id}", response=MovieSchemaOut, tags=["movies"])
async def get_movie(request: HttpRequest, movie_id: int) -> Movie:  # noqa: ARG001, D103
    movie: Movie = await aget_object_or_404(Movie, id=movie_id)  # pyright: ignore[reportUnknownVariableType]
    return movie  # pyright: ignore[reportUnknownVariableType]
