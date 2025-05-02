import inspect

# pylint: disable=unused-import  # reason: needed for Enum validation
from enum import Enum
from types import UnionType
from typing import Any, Callable, Optional, Type, Union, cast, get_args, get_type_hints

from pydantic import BaseModel


def get_imports(type_hint) -> set[str]:

    if inspect.isclass(type_hint):
        if type_hint.__module__ == "builtins":
            return set[str]()

        return {f"import {type_hint.__module__}"}

    # case if its Optional

    if hasattr(type_hint, "__origin__") and type_hint.__origin__ == Union:
        imports = set[str]()
        imports.add("from typing import Optional")

        for arg in type_hint.__args__:
            imports = imports.union(get_imports(arg))
        return imports

    if type_hint.__class__ is UnionType:
        imports = set[str]()
        imports.add("from typing import Union")

        for arg in type_hint.__args__:
            imports = imports.union(get_imports(arg))
        return imports

    args = get_args(type_hint)
    if len(args) > 0:
        imports = set[str]()

        for arg in args:
            imports = imports.union(get_imports(arg))
        return imports

    return {f"from {type_hint.__module__} import {type_hint.__name__}"}


def get_type_hint_str(type_hint):
    if inspect.isclass(type_hint):
        if type_hint.__module__ == "builtins":
            if type_hint.__name__ == "NoneType":
                return "None"

            return type_hint.__name__

        return f"{type_hint.__module__}.{type_hint.__name__}"

    # case if its Optional
    if hasattr(type_hint, "__origin__") and type_hint.__origin__ == Union:
        args = get_args(type_hint)
        return f"Optional[{get_type_hint_str(args[0])}]"

    if type_hint.__class__ is UnionType:
        return f"Union[{', '.join([get_type_hint_str(arg) for arg in type_hint.__args__])}]"

    return str(type_hint)


def get_model_filters(
    model_class: Type[BaseModel],
    exclude: Optional[list[str]] = None,
):
    if exclude is None:
        exclude = []

    filtered_type_hints = {}

    for field_name, type_hint in get_type_hints(model_class).items():
        if field_name in exclude:
            continue

        if field_name.startswith("__"):
            continue

        field = model_class.model_fields[field_name]
        if field.alias:
            field_name = field.alias

        filtered_type_hints[field_name] = type_hint

    all_imports = set[str](
        {"from typing import Annotated", "from fastapi import Query"}
    )
    for type_hint in filtered_type_hints.values():
        imports = get_imports(type_hint)
        all_imports = all_imports.union(imports)

    all_imports = sorted(all_imports)

    params_str = ",\n".join(
        [
            f"{field_name}: Annotated[{get_type_hint_str(type_hint)}, Query(...)] = None"
            for field_name, type_hint in filtered_type_hints.items()
        ]
    )

    filters_dict_str = f"    filters = {{ {', '.join([f'{field_name!r}: ({field_name}.value if isinstance({field_name}, Enum) else {field_name})' for field_name in filtered_type_hints])} }}\n"

    return_str = "    filters =  {k: v for k, v in filters.items() if v is not None}\n    return filters"

    func_str = "\n".join(
        [
            "\n".join(all_imports),
            f"def _get_model_filters({params_str}) -> dict[str, Any]:",
            filters_dict_str,
            return_str,
        ]
    )

    local_scope = {}

    def _get_model_filters(*_, **__) -> dict[str, Any]: ...

    exec(func_str, globals(), local_scope)

    _get_model_filters = cast(
        Callable[..., dict[str, Any]], local_scope["_get_model_filters"]
    )

    return _get_model_filters
