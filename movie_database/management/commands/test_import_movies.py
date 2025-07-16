import csv
from pathlib import Path

import pytest
from django.core.management import call_command
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
    with Path.open(watched_csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["2019-10-05", "The Plague of the Zombies", "1966", "https://boxd.it/1okg"])

    call_command("import_movies", watched_csv_file)
    assert Movie.objects.count() == 1


@pytest.mark.django_db
def test_can_import_two_movies(watched_csv_file: Path):
    with Path.open(watched_csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["2019-10-05", "The Plague of the Zombies", "1966", "https://boxd.it/1okg"])
        writer.writerow(["2020-03-31", "The People Who Own the Dark", "1976", "https://boxd.it/1mtq"])

    call_command("import_movies", watched_csv_file)
    assert Movie.objects.count() == 2


@pytest.mark.django_db
def test_import_fails_when_csv_is_malformed(watched_csv_file: Path):
    with Path.open(watched_csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["The Plague of the Zombies", "1966", "https://boxd.it/1okg"])
        writer.writerow(["2020-03-31", "The People Who Own the Dark", "1976", "https://boxd.it/1mtq"])

    with pytest.raises(ValidationError):
        call_command("import_movies", watched_csv_file)
