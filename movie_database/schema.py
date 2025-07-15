from ninja import ModelSchema

from .models import Movie


class MovieSchema(ModelSchema):
    """Schema for the Movie model."""

    class Meta:
        """Meta class for MovieSchema."""

        model = Movie
        fields = "__all__"
