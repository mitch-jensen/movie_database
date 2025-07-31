import csv
from argparse import ArgumentParser
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
from django.core.management.base import BaseCommand
from pydantic import BaseModel, ConfigDict, Field

from movie_database.models import Movie

logger = structlog.get_logger()


class ImportMovie(BaseModel):
    """Represents a movie to be imported into the database."""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)
    title: str
    release_year: int
    letterboxd_uri: str
    watched: bool


class WatchedEntry(BaseModel):
    """Represents a single entry in the watched.csv file."""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)
    date: datetime = Field(alias="Date")
    name: str = Field(alias="Name")
    year: int = Field(alias="Year")
    uri: str = Field(alias="Letterboxd URI")


class Command(BaseCommand):
    """Command to import watched movies from Letterboxd's watched.csv file."""

    help = "Import watched movies from Letterboxd's watched.csv export"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command line arguments to manage.py command."""
        parser.add_argument("csv_file", help="Path to watched.csv file")

    def handle(self, *args: Any, **options: str) -> None:  # noqa: ANN401, ARG002
        """Handle the command to import watched movies."""
        csv_file: Path = Path(options["csv_file"])

        if not csv_file.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file}"))
            return

        movies = self.get_movies_from_csv(csv_file)

        if not movies:
            logger.warning("CSV file was empty.")
            self.stdout.write(self.style.WARNING("No movies found in file."))
            return

        self.add_or_update_movies(movies)

    def get_movies_from_csv(self, csv_file: Path) -> list[WatchedEntry]:
        """Parse movies into WatchedEntry Pydantic model.

        Args:
            csv_file (Path): path to CSV file exported from Letterboxd containing movies.

        Returns:
            list[WatchedEntry]: list of movies as WatchedEntry objects.

        """
        with csv_file.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            return [WatchedEntry.model_validate(row) for row in reader]

    def add_or_update_movies(self, entries: Iterable[WatchedEntry]) -> None:
        """Add new movies from the import file that don't already exist in the database, updating the watched status of any that do already exist.

        Args:
            entries (Iterable[WatchedEntry]): iterable containing entries in the watched.csv file.

        """
        movies = {ImportMovie(title=e.name, release_year=e.year, letterboxd_uri=e.uri, watched=True) for e in entries}

        Movie.objects.bulk_create(
            [Movie(**m.model_dump()) for m in movies],
            update_conflicts=True,
            update_fields=["watched"],
            unique_fields=["title", "release_year", "letterboxd_uri"],
        )
