from django.http import HttpRequest
from django.shortcuts import aget_object_or_404
from ninja.pagination import RouterPaginated

import movie_database.schema as schemas
from movie_database.api.responses import DefaultDeleteSuccessResponse, DefaultPostSuccessResponse
from movie_database.models import MediaCaseDimension, PhysicalMedia

router = RouterPaginated(tags=["Physical Media"])


@router.post("/")
async def create_physical_media(request: HttpRequest, payload: schemas.PhysicalMediaIn) -> DefaultPostSuccessResponse:  # noqa: ARG001, D103
    physical_media = await PhysicalMedia.objects.acreate(**payload.dict())
    return {"id": physical_media.id}


@router.get("/", response=list[schemas.PhysicalMediaOut])
async def list_physical_medias(request: HttpRequest) -> list[schemas.PhysicalMediaOut]:  # noqa: ARG001, D103
    physical_medias = PhysicalMedia.objects.all()
    return [schemas.PhysicalMediaOut.from_orm(m) async for m in physical_medias]


@router.get("/{physical_media_id}", response=schemas.PhysicalMediaOut)
async def get_physical_media(request: HttpRequest, physical_media_id: int) -> PhysicalMedia:  # noqa: ARG001, D103
    return await aget_object_or_404(PhysicalMedia, id=physical_media_id)


@router.get("/{physical_media_id}/dimension", response=schemas.MediaCaseDimensionOut, tags=["Physical Media", "Dimension"])
async def get_physical_media_dimension(request: HttpRequest, physical_media_id: int) -> MediaCaseDimension:  # noqa: ARG001, D103
    physical_media = await aget_object_or_404(PhysicalMedia, id=physical_media_id)
    return physical_media.dimensions


@router.delete("/{physical_media_id}")
async def delete_physical_media(request: HttpRequest, physical_media_id: int) -> DefaultDeleteSuccessResponse:  # noqa: ARG001, D103
    physical_media = await aget_object_or_404(PhysicalMedia, id=physical_media_id)
    await physical_media.adelete()
    return {"success": True}
