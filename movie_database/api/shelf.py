from django.http import HttpRequest
from django.shortcuts import aget_object_or_404
from ninja.pagination import RouterPaginated

import movie_database.schema as schemas
from movie_database.api.responses import DefaultDeleteSuccessResponse, DefaultPostSuccessResponse
from movie_database.models import Shelf, ShelfDimension

router = RouterPaginated(tags=["Shelf"])


@router.post("/")
async def create_shelf(request: HttpRequest, payload: schemas.ShelfIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    shelf_dimension = await Shelf.objects.acreate(**payload.dict())
    return {"id": shelf_dimension.id}


@router.get("/", response=list[schemas.ShelfOut])
async def list_shelves(request: HttpRequest) -> list[schemas.ShelfOut]:  # noqa: ARG001, D103
    shelf_dimensions = Shelf.objects.all()
    return [schemas.ShelfOut.from_orm(m) async for m in shelf_dimensions]


@router.get("/{shelf_id}", response=schemas.ShelfOut)
async def get_shelf(request: HttpRequest, shelf_id: int) -> Shelf:  # noqa: ARG001, D103
    return await aget_object_or_404(Shelf, id=shelf_id)


@router.get("/{shelf_id}/dimensions", response=schemas.ShelfDimensionOut, tags=["Shelf", "Dimension"])
async def get_shelf_dimension(request: HttpRequest, shelf_id: int) -> ShelfDimension:  # noqa: ARG001, D103
    shelf = await aget_object_or_404(Shelf, id=shelf_id)
    return shelf.dimensions


@router.delete("/{shelf_id}")
async def delete_shelf(request: HttpRequest, shelf_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    shelf_dimension = await aget_object_or_404(Shelf, id=shelf_id)
    await shelf_dimension.adelete()
    return {"success": True}
