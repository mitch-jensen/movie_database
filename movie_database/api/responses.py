from typing import Literal

from pydantic import BaseModel


class DefaultPostSuccessResponse(BaseModel):
    """The default success response body on a POST request."""

    id: int


class DefaultDeleteSuccessResponse(BaseModel):
    """The default success response body on a DELETE request."""

    success: Literal[True] = True
