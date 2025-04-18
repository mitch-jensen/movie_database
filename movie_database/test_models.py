import pytest
from django.db import IntegrityError
from model_bakery import baker

from .models import Bookcase, MediaCaseDimensions, Movie, PhysicalMedia, Shelf


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
        bookcase = Bookcase.objects.create(name="Test Bookcase")
        shelf = Shelf.objects.create(
            position_from_top=3,
            bookcase=bookcase,
        )
        assert str(shelf) == "<Shelf: Test Bookcase - 3>"

    @pytest.mark.django_db
    def test_shelf_creation(self):
        """Test creating a shelf."""
        bookcase: Bookcase = baker.make("Bookcase")
        shelf = Shelf.objects.create(
            position_from_top=1,
            bookcase=bookcase,
        )

        assert shelf.position_from_top == 1
        assert shelf.bookcase == bookcase
        assert str(shelf) == f"<Shelf: {bookcase.name} - {shelf.position_from_top}>"

    @pytest.mark.django_db
    def test_shelf_creation_with_duplicate_position(self):
        """Test creating a shelf with duplicate position."""
        bookcase: Bookcase = baker.make("Bookcase")
        Shelf.objects.create(position_from_top=1, bookcase=bookcase)

        with pytest.raises(IntegrityError):
            Shelf.objects.create(position_from_top=1, bookcase=bookcase)

    @pytest.mark.django_db
    def test_shelves_with_same_position_in_different_bookcases(self):
        """Shelves with the same position should be allowed in different bookcases."""
        bookcase1: Bookcase = baker.make("Bookcase")
        bookcase2: Bookcase = baker.make("Bookcase")
        shelf1 = Shelf.objects.create(position_from_top=1, bookcase=bookcase1)
        shelf2 = Shelf.objects.create(position_from_top=1, bookcase=bookcase2)

        assert shelf1.position_from_top == 1
        assert shelf1.bookcase == bookcase1
        assert shelf1 != shelf2
        assert shelf2.position_from_top == 1
        assert shelf2.bookcase == bookcase2

    @pytest.mark.django_db
    def test_shelf_ordering(self):
        """Shelves should be ordered by position_from_top by default."""
        bookcase: Bookcase = baker.make("Bookcase")
        Shelf.objects.create(position_from_top=3, bookcase=bookcase)
        Shelf.objects.create(position_from_top=1, bookcase=bookcase)
        Shelf.objects.create(position_from_top=2, bookcase=bookcase)

        positions: list[int] = list(bookcase.shelves.values_list("position_from_top", flat=True))
        assert positions == [1, 2, 3]

    @pytest.mark.django_db
    def test_shelf_deletion_on_bookcase_delete(self):
        """Deleting a bookcase should delete its shelves."""
        bookcase: Bookcase = baker.make("Bookcase")
        Shelf.objects.create(position_from_top=1, bookcase=bookcase)
        Shelf.objects.create(position_from_top=2, bookcase=bookcase)

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
        with pytest.raises(IntegrityError):
            Shelf.objects.create(position_from_top=position_from_top, bookcase=bookcase)


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
