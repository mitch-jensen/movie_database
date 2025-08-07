from django.http import HttpRequest
from django.shortcuts import aget_object_or_404
from ninja.pagination import RouterPaginated

import movie_database.schema as schemas
from movie_database.api.responses import DefaultDeleteSuccessResponse, DefaultPostSuccessResponse
from movie_database.models import Bookcase

router = RouterPaginated(tags=["Bookcase"])


@router.post("/")
async def create_bookcase(request: HttpRequest, payload: schemas.BookcaseIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    bookcase = await Bookcase.objects.acreate(**payload.dict())
    return {"id": bookcase.id}


@router.get("/", response=list[schemas.BookcaseOut])
async def list_bookcases(request: HttpRequest) -> list[schemas.BookcaseOut]:  # noqa: ARG001, D103
    bookcase = Bookcase.objects.all()
    return [schemas.BookcaseOut.from_orm(m) async for m in bookcase]


@router.get("/{bookcase_id}", response=schemas.BookcaseOut)
async def get_bookcase(request: HttpRequest, bookcase_id: int) -> Bookcase:  # noqa: ARG001, D103
    return await aget_object_or_404(Bookcase, id=bookcase_id)


@router.get("/{bookcase_id}/shelves", response=list[schemas.ShelfOut], tags=["Bookcase", "Shelf"])
async def get_bookcase_shelves(request: HttpRequest, bookcase_id: int) -> list[schemas.ShelfOut]:  # noqa: ARG001, D103
    bookcase = await aget_object_or_404(Bookcase, id=bookcase_id)
    return [schemas.ShelfOut.from_orm(shelf) async for shelf in bookcase.shelves.all()]


@router.delete("/{bookcase_id}")
async def delete_bookcase(request: HttpRequest, bookcase_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    bookcase = await aget_object_or_404(Bookcase, id=bookcase_id)
    await bookcase.adelete()
    return {"success": True}
