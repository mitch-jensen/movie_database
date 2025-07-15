import pytest
from django.db import IntegrityError
from model_bakery import baker

from .models import Bookcase, Collection, MediaCaseDimensions, Movie, PhysicalMedia, Shelf, ShelfDimensions, TMDbProfile


class TestBookcase:
    """Test class for the Bookcase model."""

    @pytest.mark.django_db
    def test_str_method(self):
        """Test the string representation of the Bookcase model."""
        bookcase = Bookcase.objects.create(name="Test Bookcase")
        assert str(bookcase) == "<Bookcase: Test Bookcase>"


class TestShelf:
    """Test class for the Shelf model."""

    @pytest.mark.django_db
    def test_str_method(self):
        """Test the string representation of the Shelf model."""
        bookcase: Bookcase = baker.make(Bookcase, name="Test Bookcase")
        dimensions: ShelfDimensions = baker.make(ShelfDimensions)
        shelf = Shelf.objects.create(
            position_from_top=3,
            bookcase=bookcase,
            dimensions=dimensions,
        )
        assert str(shelf) == "<Shelf: Test Bookcase - 3>"

    @pytest.mark.django_db
    def test_shelf_creation(self):
        """Test creating a shelf."""
        bookcase: Bookcase = baker.make("Bookcase")
        dimensions: ShelfDimensions = baker.make(ShelfDimensions)
        shelf = Shelf.objects.create(
            position_from_top=1,
            bookcase=bookcase,
            dimensions=dimensions,
        )

        assert shelf.position_from_top == 1
        assert shelf.bookcase == bookcase
        assert str(shelf) == f"<Shelf: {bookcase.name} - {shelf.position_from_top}>"

    @pytest.mark.django_db
    def test_shelf_creation_with_duplicate_position(self):
        """Test creating a shelf with duplicate position."""
        bookcase: Bookcase = baker.make("Bookcase")
        dimensions: ShelfDimensions = baker.make(ShelfDimensions)
        Shelf.objects.create(
            position_from_top=1,
            bookcase=bookcase,
            dimensions=dimensions,
        )

        with pytest.raises(IntegrityError):
            Shelf.objects.create(position_from_top=1, bookcase=bookcase)

    @pytest.mark.django_db
    def test_shelves_with_same_position_in_different_bookcases(self):
        """Shelves with the same position should be allowed in different bookcases."""
        bookcase1: Bookcase = baker.make("Bookcase")
        bookcase2: Bookcase = baker.make("Bookcase")
        dimensions: ShelfDimensions = baker.make(ShelfDimensions)
        shelf1 = Shelf.objects.create(position_from_top=1, bookcase=bookcase1, dimensions=dimensions)
        shelf2 = Shelf.objects.create(position_from_top=1, bookcase=bookcase2, dimensions=dimensions)

        assert shelf1.position_from_top == 1
        assert shelf1.bookcase == bookcase1
        assert shelf1 != shelf2
        assert shelf2.position_from_top == 1
        assert shelf2.bookcase == bookcase2

    @pytest.mark.django_db
    def test_shelf_ordering(self):
        """Shelves should be ordered by position_from_top by default."""
        bookcase: Bookcase = baker.make("Bookcase")
        dimensions: ShelfDimensions = baker.make(ShelfDimensions)
        Shelf.objects.create(position_from_top=3, bookcase=bookcase, dimensions=dimensions)
        Shelf.objects.create(position_from_top=1, bookcase=bookcase, dimensions=dimensions)
        Shelf.objects.create(position_from_top=2, bookcase=bookcase, dimensions=dimensions)

        positions: list[int] = list(bookcase.shelves.values_list("position_from_top", flat=True))
        assert positions == [1, 2, 3]

    @pytest.mark.django_db
    def test_shelf_deletion_on_bookcase_delete(self):
        """Deleting a bookcase should delete its shelves."""
        bookcase: Bookcase = baker.make("Bookcase")
        dimensions: ShelfDimensions = baker.make(ShelfDimensions)
        Shelf.objects.create(position_from_top=1, bookcase=bookcase, dimensions=dimensions)
        Shelf.objects.create(position_from_top=2, bookcase=bookcase, dimensions=dimensions)

        bookcase.delete()
        assert Shelf.objects.count() == 0

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "position_from_top",
        [-1, -5, -10],
        ids=["negative_one", "negative_five", "negative_ten"],
    )
    def test_shelf_invalid_position(self, position_from_top: int):
        """Shelves should not accept zero or negative positions."""
        bookcase: Bookcase = baker.make("Bookcase")
        dimensions: ShelfDimensions = baker.make(ShelfDimensions)
        with pytest.raises(IntegrityError):
            Shelf.objects.create(position_from_top=position_from_top, bookcase=bookcase, dimensions=dimensions)


class TestShelfAccommodation:
    """Test class for accommodating PhysicalMedia on a shelf."""


class TestMediaCaseDimension:
    """Test class for the MediaCaseDimensions model."""

    @pytest.mark.django_db
    def test_str_method(self):
        """Test the string representation of the MediaCaseDimensions model."""
        dimensions = MediaCaseDimensions(
            media_format="DVD",
            description="DVD (Standard)",
            width=100.01,
            height=101.00,
            depth=102.10,
        )
        assert str(dimensions) == "<MediaCaseDimensions (DVD): 100.01 x 101.00 x 102.10>"

    @pytest.mark.django_db
    def test_bluray_us_standard_exists(self):
        """Test if the Blu-ray US Standard dimensions exist."""
        assert MediaCaseDimensions.objects.filter(
            media_format="Blu-ray",
            description="Blu-ray (US Standard)",
            width=128.50,
            height=148.00,
            depth=12.00,
        ).exists()

    @pytest.mark.django_db
    def test_bluray_uk_standard_exists(self):
        """Test if the Blu-ray UK Standard dimensions exist."""
        assert MediaCaseDimensions.objects.filter(
            media_format="Blu-ray",
            description="Blu-ray (UK Standard)",
            width=148.00,
            height=129.00,
            depth=14.00,
        ).exists()

    @pytest.mark.django_db
    def test_dvd_standard_exists(self):
        """Test if the DVD Standard dimensions exist."""
        assert MediaCaseDimensions.objects.filter(
            media_format="DVD",
            description="DVD (Standard)",
            width=130.00,
            height=184.00,
            depth=14.00,
        ).exists()


class TestPhysicalMedia:
    """Test class for the PhysicalMedia model."""

    @pytest.mark.django_db
    def test_str_method_one_movie(self):
        """Test the string representation of the PhysicalMedia model."""
        movie: Movie = baker.make("Movie", title="Test Movie")
        media: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie])
        assert str(media) == "<PhysicalMedia: Test Movie>"

    @pytest.mark.django_db
    def test_str_method_multiple_movies(self):
        """Test the string representation of the PhysicalMedia model with multiple movies."""
        movie1: Movie = baker.make("Movie", title="Movie 1")
        movie2: Movie = baker.make("Movie", title="Movie 2")
        media: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie1, movie2])
        assert str(media) == "<PhysicalMedia: Movie 1, Movie 2>"

    @pytest.mark.django_db
    def test_physical_media_can_have_multiple_movies(self):
        """Test that a PhysicalMedia can have multiple movies."""
        movie1: Movie = baker.make("Movie", title="Movie 1")
        movie2: Movie = baker.make("Movie", title="Movie 2")
        media: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie1, movie2])

        assert media.movies.count() == 2
        assert media.movies.filter(title="Movie 1").exists()
        assert media.movies.filter(title="Movie 2").exists()

    @pytest.mark.django_db
    def test_physical_media_can_have_shelf(self):
        """Test that a PhysicalMedia can have a shelf."""
        movie: Movie = baker.make("Movie", title="Test Movie")
        bookcase: Bookcase = baker.make("Bookcase", name="Test Bookcase")
        shelf: Shelf = baker.make("Shelf", position_from_top=1, bookcase=bookcase)
        media: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie], shelf=shelf)

        assert media.shelf == shelf
        assert media.shelf.bookcase == bookcase

    @pytest.mark.django_db
    def test_position_on_shelf_is_unique_within_one_shelf(self):
        """Test that the position on a shelf is unique."""
        movie1: Movie = baker.make("Movie", title="Movie 1")
        movie2: Movie = baker.make("Movie", title="Movie 2")
        bookcase: Bookcase = baker.make("Bookcase", name="Test Bookcase")
        shelf: Shelf = baker.make("Shelf", position_from_top=1, bookcase=bookcase)
        _media1: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie1], shelf=shelf, position_on_shelf=1)

        with pytest.raises(IntegrityError):
            _media2: PhysicalMedia = baker.make(
                "PhysicalMedia",
                movies=[movie2],
                shelf=shelf,
                position_on_shelf=1,
            )

    @pytest.mark.django_db
    def test_position_on_shelf_can_be_same_in_different_shelves(self):
        """Test that the position on a shelf can be the same in different shelves."""
        movie1: Movie = baker.make("Movie", title="Movie 1")
        movie2: Movie = baker.make("Movie", title="Movie 2")
        bookcase: Bookcase = baker.make("Bookcase", name="Test Bookcase")
        shelf1: Shelf = baker.make("Shelf", position_from_top=1, bookcase=bookcase)
        shelf2: Shelf = baker.make("Shelf", position_from_top=2, bookcase=bookcase)
        media1: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie1], shelf=shelf1, position_on_shelf=1)
        media2: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie2], shelf=shelf2, position_on_shelf=1)

        assert media1.position_on_shelf == 1
        assert media2.position_on_shelf == 1


class TestCollection:
    """Test class for the Collection model."""

    @pytest.mark.django_db
    def test_str_method(self):
        """Test the string representation of the Collection model."""
        collection = Collection.objects.create(name="Test Collection")
        assert str(collection) == "<Collection: Test Collection>"

    @pytest.mark.django_db
    def test_collection_can_have_physical_media(self):
        """Test creating a collection."""
        movie1 = baker.make("Movie", title="Movie 1")
        movie2 = baker.make("Movie", title="Movie 2")
        physical_media1: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie1])
        physical_media2: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie2])
        collection = Collection.objects.create(name="Test Collection")
        collection.physical_media.add(physical_media1, physical_media2)

        assert collection.name == "Test Collection"
        assert collection.physical_media.count() == 2
        assert collection.movies.count() == 2
        assert list(collection.movies.values_list("title", flat=True)) == ["Movie 1", "Movie 2"]

    @pytest.mark.django_db
    def test_collection_can_have_physical_media_with_multiple_movies(self):
        """Test that a collection can have multiple physical media."""
        movie1: Movie = baker.make("Movie", title="Movie 1")
        movie2: Movie = baker.make("Movie", title="Movie 2")
        movie3: Movie = baker.make("Movie", title="Movie 3")
        movie4: Movie = baker.make("Movie", title="Movie 4")
        movie5: Movie = baker.make("Movie", title="Movie 5")
        physical_media1: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie1, movie2, movie3])
        physical_media2: PhysicalMedia = baker.make("PhysicalMedia", movies=[movie3, movie4, movie5])
        collection = Collection.objects.create(name="Test Collection")
        collection.physical_media.add(physical_media1, physical_media2)

        assert collection.physical_media.count() == 2
        assert collection.movies.count() == 6
        assert collection.movies.distinct().count() == 5
        assert list(collection.movies.distinct().values_list("title", flat=True)) == [
            "Movie 1",
            "Movie 2",
            "Movie 3",
            "Movie 4",
            "Movie 5",
        ]


class TestTMDbProfile:
    """Test class for the TMDbProfile model."""

    @pytest.mark.django_db
    def test_str_method(self):
        """Test the string representation of the TMDbProfile model."""
        movie: Movie = baker.make("Movie", title="Test Movie")
        tmdb_profile = TMDbProfile.objects.create(movie=movie, tmdb_id=12345)
        assert str(tmdb_profile) == "<TMDbProfile: 12345 - Test Movie>"

    @pytest.mark.django_db
    def test_cannot_add_duplicate_tmdb_id(self):
        """Test that a TMDbProfile cannot have duplicate tmdb_id."""
        movie1: Movie = baker.make("Movie", title="Movie 1")
        movie2: Movie = baker.make("Movie", title="Movie 2")
        TMDbProfile.objects.create(movie=movie1, tmdb_id=12345)

        with pytest.raises(IntegrityError):
            TMDbProfile.objects.create(movie=movie2, tmdb_id=12345)

    @pytest.mark.django_db
    def test_tmdb_profile_uniqueness_per_movie(self):
        """Test that a TMDbProfile is unique per movie."""
        movie: Movie = baker.make("Movie", title="Movie 1")
        _tmdb_profile1 = TMDbProfile.objects.create(movie=movie, tmdb_id=12345)

        with pytest.raises(IntegrityError):
            _tmdb_profile2 = TMDbProfile.objects.create(movie=movie, tmdb_id=67890)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "is_adult",
        [True, False],
        ids=["adult", "not_adult"],
    )
    def test_tmdb_profile_adult_flag(self, is_adult: bool):
        """Test the adult flag in TMDbProfile."""
        movie: Movie = baker.make("Movie", title="Test Movie")
        tmdb_profile = TMDbProfile.objects.create(movie=movie, tmdb_id=12345, adult=is_adult)

        assert tmdb_profile.adult == is_adult

    @pytest.mark.django_db
    def test_tmdb_profile_delete_on_movie_delete(self):
        """Test that deleting a movie deletes its TMDbProfile."""
        movie: Movie = baker.make("Movie", title="Test Movie")
        _tmdb_profile = TMDbProfile.objects.create(movie=movie, tmdb_id=12345)

        assert TMDbProfile.objects.filter(movie=movie).exists()

        movie.delete()

        assert not TMDbProfile.objects.exists()


class TestMovie:
    """Test class for the Movie model."""

    @pytest.mark.django_db
    def test_str_method(self):
        """Test the string representation of the Movie model."""
        movie = Movie.objects.create(title="Test Movie", release_year=1998)
        assert str(movie) == "<Movie: Test Movie (1998)>"
