from enum import Enum
from typing import Any, Callable, Dict, Type, TypeVar, cast

T = TypeVar("T", bound=Enum)


def dynamic_enum(func: Callable[..., Dict[str, Any]]):

    def create_dynamic_enum(cls: Type[T]) -> Type[T]:
        new_enum_class = update_enum_values(cls, func)

        return new_enum_class

    return create_dynamic_enum


def update_enum_values(cls: type[T], func):
    enum_values = func()
    new_enum_class = Enum(cls.__name__, enum_values)
    new_enum_class.__module__ = cls.__module__
    new_enum_class.__doc__ = cls.__doc__
    new_enum_class.__qualname__ = cls.__qualname__
    new_enum_class.__annotations__ = cls.__annotations__

    new_enum_class = cast(Type[T], new_enum_class)
    return new_enum_class
