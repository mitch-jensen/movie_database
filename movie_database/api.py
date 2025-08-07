from typing import Annotated, Literal, TypedDict

from django.http import HttpRequest
from django.shortcuts import aget_object_or_404
from ninja import Query, Router

import movie_database.schema as schemas

from .models import Bookcase, Collection, MediaCaseDimension, Movie, PhysicalMedia, ShelfDimension

router = Router()


class DefaultPostSuccessResponse(TypedDict):
    """The default success response body on a POST request."""

    id: int


class DefaultDeleteSuccessResponse(TypedDict):
    """The default success response body on a DELETE request."""

    success: Literal[True]


@router.post("/bookcases", tags=["bookcase"])
async def create_bookcase(request: HttpRequest, payload: schemas.BookcaseIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    bookcase = await Bookcase.objects.acreate(**payload.dict())
    return {"id": bookcase.id}


@router.get("/bookcases", response=list[schemas.BookcaseOut], tags=["bookcase"])
async def list_bookcases(request: HttpRequest) -> list[schemas.BookcaseOut]:  # noqa: ARG001, D103
    bookcase = Bookcase.objects.all()
    return [schemas.BookcaseOut.from_orm(m) async for m in bookcase]


@router.get("/bookcases/{bookcase_id}", response=schemas.BookcaseOut, tags=["bookcase"])
async def get_bookcase(request: HttpRequest, bookcase_id: int) -> Bookcase:  # noqa: ARG001, D103
    return await aget_object_or_404(Bookcase, id=bookcase_id)


@router.get("/bookcases/{bookcase_id}/shelves", response=list[schemas.ShelfOut], tags=["bookcase", "shelf"])
async def get_bookcase_shelves(request: HttpRequest, bookcase_id: int) -> list[schemas.ShelfOut]:  # noqa: ARG001, D103
    bookcase = await aget_object_or_404(Bookcase, id=bookcase_id)
    return [schemas.ShelfOut.from_orm(shelf) async for shelf in bookcase.shelves.all()]


@router.delete("/bookcases/{bookcase_id}", tags=["bookcase"])
async def delete_bookcase(request: HttpRequest, bookcase_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    bookcase = await aget_object_or_404(Bookcase, id=bookcase_id)
    await bookcase.adelete()
    return {"success": True}


@router.post("/collections", tags=["collection"])
async def create_collection(request: HttpRequest, payload: schemas.CollectionIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    collection = await Collection.objects.acreate(**payload.dict())
    return {"id": collection.id}


@router.get("/collections", response=list[schemas.CollectionOut], tags=["collection"])
async def list_collections(request: HttpRequest) -> list[schemas.CollectionOut]:  # noqa: ARG001, D103
    collection = Collection.objects.all()
    return [schemas.CollectionOut.from_orm(m) async for m in collection]


@router.get("/collections/{collection_id}", response=schemas.CollectionOut, tags=["collection"])
async def get_collection(request: HttpRequest, collection_id: int) -> Collection:  # noqa: ARG001, D103
    return await aget_object_or_404(Collection, id=collection_id)


@router.get("/collections/{collection_id}/media", response=list[schemas.PhysicalMedia], tags=["collection", "physical_media"])
async def get_collection_media_list(request: HttpRequest, collection_id: int) -> list[schemas.PhysicalMedia]:  # noqa: ARG001, D103
    collection = await aget_object_or_404(Collection, id=collection_id)
    return [schemas.PhysicalMedia.from_orm(shelf) async for shelf in collection.physical_media_set.all()]


@router.get("/collections/{collection_id}/media/{media_id}", response=schemas.PhysicalMedia, tags=["collection", "physical_media"])
async def get_collection_media(request: HttpRequest, collection_id: int, media_id: int) -> PhysicalMedia:  # noqa: ARG001, D103
    collection: Collection = await aget_object_or_404(Collection, id=collection_id)
    return await collection.physical_media_set.aget(id=media_id)


@router.delete("/collections/{collection_id}", tags=["collection"])
async def delete_collection(request: HttpRequest, collection_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    collection = await aget_object_or_404(Collection, id=collection_id)
    await collection.adelete()
    return {"success": True}


@router.post("/media_case_dimensions", tags=["media_case_dimension"])
async def create_media_case_dimension(request: HttpRequest, payload: schemas.MediaCaseDimensionIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    media_case_dimension = await MediaCaseDimension.objects.acreate(**payload.dict())
    return {"id": media_case_dimension.id}


@router.get("/media_case_dimensions", response=list[schemas.MediaCaseDimensionOut], tags=["media_case_dimension"])
async def list_media_case_dimensions(request: HttpRequest) -> list[schemas.MediaCaseDimensionOut]:  # noqa: ARG001, D103
    media_case_dimensions = MediaCaseDimension.objects.all()
    return [schemas.MediaCaseDimensionOut.from_orm(m) async for m in media_case_dimensions]


@router.get("/media_case_dimensions/{media_case_dimension_id}", response=schemas.MediaCaseDimensionOut, tags=["media_case_dimension"])
async def get_media_case_dimension(request: HttpRequest, media_case_dimension_id: int) -> MediaCaseDimension:  # noqa: ARG001, D103
    return await aget_object_or_404(MediaCaseDimension, id=media_case_dimension_id)


@router.delete("/media_case_dimensions/{media_case_dimension_id}", tags=["media_case_dimension"])
async def delete_media_case_dimension(request: HttpRequest, media_case_dimension_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    media_case_dimension = await aget_object_or_404(MediaCaseDimension, id=media_case_dimension_id)
    await media_case_dimension.adelete()
    return {"success": True}


@router.post("/shelf_dimensions", tags=["shelf_dimension"])
async def create_shelf_dimension(request: HttpRequest, payload: schemas.ShelfDimensionIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    shelf_dimension = await ShelfDimension.objects.acreate(**payload.dict())
    return {"id": shelf_dimension.id}


@router.get("/shelf_dimensions", response=list[schemas.ShelfDimensionOut], tags=["shelf_dimension"])
async def list_shelf_dimensions(request: HttpRequest) -> list[schemas.ShelfDimensionOut]:  # noqa: ARG001, D103
    shelf_dimensions = ShelfDimension.objects.all()
    return [schemas.ShelfDimensionOut.from_orm(m) async for m in shelf_dimensions]


@router.get("/shelf_dimensions/{shelf_dimension_id}", response=schemas.ShelfDimensionOut, tags=["shelf_dimension"])
async def get_shelf_dimension(request: HttpRequest, shelf_dimension_id: int) -> ShelfDimension:  # noqa: ARG001, D103
    return await aget_object_or_404(ShelfDimension, id=shelf_dimension_id)


@router.delete("/shelf_dimensions/{shelf_dimension_id}", tags=["shelf_dimension"])
async def delete_shelf_dimension(request: HttpRequest, shelf_dimension_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    shelf_dimension = await aget_object_or_404(ShelfDimension, id=shelf_dimension_id)
    await shelf_dimension.adelete()
    return {"success": True}


@router.post("/movies", tags=["movies"])
async def create_movie(request: HttpRequest, payload: schemas.MovieIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    movie = await Movie.objects.acreate(**payload.dict())
    return {"id": movie.id}


@router.get("/movies", response=list[schemas.MovieOut], tags=["movies"])
async def list_movies(request: HttpRequest, filters: Annotated[schemas.MovieFilter, Query(...)]) -> list[schemas.MovieOut]:  # noqa: ARG001, D103
    movies = Movie.objects.all()
    movies = filters.filter(movies)
    return [schemas.MovieOut.from_orm(movie) async for movie in movies]


@router.get("/movies/{movie_id}", response=schemas.MovieOut, tags=["movies"])
async def get_movie(request: HttpRequest, movie_id: int) -> Movie:  # noqa: ARG001, D103
    return await aget_object_or_404(Movie, id=movie_id)


@router.get("/movies/{movie_id}/physical_media", response=list[schemas.PhysicalMedia], tags=["movies", "physical_media"])
async def get_movie_physical_media(request: HttpRequest, movie_id: int) -> list[schemas.PhysicalMedia]:  # noqa: ARG001, D103
    movie: Movie = await aget_object_or_404(Movie, id=movie_id)
    return [schemas.PhysicalMedia.from_orm(medium) async for medium in movie.physical_media_set.all()]
