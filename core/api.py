from ninja import NinjaAPI
from ninja.pagination import RouterPaginated

from movie_database.api import router as movie_db_router

api = NinjaAPI(default_router=RouterPaginated())

api.add_router("/movie_database/", movie_db_router)
