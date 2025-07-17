import csv
from pathlib import Path

import pytest
from django.core.management import call_command
from model_bakery import baker
from pydantic import ValidationError

from movie_database.models import Movie


@pytest.fixture
def watched_csv_file(tmp_path: Path) -> Path:
    file = tmp_path / "watched.csv"
    with Path.open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Name", "Year", "Letterboxd URI"])
    return file


@pytest.mark.django_db
def test_no_failures_on_empty_csv_file(watched_csv_file: Path):
    call_command("import_movies", watched_csv_file)
    assert Movie.objects.count() == 0


@pytest.mark.django_db
def test_can_import_single_movie(watched_csv_file: Path):
    title = "The Plague of the Zombies"
    year = 1966
    letterboxd_uri = "https://boxd.it/1okg"

    with Path.open(watched_csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["2019-10-05", title, year, letterboxd_uri])

    call_command("import_movies", watched_csv_file)
    assert Movie.objects.count() == 1

    movie: Movie = Movie.objects.first()
    assert movie.title == title
    assert movie.release_year == year
    assert movie.letterboxd_uri == letterboxd_uri


@pytest.mark.django_db
def test_duplicate_import_only_imports_once(watched_csv_file: Path):
    """Test that the same movie appearing in the csv file twice only imports once."""
    title = "The Plague of the Zombies"
    year = 1966
    letterboxd_uri = "https://boxd.it/1okg"

    with Path.open(watched_csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["2019-10-05", title, year, letterboxd_uri])
        writer.writerow(["2019-10-06", title, year, letterboxd_uri])

    call_command("import_movies", watched_csv_file)
    assert Movie.objects.count() == 1

    movie: Movie = Movie.objects.first()
    assert movie.title == title
    assert movie.release_year == year
    assert movie.letterboxd_uri == letterboxd_uri


@pytest.mark.django_db
def test_can_import_two_movies(watched_csv_file: Path):
    title_1 = "The Plague of the Zombies"
    year_1 = 1966
    letterboxd_uri_1 = "https://boxd.it/1okg"

    title_2 = "The People Who Own the Dark"
    year_2 = 1976
    letterboxd_uri_2 = "https://boxd.it/1mtq"

    with Path.open(watched_csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["2019-10-05", title_1, year_1, letterboxd_uri_1])
        writer.writerow(["2020-03-31", title_2, year_2, letterboxd_uri_2])

    call_command("import_movies", watched_csv_file)
    assert Movie.objects.count() == 2

    movie_1 = Movie.objects.get(title=title_1)
    assert movie_1.release_year == year_1
    assert movie_1.letterboxd_uri == letterboxd_uri_1

    movie_2 = Movie.objects.get(title=title_2)
    assert movie_2.release_year == year_2
    assert movie_2.letterboxd_uri == letterboxd_uri_2


@pytest.mark.django_db
def test_running_same_import_twice_is_idempotent(watched_csv_file: Path):
    title_1 = "The Plague of the Zombies"
    year_1 = 1966
    letterboxd_uri_1 = "https://boxd.it/1okg"

    title_2 = "The People Who Own the Dark"
    year_2 = 1976
    letterboxd_uri_2 = "https://boxd.it/1mtq"

    with Path.open(watched_csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["2019-10-05", title_1, year_1, letterboxd_uri_1])
        writer.writerow(["2020-03-31", title_2, year_2, letterboxd_uri_2])

    # Run import twice
    call_command("import_movies", watched_csv_file)
    call_command("import_movies", watched_csv_file)

    # Assert that all the same conditions expected from a single run are still true
    assert Movie.objects.count() == 2

    movie_1 = Movie.objects.get(title=title_1)
    assert movie_1.release_year == year_1
    assert movie_1.letterboxd_uri == letterboxd_uri_1

    movie_2 = Movie.objects.get(title=title_2)
    assert movie_2.release_year == year_2
    assert movie_2.letterboxd_uri == letterboxd_uri_2


@pytest.mark.django_db
def test_import_fails_when_csv_is_malformed(watched_csv_file: Path):
    with Path.open(watched_csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["The Plague of the Zombies", "1966", "https://boxd.it/1okg"])
        writer.writerow(["2020-03-31", "The People Who Own the Dark", "1976", "https://boxd.it/1mtq"])

    with pytest.raises(ValidationError):
        call_command("import_movies", watched_csv_file)

    assert Movie.objects.count() == 0


@pytest.mark.django_db
def test_importing_movies_updates_watched_status(watched_csv_file: Path):
    """Test that a movie that already exists in the databased with an unwatched status gets changed to watched upon import."""
    # TODO @mitch-jensen: have the import be more general and not depend on importing the watched movies only.  # noqa: FIX002, TD003

    title = "Test Movie"
    release_year = "1987"
    letterboxd_uri = "https://boxd.it/1okg"
    watched_date = "2020-03-31"

    movie: Movie = baker.make(Movie, title=title, release_year=release_year, letterboxd_uri=letterboxd_uri, watched=False)

    with Path.open(watched_csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([watched_date, title, release_year, letterboxd_uri])

    call_command("import_movies", watched_csv_file)
    movie.refresh_from_db()
    assert movie.watched
