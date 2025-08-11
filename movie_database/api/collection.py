from django.http import HttpRequest
from django.shortcuts import aget_object_or_404
from ninja.pagination import RouterPaginated

import movie_database.schema as schemas
from movie_database.api.responses import DefaultDeleteSuccessResponse, DefaultPostSuccessResponse
from movie_database.models import Collection, PhysicalMedia

router = RouterPaginated(tags=["Collection"])


@router.post("/")
async def create_collection(request: HttpRequest, payload: schemas.CollectionIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    collection = await Collection.objects.acreate(**payload.dict())
    return {"id": collection.id}


@router.get("/", response=list[schemas.CollectionOut])
async def list_collections(request: HttpRequest) -> list[schemas.CollectionOut]:  # noqa: ARG001, D103
    collection = Collection.objects.all()
    return [schemas.CollectionOut.from_orm(m) async for m in collection]


@router.get("/{collection_id}", response=schemas.CollectionOut)
async def get_collection(request: HttpRequest, collection_id: int) -> Collection:  # noqa: ARG001, D103
    return await aget_object_or_404(Collection, id=collection_id)


@router.get("/{collection_id}/media", response=list[schemas.PhysicalMediaOut], tags=["Collection", "Physical Media"])
async def get_collection_media_list(request: HttpRequest, collection_id: int) -> list[schemas.PhysicalMediaOut]:  # noqa: ARG001, D103
    collection = await aget_object_or_404(Collection, id=collection_id)
    return [schemas.PhysicalMediaOut.from_orm(shelf) async for shelf in collection.physical_media_set.all()]


@router.get("/{collection_id}/media/{media_id}", response=schemas.PhysicalMediaOut, tags=["Collection", "Physical Media"])
async def get_collection_media(request: HttpRequest, collection_id: int, media_id: int) -> PhysicalMedia:  # noqa: ARG001, D103
    collection: Collection = await aget_object_or_404(Collection, id=collection_id)
    return await collection.physical_media_set.aget(id=media_id)


@router.delete("/{collection_id}")
async def delete_collection(request: HttpRequest, collection_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    collection = await aget_object_or_404(Collection, id=collection_id)
    await collection.adelete()
    return {"success": True}
