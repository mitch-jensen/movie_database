from ninja.pagination import RouterPaginated

from .bookcase import router as bookcase_router
from .collection import router as collection_router
from .movie import router as movie_router
from .physical_media import router as physical_media_router
from .shelf import router as shelf_router

router = RouterPaginated()
router.add_router("bookcase/", bookcase_router)
router.add_router("collection/", collection_router)
router.add_router("movies/", movie_router)
router.add_router("physical_media/", physical_media_router)
router.add_router("shelves/", shelf_router)
