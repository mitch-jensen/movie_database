from ninja import NinjaAPI

from movie_database.api import router as movie_router

api = NinjaAPI()

api.add_router("/movie_database/", movie_router)
