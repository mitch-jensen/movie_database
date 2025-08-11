import random
from collections.abc import Awaitable, Sequence
from decimal import Decimal
from typing import Protocol

import pytest_asyncio

from movie_database.models import Bookcase, Collection, MediaCaseDimension, Movie, PhysicalMedia, Shelf, ShelfDimension


class BookcaseCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        name: str,
        description: str = ...,
        location: str = ...,
    ) -> Awaitable[Bookcase]: ...


class CollectionCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        name: str,
        physical_media: Sequence[PhysicalMedia] = ...,
    ) -> Awaitable[Collection]: ...


class MediaCaseDimensionCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        media_format: MediaCaseDimension.Format = ...,
        description: str = ...,
        width: Decimal = ...,
        height: Decimal = ...,
        depth: Decimal = ...,
    ) -> Awaitable[MediaCaseDimension]: ...


class MovieCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        title: str,
        release_year: str = ...,
        letterboxd_uri: str = ...,
        watched: bool = ...,  # noqa: FBT001
    ) -> Awaitable[Movie]: ...


class PhysicalMediaCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102, PLR0913
        self,
        movies: Sequence[Movie],
        shelf: Shelf,
        position_on_shelf: int = ...,
        case_dimensions: MediaCaseDimension = ...,
        collection: Collection = ...,
        notes: str = ...,
    ) -> Awaitable[PhysicalMedia]: ...


class ShelfCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        position_from_top: int,
        bookcase: Bookcase,
        dimensions: ShelfDimension = ...,
        orientation: Shelf.Orientation = ...,
    ) -> Awaitable[Shelf]: ...


class ShelfDimensionCreator(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        width: Decimal = ...,
        height: Decimal = ...,
        depth: Decimal = ...,
    ) -> Awaitable[ShelfDimension]: ...


@pytest_asyncio.fixture
async def make_bookcase() -> BookcaseCreator:
    """Make a bookcase.

    Returns:
        BookcaseCreator: a factory function to create a Bookcase object.

    """

    async def _make_bookcase(name: str, description: str = "", location: str = "") -> Bookcase:
        return await Bookcase.objects.acreate(name=name, description=description, location=location)

    return _make_bookcase


@pytest_asyncio.fixture
async def make_collection() -> CollectionCreator:
    """Make a collection.

    Returns:
        CollectionCreator: a factory function to create a Collection object.

    """

    async def _make_collection(name: str, physical_media: Sequence[PhysicalMedia] | None = None) -> Collection:
        collection = await Collection.objects.acreate(name=name)
        if physical_media:
            await collection.physical_media_set.aadd(*physical_media)
        return collection

    return _make_collection


@pytest_asyncio.fixture
async def make_media_case_dimension() -> MediaCaseDimensionCreator:
    """Make a MediaCaseDimension object.

    Returns:
        MediaCaseDimensionCreator: a factory function to create a MediaCaseDimension object.

    """

    async def _make_media_case_dimension(
        media_format: MediaCaseDimension.Format | None = None,
        description: str | None = None,
        width: Decimal | None = None,
        height: Decimal | None = None,
        depth: Decimal | None = None,
    ) -> MediaCaseDimension:
        _media_format: MediaCaseDimension.Format = media_format or MediaCaseDimension.Format.BLURAY
        _description: str = description or "This is a description."
        _width: Decimal = width or Decimal(str(random.uniform(90.0, 128.0)))  # noqa: S311
        _height: Decimal = height or Decimal(str(random.uniform(90.0, 128.0)))  # noqa: S311
        _depth: Decimal = depth or Decimal(str(random.uniform(90.0, 128.0)))  # noqa: S311

        return await MediaCaseDimension.objects.acreate(media_format=_media_format, description=_description, width=_width, height=_height, depth=_depth)

    return _make_media_case_dimension


@pytest_asyncio.fixture
async def make_movie() -> MovieCreator:
    """Make a movie.

    Returns:
        MovieCreator: a factory function to create a Movie object.

    """

    async def _make_movie(title: str, release_year: str | None = None, letterboxd_uri: str = "", watched: bool = False) -> Movie:  # noqa: FBT001, FBT002
        _release_year: str = release_year or str(random.randint(1888, 2100))  # noqa: S311
        return await Movie.objects.acreate(title=title, release_year=_release_year, letterboxd_uri=letterboxd_uri, watched=watched)

    return _make_movie


@pytest_asyncio.fixture
async def make_physical_media(make_media_case_dimension: MediaCaseDimensionCreator, make_collection: CollectionCreator) -> PhysicalMediaCreator:
    """Make a PhysicalMedia instance.

    Returns:
        PhysicalMediaCreator: a factory function to create a PhysicalMedia object.

    """

    async def _make_physical_media(  # noqa: PLR0913
        movies: Sequence[Movie],
        shelf: Shelf,
        position_on_shelf: int | None = None,
        case_dimensions: MediaCaseDimension | None = None,
        collection: Collection | None = None,
        notes: str | None = None,
    ) -> PhysicalMedia:
        _position_on_shelf: int = position_on_shelf or 1
        _case_dimension: MediaCaseDimension = case_dimensions or await make_media_case_dimension()
        _collection: Collection = collection or await make_collection(name="R")
        _notes: str = notes or "Here are some notes."
        physical_media = await PhysicalMedia.objects.acreate(
            shelf=shelf,
            position_on_shelf=_position_on_shelf,
            case_dimensions=_case_dimension,
            collection=_collection,
            notes=_notes,
        )
        await physical_media.movies.aadd(*movies)
        return physical_media

    return _make_physical_media


@pytest_asyncio.fixture
async def make_shelf(make_shelf_dimension: ShelfDimensionCreator) -> ShelfCreator:
    """Make a shelf.

    Returns:
        ShelfCreator: a factory function to create a Shelf object.

    """

    async def _make_shelf(
        position_from_top: int,
        bookcase: Bookcase,
        dimensions: ShelfDimension | None = None,
        orientation: Shelf.Orientation | None = None,
    ) -> Shelf:
        _dimensions: ShelfDimension = dimensions or await make_shelf_dimension()
        _orientation: Shelf.Orientation = orientation or Shelf.Orientation.HORIZONTAL
        return await Shelf.objects.acreate(position_from_top=position_from_top, bookcase=bookcase, dimensions=_dimensions, orientation=_orientation)

    return _make_shelf


@pytest_asyncio.fixture
async def make_shelf_dimension() -> ShelfDimensionCreator:
    """Make a ShelfDimension object.

    Returns:
        ShelfDimensionCreator: a factory function to create a ShelfDimension object.

    """

    async def _make_shelf_dimension(width: Decimal | None = None, height: Decimal | None = None, depth: Decimal | None = None) -> ShelfDimension:
        _width: Decimal = width or Decimal(str(random.uniform(90.0, 128.0)))  # noqa: S311
        _height = height or Decimal(str(random.uniform(90.0, 128.0)))  # noqa: S311
        _depth = depth or Decimal(str(random.uniform(90.0, 128.0)))  # noqa: S311
        return await ShelfDimension.objects.acreate(width=_width, height=_height, depth=_depth)

    return _make_shelf_dimension
