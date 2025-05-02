from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar

from pydantic import BaseModel


class OrderDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class PaginationFilters(BaseModel):
    skip: int
    limit: int
    order_by: Optional[str] = None
    order_direction: OrderDirection = OrderDirection.ASC


class PaginationMetadata(BaseModel):
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
    current_page: int
    limit: int
    skip: int


T = TypeVar("T")


class Paginator(Generic[T]):
    def __init__(
        self, items: list[T]
    ):  # pylint: disable=undefined-variable # reason: `T` is defined in the class signature. False positive.
        self._items = items

    def paginate(
        self, pagination_filters: PaginationFilters
    ) -> tuple[
        list[T], PaginationMetadata
    ]:  # pylint: disable=undefined-variable # reason: `T` is defined in the class signature. False positive.
        """For the given list of items, return a tuple with the paginated data and the pagination metadata.

        `total_pages`, `has_next`, `has_previous` and `current_page` are more accurate when `skip` is a multiple of `limit`.
        """

        if pagination_filters.order_by:
            self._items = sorted(
                self._items,
                key=self._sort_func(pagination_filters.order_by),
                reverse=pagination_filters.order_direction == OrderDirection.DESC,
            )
        elif pagination_filters.order_direction:
            self._items = (
                list(reversed(self._items))
                if pagination_filters.order_direction == OrderDirection.DESC
                else self._items
            )

        aux_limit = pagination_filters.limit or len(self._items)
        if pagination_filters.limit + pagination_filters.skip > len(self._items):
            aux_limit = len(self._items) - pagination_filters.skip

        start = pagination_filters.skip
        end = start + aux_limit

        page_data = self._items[start:end]

        total_items = len(self._items)
        total_pages = (
            (total_items + pagination_filters.limit - 1) // pagination_filters.limit
            if pagination_filters.limit
            else 1
        )
        has_next = (
            (pagination_filters.skip + pagination_filters.limit < total_items)
            if pagination_filters.limit
            else False
        )
        has_previous = pagination_filters.skip > 0
        current_page = (
            pagination_filters.skip // pagination_filters.limit + 1
            if pagination_filters.limit
            else 1
        )

        return page_data, PaginationMetadata(
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
            current_page=current_page,
            limit=pagination_filters.limit,
            skip=pagination_filters.skip,
        )

    def _sort_func(self, order_by: str) -> Callable[..., tuple[bool, Any]]:
        def key(item) -> tuple[bool, Any]:
            attr1 = getattr(item, order_by)

            if isinstance(attr1, Enum):
                return (attr1.value is None, attr1.value)

            return (attr1 is None, attr1)

        return key
