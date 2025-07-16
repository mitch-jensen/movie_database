import csv
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Q
from pydantic import BaseModel, Field

from movie_database.models import Movie


class WatchedEntry(BaseModel):
    """Represents a single entry in the watched.csv file."""

    date: datetime = Field(alias="Date")
    name: str = Field(alias="Name")
    year: int = Field(alias="Year")
    uri: str = Field(alias="Letterboxd URI")

    def normalized_key(self) -> tuple[str, int]:
        """Generate a normalized key for the movie entry."""
        return (self.name.strip().lower(), self.year)


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

        with csv_file.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            entries = [WatchedEntry.model_validate(row) for row in reader]

        if not entries:
            self.stdout.write(self.style.WARNING("No valid entries found."))
            return

        # Use normalized key for matching
        title_year_pairs: set[tuple[str, int]] = {entry.normalized_key() for entry in entries}

        # Query all matching movies in one go
        filters = Q()
        for title, year in title_year_pairs:
            filters |= Q(title__iexact=title, release_year=year)

        matched_movies = Movie.objects.filter(filters)
        movie_lookup = {(movie.title.lower(), movie.release_year): movie for movie in matched_movies}

        updated_movies = []
        not_found = []

        for entry in entries:
            key = entry.normalized_key()
            movie = movie_lookup.get(key)
            if movie:
                if not movie.watched:
                    movie.watched = True
                    updated_movies.append(movie)
            else:
                not_found.append(f"{entry.name} ({entry.year})")

        if updated_movies:
            Movie.objects.bulk_update(updated_movies, ["watched"])

        self.stdout.write(self.style.SUCCESS(f"Updated {len(updated_movies)} movies as watched."))
        if not_found:
            self.stdout.write(self.style.WARNING(f"{len(not_found)} movies not found in your DB:"))
            for title in not_found:
                self.stdout.write(f"  - {title}")
