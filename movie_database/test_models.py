import pytest
from django.db import IntegrityError
from model_bakery import baker

from .models import MediaCaseDimensions, Movie, Shelf


@pytest.fixture
def movie():
    """Fixture for baked Movie model."""
    return baker.make(Movie)


@pytest.mark.django_db
def test_using_movie(movie: Movie):
    """Test function using fixture of baked model."""
    assert isinstance(movie, Movie)


class TestShelf:
    """Test class for the Shelf model."""

    @pytest.mark.django_db
    def test_shelf_creation(self):
        """Test creating a shelf."""
        bookcase = baker.make("Bookcase")
        shelf = Shelf.objects.create(
            position_from_top=1,
            bookcase=bookcase,
        )

        assert shelf.position_from_top == 1
        assert shelf.bookcase == bookcase
        assert str(shelf) == f"<Shelf: {shelf.bookcase.name} - {shelf.position_from_top}>"

    @pytest.mark.django_db
    def test_shelf_creation_with_duplicate_position(self):
        """Test creating a shelf with duplicate position."""
        bookcase = baker.make("Bookcase")
        Shelf.objects.create(position_from_top=1, bookcase=bookcase)

        with pytest.raises(IntegrityError):
            Shelf.objects.create(position_from_top=1, bookcase=bookcase)

    @pytest.mark.django_db
    def test_shelves_with_same_position_in_different_bookcases(self):
        """Shelves with the same position should be allowed in different bookcases."""
        bookcase1 = baker.make("Bookcase")
        bookcase2 = baker.make("Bookcase")
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
        bookcase = baker.make("Bookcase")
        Shelf.objects.create(position_from_top=3, bookcase=bookcase)
        Shelf.objects.create(position_from_top=1, bookcase=bookcase)
        Shelf.objects.create(position_from_top=2, bookcase=bookcase)

        positions = list(bookcase.shelves.values_list("position_from_top", flat=True))
        assert positions == [1, 2, 3]

    @pytest.mark.django_db
    def test_shelf_deletion_on_bookcase_delete(self):
        """Deleting a bookcase should delete its shelves."""
        bookcase = baker.make("Bookcase")
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
        bookcase = baker.make("Bookcase")
        with pytest.raises(IntegrityError):
            Shelf.objects.create(position_from_top=position_from_top, bookcase=bookcase)


class TestMediaCaseDimension:
    """Test class for the MediaCaseDimensions model."""

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
