from decimal import Decimal

import pytest
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from model_bakery import baker

from movie_database.models import Bookcase, Collection, MediaCaseDimensions, MediaFormat, Movie, PhysicalMedia, PhysicalMediaOrientation, Shelf, TMDbProfile
from movie_database.tests.conftest import BookcaseCreator, CollectionCreator, MediaCaseDimensionCreator, MovieCreator, PhysicalMediaCreator, ShelfCreator


class TestBookcase:
    """Test class for the Bookcase model."""

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_str_method(self, make_bookcase: BookcaseCreator):
        """Test the string representation of the Bookcase model."""
        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        assert str(bookcase) == "Test Bookcase"


class TestShelf:
    """Test class for the Shelf model."""

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_str_method(self, make_bookcase: BookcaseCreator, make_shelf: ShelfCreator):
        """Test the string representation of the Shelf model."""
        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        shelf: Shelf = await make_shelf(
            position_from_top=3,
            bookcase=bookcase,
        )
        assert str(shelf) == "Test Bookcase - 3"

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_shelf_creation(self, make_bookcase: BookcaseCreator, make_shelf: ShelfCreator):
        """Test creating a shelf."""
        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        shelf: Shelf = await make_shelf(
            position_from_top=1,
            bookcase=bookcase,
        )

        assert shelf.position_from_top == 1
        assert shelf.bookcase == bookcase
        assert str(shelf) == f"{bookcase.name} - {shelf.position_from_top}"

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_shelf_creation_with_duplicate_position(
        self,
        make_bookcase: BookcaseCreator,
        make_shelf: ShelfCreator,
    ):
        """Test creating a shelf with duplicate position."""
        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        _shelf: Shelf = await make_shelf(
            position_from_top=1,
            bookcase=bookcase,
        )

        with pytest.raises(IntegrityError):
            await Shelf.objects.acreate(position_from_top=1, bookcase=bookcase)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_shelves_with_same_position_in_different_bookcases(
        self,
        make_bookcase: BookcaseCreator,
        make_shelf: ShelfCreator,
    ):
        """Shelves with the same position should be allowed in different bookcases."""
        bookcase1: Bookcase = await make_bookcase("Test Bookcase 1")
        bookcase2: Bookcase = await make_bookcase("Test Bookcase 2")
        shelf1 = await make_shelf(position_from_top=1, bookcase=bookcase1)
        shelf2 = await make_shelf(position_from_top=1, bookcase=bookcase2)

        assert shelf1.position_from_top == 1
        assert shelf1.bookcase == bookcase1
        assert shelf1 != shelf2
        assert shelf2.position_from_top == 1
        assert shelf2.bookcase == bookcase2

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_shelf_ordering(self, make_bookcase: BookcaseCreator, make_shelf: ShelfCreator):
        """Shelves should be ordered by position_from_top by default."""
        bookcase: Bookcase = await make_bookcase("Test Bookcase")
        _shelf_1: Shelf = await make_shelf(position_from_top=3, bookcase=bookcase)
        _shelf_2: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)
        _shelf_3: Shelf = await make_shelf(position_from_top=2, bookcase=bookcase)

        positions: list[int] = [position async for position in bookcase.shelves.values_list("position_from_top", flat=True)]
        assert positions == [1, 2, 3]

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_shelf_deletion_on_bookcase_delete(self, make_bookcase: BookcaseCreator, make_shelf: ShelfCreator):
        """Deleting a bookcase should delete its shelves."""
        bookcase: Bookcase = await make_bookcase("Test Bookcase")
        _shelf_1: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)
        _shelf_2: Shelf = await make_shelf(position_from_top=2, bookcase=bookcase)

        await bookcase.adelete()
        assert await Shelf.objects.acount() == 0

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        "position_from_top",
        [-1, -5, -10],
        ids=["negative_one", "negative_five", "negative_ten"],
    )
    @pytest.mark.asyncio
    async def test_shelf_invalid_position(self, position_from_top: int, make_bookcase: BookcaseCreator):
        """Shelves should not accept zero or negative positions."""
        bookcase: Bookcase = await make_bookcase("Test Bookcase")
        with pytest.raises(IntegrityError):
            await Shelf.objects.acreate(position_from_top=position_from_top, bookcase=bookcase)


class TestShelfAccommodation:
    """Test class for accommodating PhysicalMedia on a shelf."""

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        ("media_height", "shelf_height", "should_fit"),
        [
            (127.0, 127.0, True),
            (127.0, 128.0, True),
            (127.0, 127.00001, True),
            (128.0, 127.0, False),
            (127.00001, 127.0, False),
        ],
        ids=[
            "shelf and media height equal",
            "shelf higher than media",
            "shelf higher than media by fractional margin",
            "media higher than shelf",
            "media higher than shelf by fractional margin",
        ],
    )
    @pytest.mark.asyncio
    async def test_can_fit_media_with_vertical_orientation(
        self,
        media_height: Decimal,
        shelf_height: Decimal,
        should_fit: bool,
    ):
        """Test that Shelf.can_fit_media behaves correctly for vertical orientations."""
        media: PhysicalMedia = await sync_to_async(baker.make)(PhysicalMedia, case_dimensions__height=media_height)
        shelf: Shelf = await sync_to_async(baker.make)(Shelf, dimensions__height=shelf_height, orientation=PhysicalMediaOrientation.VERTICAL)

        assert shelf.can_fit_media(media) == should_fit

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        ("media_width", "shelf_width", "should_fit"),
        [
            (127.0, 127.0, True),
            (127.0, 128.0, True),
            (127.0, 127.00001, True),
            (128.0, 127.0, False),
            (127.00001, 127.0, False),
        ],
        ids=[
            "shelf and media width equal",
            "shelf wider than media",
            "shelf wider than media by fractional margin",
            "media wider than shelf",
            "media wider than shelf by fractional margin",
        ],
    )
    @pytest.mark.asyncio
    async def test_can_fit_media_with_horizontal_orientation(self, media_width: Decimal, shelf_width: Decimal, should_fit: bool):
        """Test that Shelf.can_fit_media behaves correctly for horizontal orientations."""
        media: PhysicalMedia = await sync_to_async(baker.make)(PhysicalMedia, case_dimensions__width=media_width)
        shelf: Shelf = await sync_to_async(baker.make)(Shelf, dimensions__width=shelf_width, orientation=PhysicalMediaOrientation.HORIZONTAL)

        assert shelf.can_fit_media(media) == should_fit

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        ("shelf_height", "expected_used_space"),
        [
            (150, 0),
            (177, 0),
            (0, 0),
            (1000000, 0),
        ],
    )
    @pytest.mark.asyncio
    async def test_used_space_with_vertical_orientation_and_no_media(self, shelf_height: Decimal, expected_used_space: Decimal):
        """Test that Shelf.used_space behaves correctly with no physical media present."""
        shelf: Shelf = await sync_to_async(baker.make)(Shelf, dimensions__height=shelf_height, orientation=PhysicalMediaOrientation.VERTICAL)

        assert await shelf.used_space() == expected_used_space

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        ("shelf_width", "expected_used_space"),
        [
            (150, 0),
            (177, 0),
            (0, 0),
            (1000000, 0),
        ],
    )
    @pytest.mark.asyncio
    async def test_used_space_with_horizontal_orientation_and_no_media(self, shelf_width: Decimal, expected_used_space: Decimal):
        """Test that Shelf.used_space behaves correctly with no physical media present."""
        shelf: Shelf = await sync_to_async(baker.make)(Shelf, dimensions__width=shelf_width, orientation=PhysicalMediaOrientation.HORIZONTAL)

        assert await shelf.used_space() == expected_used_space

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        ("shelf_height", "media_heights", "expected_used_space"),
        [
            (150, [10], 10),
            (150, [10, 20, 30], 60),
            (150, [127.27], Decimal("127.27")),
            (150, [127.27, 10.78], Decimal("138.05")),
        ],
    )
    @pytest.mark.asyncio
    async def test_used_space_with_vertical_orientation_and_media_present(
        self,
        shelf_height: Decimal,
        media_heights: list[Decimal],
        expected_used_space: Decimal,
    ):
        """Test that Shelf.used_space is always the sum of physical media widths varying numbers of physical media present."""
        media: list[PhysicalMedia] = [await sync_to_async(baker.make)(PhysicalMedia, case_dimensions__height=media_width) for media_width in media_heights]
        shelf: Shelf = await sync_to_async(baker.make)(Shelf, dimensions__height=shelf_height, orientation=PhysicalMediaOrientation.VERTICAL)
        await shelf.physical_media_set.aadd(*media)

        assert await shelf.used_space() == expected_used_space

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        ("shelf_width", "media_widths", "expected_used_space"),
        [
            (150, [10], 10),
            (150, [10, 20, 30], 60),
            (150, [127.27], Decimal("127.27")),
            (150, [127.27, 10.78], Decimal("138.05")),
        ],
    )
    @pytest.mark.asyncio
    async def test_used_space_with_horizontal_orientation_and_media_present(
        self,
        shelf_width: Decimal,
        media_widths: list[Decimal],
        expected_used_space: Decimal,
    ):
        """Test that Shelf.used_space is always the sum of physical media widths varying numbers of physical media present."""
        media: list[PhysicalMedia] = [await sync_to_async(baker.make)(PhysicalMedia, case_dimensions__width=media_width) for media_width in media_widths]
        shelf: Shelf = await sync_to_async(baker.make)(Shelf, dimensions__width=shelf_width, orientation=PhysicalMediaOrientation.HORIZONTAL)
        await shelf.physical_media_set.aadd(*media)

        assert await shelf.used_space() == expected_used_space


class TestMediaCaseDimension:
    """Test class for the MediaCaseDimensions model."""

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_str_method(self, make_media_case_dimensions: MediaCaseDimensionCreator):
        """Test the string representation of the MediaCaseDimensions model."""
        dimensions = await make_media_case_dimensions(
            media_format=MediaFormat.DVD,
            description="DVD (Standard)",
            width=Decimal("100.01"),
            height=Decimal("101.00"),
            depth=Decimal("102.10"),
        )
        assert str(dimensions) == "100.01W x 101.00H x 102.10D"

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_bluray_us_standard_exists(self):
        """Test if the Blu-ray US Standard dimensions exist."""
        assert await MediaCaseDimensions.objects.filter(
            media_format=MediaFormat.BLURAY,
            description="Blu-ray (US Standard)",
            width=128.50,
            height=148.00,
            depth=12.00,
        ).aexists()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_bluray_uk_standard_exists(self):
        """Test if the Blu-ray UK Standard dimensions exist."""
        assert await MediaCaseDimensions.objects.filter(
            media_format=MediaFormat.BLURAY,
            description="Blu-ray (UK Standard)",
            width=148.00,
            height=129.00,
            depth=14.00,
        ).aexists()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_dvd_standard_exists(self):
        """Test if the DVD Standard dimensions exist."""
        assert await MediaCaseDimensions.objects.filter(
            media_format=MediaFormat.DVD,
            description="DVD (Standard)",
            width=130.00,
            height=184.00,
            depth=14.00,
        ).aexists()


class TestPhysicalMedia:
    """Test class for the PhysicalMedia model."""

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_str_method_one_movie(
        self,
        make_bookcase: BookcaseCreator,
        make_movie: MovieCreator,
        make_physical_media: PhysicalMediaCreator,
        make_shelf: ShelfCreator,
    ):
        """Test the string representation of the PhysicalMedia model."""
        movie: Movie = await make_movie(title="Test Movie", release_year="1967")
        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        shelf: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)
        media: PhysicalMedia = await make_physical_media(movies=[movie], shelf=shelf)
        assert await sync_to_async(str)(media) == "Test Movie (1967)"

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_str_method_multiple_movies(
        self,
        make_bookcase: BookcaseCreator,
        make_movie: MovieCreator,
        make_physical_media: PhysicalMediaCreator,
        make_shelf: ShelfCreator,
    ):
        """Test the string representation of the PhysicalMedia model with multiple movies."""
        movie_1: Movie = await make_movie(title="Movie 1", release_year="1943")
        movie_2: Movie = await make_movie(title="Movie 2", release_year="1983")

        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        shelf: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)
        media: PhysicalMedia = await make_physical_media(movies=[movie_1, movie_2], shelf=shelf)

        assert await sync_to_async(str)(media) == "Movie 1 (1943), Movie 2 (1983)"

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_physical_media_can_have_multiple_movies(
        self,
        make_bookcase: BookcaseCreator,
        make_movie: MovieCreator,
        make_physical_media: PhysicalMediaCreator,
        make_shelf: ShelfCreator,
    ):
        """Test that a PhysicalMedia can have multiple movies."""
        movie_1: Movie = await make_movie(title="Movie 1")
        movie_2: Movie = await make_movie(title="Movie 2")

        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        shelf: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)
        media: PhysicalMedia = await make_physical_media(movies=[movie_1, movie_2], shelf=shelf)

        assert await media.movies.acount() == 2
        assert await media.movies.filter(title="Movie 1").aexists()
        assert await media.movies.filter(title="Movie 2").aexists()

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_physical_media_can_have_shelf(
        self,
        make_bookcase: BookcaseCreator,
        make_movie: MovieCreator,
        make_physical_media: PhysicalMediaCreator,
        make_shelf: ShelfCreator,
    ):
        """Test that a PhysicalMedia can have a shelf."""
        movie: Movie = await make_movie(title="Test Movie")
        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        shelf: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)
        media: PhysicalMedia = await make_physical_media(movies=[movie], shelf=shelf)

        assert media.shelf is not None
        assert media.shelf == shelf
        assert media.shelf.bookcase is not None
        assert media.shelf.bookcase == bookcase

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_position_on_shelf_is_unique_within_one_shelf(
        self,
        make_bookcase: BookcaseCreator,
        make_movie: MovieCreator,
        make_physical_media: PhysicalMediaCreator,
        make_shelf: ShelfCreator,
    ):
        """Test that the position on a shelf is unique."""
        movie1: Movie = await make_movie(title="Movie 1")
        movie2: Movie = await make_movie(title="Movie 2")
        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        shelf: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)
        _media1: PhysicalMedia = await make_physical_media(movies=[movie1], shelf=shelf, position_on_shelf=1)

        with pytest.raises(IntegrityError):
            _media2: PhysicalMedia = await make_physical_media(
                movies=[movie2],
                shelf=shelf,
                position_on_shelf=1,
            )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_position_on_shelf_can_be_same_in_different_shelves(
        self,
        make_bookcase: BookcaseCreator,
        make_movie: MovieCreator,
        make_physical_media: PhysicalMediaCreator,
        make_shelf: ShelfCreator,
    ):
        """Test that the position on a shelf can be the same in different shelves."""
        movie1: Movie = await make_movie(title="Movie 1")
        movie2: Movie = await make_movie(title="Movie 2")
        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        shelf1: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)
        shelf2: Shelf = await make_shelf(position_from_top=2, bookcase=bookcase)
        media1: PhysicalMedia = await make_physical_media(movies=[movie1], shelf=shelf1, position_on_shelf=1)
        media2: PhysicalMedia = await make_physical_media(movies=[movie2], shelf=shelf2, position_on_shelf=1)

        assert media1.position_on_shelf == 1
        assert media2.position_on_shelf == 1


class TestCollection:
    """Test class for the Collection model."""

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_str_method(self, make_collection: CollectionCreator):
        """Test the string representation of the Collection model."""
        collection: Collection = await make_collection(name="Test Collection")
        assert str(collection) == "Test Collection"

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_collection_can_have_multiple_physical_media(
        self,
        make_bookcase: BookcaseCreator,
        make_collection: CollectionCreator,
        make_movie: MovieCreator,
        make_physical_media: PhysicalMediaCreator,
        make_shelf: ShelfCreator,
    ):
        """Test creating a collection."""
        movie_1: Movie = await make_movie("Movie 1")
        movie_2: Movie = await make_movie("Movie 2")

        bookcase: Bookcase = await make_bookcase("Test Bookcase")
        shelf: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)

        physical_media1: PhysicalMedia = await make_physical_media(movies=[movie_1], shelf=shelf, position_on_shelf=1)
        physical_media2: PhysicalMedia = await make_physical_media(movies=[movie_2], shelf=shelf, position_on_shelf=2)

        collection: Collection = await make_collection(name="Test Collection", physical_media=[physical_media1, physical_media2])

        assert collection.name == "Test Collection"
        assert await collection.physical_media_set.acount() == 2
        assert [m async for m in collection.get_movies()] == [movie_1, movie_2]

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_collection_can_have_physical_media_with_multiple_movies(
        self,
        make_bookcase: BookcaseCreator,
        make_collection: CollectionCreator,
        make_movie: MovieCreator,
        make_physical_media: PhysicalMediaCreator,
        make_shelf: ShelfCreator,
    ):
        """Test that a collection can have multiple physical media."""
        movie1: Movie = await make_movie(title="Movie 1")
        movie2: Movie = await make_movie(title="Movie 2")
        movie3: Movie = await make_movie(title="Movie 3")
        movie4: Movie = await make_movie(title="Movie 4")
        movie5: Movie = await make_movie(title="Movie 5")

        bookcase: Bookcase = await make_bookcase(name="Test Bookcase")
        shelf: Shelf = await make_shelf(position_from_top=1, bookcase=bookcase)
        physical_media1: PhysicalMedia = await make_physical_media(shelf=shelf, movies=[movie1, movie2, movie3], position_on_shelf=1)
        physical_media2: PhysicalMedia = await make_physical_media(shelf=shelf, movies=[movie3, movie4, movie5], position_on_shelf=2)
        collection: Collection = await make_collection(name="Test Collection", physical_media=[physical_media1, physical_media2])

        assert await collection.physical_media_set.acount() == 2
        assert await collection.get_movies().acount() == 5


class TestTMDbProfile:
    """Test class for the TMDbProfile model."""

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_str_method(self, make_movie: MovieCreator):
        """Test the string representation of the TMDbProfile model."""
        movie: Movie = await make_movie(title="Test Movie")
        tmdb_profile: TMDbProfile = await TMDbProfile.objects.acreate(movie=movie, tmdb_id=12345)
        assert str(tmdb_profile) == "Test Movie"

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_cannot_add_duplicate_tmdb_id(self, make_movie: MovieCreator):
        """Test that a TMDbProfile cannot have duplicate tmdb_id."""
        movie1: Movie = await make_movie(title="Movie 1")
        movie2: Movie = await make_movie(title="Movie 2")
        _tmdb_profile: TMDbProfile = await TMDbProfile.objects.acreate(movie=movie1, tmdb_id=12345)

        with pytest.raises(IntegrityError):
            _tmdb_profile_2 = await TMDbProfile.objects.acreate(movie=movie2, tmdb_id=12345)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_tmdb_profile_uniqueness_per_movie(self, make_movie: MovieCreator):
        """Test that a TMDbProfile is unique per movie."""
        movie: Movie = await make_movie(title="Movie 1")
        _tmdb_profile1: TMDbProfile = await TMDbProfile.objects.acreate(movie=movie, tmdb_id=12345)

        with pytest.raises(IntegrityError):
            _tmdb_profile2 = await TMDbProfile.objects.acreate(movie=movie, tmdb_id=67890)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_tmdb_profile_delete_on_movie_delete(self, make_movie: MovieCreator):
        """Test that deleting a movie deletes its TMDbProfile."""
        movie: Movie = await make_movie(title="Test Movie")
        _tmdb_profile = await TMDbProfile.objects.acreate(movie=movie, tmdb_id=12345)

        assert await TMDbProfile.objects.filter(movie=movie).aexists()

        await movie.adelete()

        assert not await TMDbProfile.objects.aexists()


class TestMovie:
    """Test class for the Movie model."""

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_str_method(self, make_movie: MovieCreator):
        """Test the string representation of the Movie model."""
        movie: Movie = await make_movie(title="Test Movie", release_year="1977")
        assert str(movie) == "Test Movie (1977)"
