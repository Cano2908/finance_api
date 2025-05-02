from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field

from apps.tools.date import Date

_DT = TypeVar("_DT")
_MT = TypeVar("_MT")


class ResponseModel(BaseModel, Generic[_DT, _MT]):
    """
    Represents a response object with status, date, detail, and data.

    Attributes:
        status (bool): The status of the response.
        date (Date): The date and time when the response was created.
        data (T): The data associated with the response.
        detail (str): A detailed description or additional information about the response.
        metadata (M): Additional information or metadata about the response.
    """

    date: Annotated[
        Date,
        Field(
            default_factory=Date,
            examples=[str(Date())],
        ),
    ] = Date()
    status: bool
    detail: str
    data: _DT = None  # type: ignore
    metadata: _MT = None  # type: ignore
