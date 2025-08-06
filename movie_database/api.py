from typing import Annotated, Literal, TypedDict

from django.http import HttpRequest
from django.shortcuts import aget_object_or_404
from ninja import Query, Router

from .models import Bookcase, Collection, MediaCaseDimensions, Movie, ShelfDimensions
from .schema import (
    BookcaseSchemaIn,
    BookcaseSchemaOut,
    CollectionSchemaIn,
    CollectionSchemaOut,
    MediaCaseDimensionSchemaIn,
    MediaCaseDimensionSchemaOut,
    MovieFilterSchema,
    MovieSchemaIn,
    MovieSchemaOut,
    PhysicalMediaSchema,
    ShelfDimensionSchemaIn,
    ShelfDimensionSchemaOut,
    ShelfSchemaOut,
)

router = Router()


class DefaultPostSuccessResponse(TypedDict):
    """The default success response body on a POST request."""

    id: int


class DefaultDeleteSuccessResponse(TypedDict):
    """The default success response body on a DELETE request."""

    success: Literal[True]


@router.post("/bookcases", tags=["bookcase"])
async def create_bookcase(request: HttpRequest, payload: BookcaseSchemaIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    bookcase = await Bookcase.objects.acreate(**payload.dict())
    return {"id": bookcase.id}


@router.get("/bookcases", response=list[BookcaseSchemaOut], tags=["bookcase"])
async def list_bookcases(request: HttpRequest) -> list[BookcaseSchemaOut]:  # noqa: ARG001, D103
    bookcase = Bookcase.objects.all()
    return [BookcaseSchemaOut.from_orm(m) async for m in bookcase]


@router.get("/bookcases/{bookcase_id}", response=BookcaseSchemaOut, tags=["bookcase"])
async def get_bookcase(request: HttpRequest, bookcase_id: int) -> Bookcase:  # noqa: ARG001, D103
    bookcase: Bookcase = await aget_object_or_404(Bookcase, id=bookcase_id)  # pyright: ignore[reportUnknownVariableType]
    return bookcase  # pyright: ignore[reportUnknownVariableType]


@router.get("/bookcases/{bookcase_id}/shelves", response=list[ShelfSchemaOut], tags=["bookcase", "shelf"])
async def get_bookcase_shelves(request: HttpRequest, bookcase_id: int) -> list[ShelfSchemaOut]:  # noqa: ARG001, D103
    bookcase: Bookcase = await aget_object_or_404(Bookcase, id=bookcase_id)  # pyright: ignore[reportUnknownVariableType]
    return [ShelfSchemaOut.from_orm(shelf) async for shelf in bookcase.shelves.all()]


@router.delete("/bookcases/{bookcase_id}", tags=["bookcase"])
async def delete_bookcase(request: HttpRequest, bookcase_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    bookcase: Bookcase = await aget_object_or_404(Bookcase, id=bookcase_id)  # pyright: ignore[reportUnknownVariableType]
    await bookcase.adelete()  # pyright: ignore[reportUnknownMemberType]
    return {"success": True}


@router.post("/collections", tags=["collection"])
async def create_collection(request: HttpRequest, payload: CollectionSchemaIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    collection = await Collection.objects.acreate(**payload.dict())
    return {"id": collection.id}


@router.get("/collections", response=list[CollectionSchemaOut], tags=["collection"])
async def list_collections(request: HttpRequest) -> list[CollectionSchemaOut]:  # noqa: ARG001, D103
    collection = Collection.objects.all()
    return [CollectionSchemaOut.from_orm(m) async for m in collection]


@router.get("/collections/{collection_id}", response=CollectionSchemaOut, tags=["collection"])
async def get_collection(request: HttpRequest, collection_id: int) -> Collection:  # noqa: ARG001, D103
    collection: Collection = await aget_object_or_404(Collection, id=collection_id)  # pyright: ignore[reportUnknownVariableType]
    return collection  # pyright: ignore[reportUnknownVariableType]


@router.get("/collections/{collection_id}/media", response=list[PhysicalMediaSchema], tags=["collection", "physical_media"])
async def get_collection_media_list(request: HttpRequest, collection_id: int) -> list[ShelfSchemaOut]:  # noqa: ARG001, D103
    collection: Collection = await aget_object_or_404(Collection, id=collection_id)  # pyright: ignore[reportUnknownVariableType]
    return [PhysicalMediaSchema.from_orm(shelf) async for shelf in collection.physical_media_set.all()]


@router.get("/collections/{collection_id}/media/{media_id}", response=PhysicalMediaSchema, tags=["collection", "physical_media"])
async def get_collection_media(request: HttpRequest, collection_id: int, media_id: int) -> ShelfSchemaOut:  # noqa: ARG001, D103
    collection: Collection = await aget_object_or_404(Collection, id=collection_id)  # pyright: ignore[reportUnknownVariableType]
    return collection.physical_media_set.aget(id=media_id)


@router.delete("/collections/{collection_id}", tags=["collection"])
async def delete_collection(request: HttpRequest, collection_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    collection: Collection = await aget_object_or_404(Collection, id=collection_id)  # pyright: ignore[reportUnknownVariableType]
    await collection.adelete()  # pyright: ignore[reportUnknownMemberType]
    return {"success": True}


@router.post("/media_case_dimensions", tags=["media_case_dimensions"])
async def create_media_case_dimensions(request: HttpRequest, payload: MediaCaseDimensionSchemaIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    media_case_dimensions = await MediaCaseDimensions.objects.acreate(**payload.dict())
    return {"id": media_case_dimensions.id}


@router.get("/media_case_dimensions", response=list[MediaCaseDimensionSchemaOut], tags=["media_case_dimensions"])
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


@router.post("/shelf_dimensions", tags=["shelf_dimensions"])
async def create_shelf_dimensions(request: HttpRequest, payload: ShelfDimensionSchemaIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    shelf_dimensions = await ShelfDimensions.objects.acreate(**payload.dict())
    return {"id": shelf_dimensions.id}


@router.get("/shelf_dimensions", response=list[ShelfDimensionSchemaOut], tags=["shelf_dimensions"])
async def list_shelf_dimensions(request: HttpRequest) -> list[ShelfDimensionSchemaOut]:  # noqa: ARG001, D103
    shelf_dimensions = ShelfDimensions.objects.all()
    return [ShelfDimensionSchemaOut.from_orm(m) async for m in shelf_dimensions]


@router.get("/shelf_dimensions/{shelf_dimensions_id}", response=ShelfDimensionSchemaOut, tags=["shelf_dimensions"])
async def get_shelf_dimensions(request: HttpRequest, shelf_dimensions_id: int) -> ShelfDimensions:  # noqa: ARG001, D103
    shelf_dimensions: ShelfDimensions = await aget_object_or_404(ShelfDimensions, id=shelf_dimensions_id)  # pyright: ignore[reportUnknownVariableType]
    return shelf_dimensions  # pyright: ignore[reportUnknownVariableType]


@router.delete("/shelf_dimensions/{shelf_dimensions_id}", tags=["shelf_dimensions"])
async def delete_shelf_dimensions(request: HttpRequest, shelf_dimensions_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    shelf_dimensions: ShelfDimensions = await aget_object_or_404(ShelfDimensions, id=shelf_dimensions_id)  # pyright: ignore[reportUnknownVariableType]
    await shelf_dimensions.adelete()  # pyright: ignore[reportUnknownMemberType]
    return {"success": True}


@router.post("/movies", tags=["movies"])
async def create_movie(request: HttpRequest, payload: MovieSchemaIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    movie = await Movie.objects.acreate(**payload.dict())
    return {"id": movie.id}


@router.get("/movies", response=list[MovieSchemaOut], tags=["movies"])
async def list_movies(request: HttpRequest, filters: Annotated[MovieFilterSchema, Query()]) -> list[MovieSchemaOut]:  # noqa: ARG001, D103
    movies = Movie.objects.all()
    movies = filters.filter(movies)
    return [MovieSchemaOut.from_orm(movie) async for movie in movies]


@router.get("/movies/{movie_id}", response=MovieSchemaOut, tags=["movies"])
async def get_movie(request: HttpRequest, movie_id: int) -> Movie:  # noqa: ARG001, D103
    movie: Movie = await aget_object_or_404(Movie, id=movie_id)  # pyright: ignore[reportUnknownVariableType]
    return movie  # pyright: ignore[reportUnknownVariableType]


@router.get("/movies/{movie_id}/physical_media", response=list[PhysicalMediaSchema], tags=["movies", "physical_media"])
async def get_movie_physical_media(request: HttpRequest, movie_id: int) -> list[PhysicalMediaSchema]:  # noqa: ARG001, D103
    movie: Movie = await aget_object_or_404(Movie, id=movie_id)  # pyright: ignore[reportUnknownVariableType]
    return [PhysicalMediaSchema.from_orm(medium) async for medium in movie.physical_media_set.all()]
