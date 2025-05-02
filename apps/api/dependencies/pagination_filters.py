from enum import Enum
from typing import (
    Any,
    Callable,
    Coroutine,
    Protocol,
    Self,
    Type,
    TypeVar,
    runtime_checkable,
)

from pydantic import BaseModel, NonNegativeInt

from apps.tools.dynamic_enum import dynamic_enum
from apps.tools.paginator import (
    OrderDirection,
    PaginationFilters,
    PaginationMetadata,
    Paginator,
)


class OrderBy(Enum):
    pass


@runtime_checkable
class Sortable(Protocol):
    def __lt__(self, other: Self) -> bool: ...


T_PaginatorCallable = TypeVar("T_PaginatorCallable")
T_PaginationFiltersDependency = TypeVar("T_PaginationFiltersDependency")

PaginatorCallable = Callable[
    [list[T_PaginatorCallable]], tuple[list[T_PaginatorCallable], PaginationMetadata]
]

PaginationFiltersDependency = (
    Callable[
        [int, int, OrderBy, OrderDirection],
        Coroutine[Any, Any, PaginatorCallable[T_PaginationFiltersDependency]],
    ]
    | Callable[
        [int, int, OrderDirection],
        Coroutine[Any, Any, PaginatorCallable[T_PaginationFiltersDependency]],
    ]
)


T = TypeVar("T", bound=BaseModel)


def get_pagination_filters(
    model_class: Type[T] | None = None,
) -> Callable[..., Coroutine[Any, Any, PaginationFilters]]:

    if not model_class:

        async def _get_pagination_filters_wo_model(
            skip: NonNegativeInt = 0,
            limit: NonNegativeInt = 0,
            order_direction: OrderDirection = OrderDirection.ASC,
        ) -> PaginationFilters:

            pagination_filters = PaginationFilters(
                skip=skip,
                limit=limit,
                order_direction=order_direction,
            )

            return pagination_filters

        return _get_pagination_filters_wo_model

    allowed_order_by = model_class.model_fields

    enum_items = {}
    for field_name, field in allowed_order_by.items():
        if isinstance(field.annotation, Sortable):
            enum_items[field_name] = field.alias or field_name

    @dynamic_enum(lambda: enum_items)
    class OrderBy(Enum):
        pass

    async def _get_pagination_filters(
        skip: NonNegativeInt = 0,
        limit: NonNegativeInt = 0,
        order_by: OrderBy = OrderBy[[member.name for member in OrderBy][0]],
        order_direction: OrderDirection = OrderDirection.ASC,
    ) -> PaginationFilters:
        pagination_filters = PaginationFilters(
            skip=skip,
            limit=limit,
            order_by=order_by.name if order_by else None,
            order_direction=order_direction,
        )

        return pagination_filters

    return _get_pagination_filters


T_get_paginator = TypeVar("T_get_paginator", bound=BaseModel)
T2 = TypeVar("T2")


def get_paginator(
    model_class: Type[T_get_paginator] | None = None,
) -> PaginationFiltersDependency[T_get_paginator]:
    """
    Middleware to get pagination filters.
    Adds the following query parameters to the endpoint:

    - skip: The number of items to skip.
    - limit: The number of items to return.
    - order_by: The field to order the items by.
    - order_direction: The direction to order the items by.

    order_by will be an Enum Dynamically created with the fields of the model.

    Args:
        model_class (Type[BaseModel]): The model class to apply pagination filters on.


    Returns:
        Callable: A function that returns the pagination filters to be used as a dependency.

    """
    if not model_class:

        async def _get_pagination_filters_wo_model(
            skip: NonNegativeInt = 0,
            limit: NonNegativeInt = 0,
            order_direction: OrderDirection = OrderDirection.ASC,
        ) -> Callable[[list[T2]], tuple[list[T2], PaginationMetadata]]:

            pagination_filters = PaginationFilters(
                skip=skip,
                limit=limit,
                order_direction=order_direction,
            )

            def paginator(items: list[T2]) -> tuple[list[T2], PaginationMetadata]:
                paginator = Paginator(items)
                return paginator.paginate(pagination_filters)

            return paginator

        return _get_pagination_filters_wo_model

    allowed_order_by = model_class.model_fields

    enum_items = {}
    for field_name, field in allowed_order_by.items():
        if isinstance(field.annotation, Sortable):
            enum_items[field_name] = field.alias or field_name

    @dynamic_enum(lambda: enum_items)
    class OrderBy(Enum):
        pass

    async def _get_pagination_filters(
        skip: NonNegativeInt = 0,
        limit: NonNegativeInt = 0,
        order_by: OrderBy = OrderBy[[member.name for member in OrderBy][0]],
        order_direction: OrderDirection = OrderDirection.ASC,
    ) -> Callable[
        [list[T_get_paginator]], tuple[list[T_get_paginator], PaginationMetadata]
    ]:
        pagination_filters = PaginationFilters(
            skip=skip,
            limit=limit,
            order_by=order_by.name if order_by else None,
            order_direction=order_direction,
        )

        def paginator(
            items: list[T_get_paginator],
        ) -> tuple[list[T_get_paginator], PaginationMetadata]:
            paginator = Paginator(items)
            return paginator.paginate(pagination_filters)

        return paginator

    return _get_pagination_filters
