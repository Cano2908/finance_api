import re
from typing import Annotated, Callable, Optional, Self, Type, TypeVar

import inflect
from pydantic import BaseModel, Field

from apps.tools.objectid import ObjectId


class BaseMongoModel(BaseModel):
    """
    Base model for all mongo models.
    """

    __collection_name__: Optional[str] = None
    __schema_version__: Optional[int] = None

    id: Annotated[
        Optional[ObjectId],
        Field(
            alias="_id",
            serialization_alias="_id",
            examples=["65a804bc2828cacc454c7d53"],
        ),
    ] = None

    @classmethod
    def from_model(cls, model: BaseModel) -> Self:
        """
        Convert a Pydantic model to a MongoDB model.

        Args:
            model (BaseModel): The Pydantic model.

        Returns:
            BaseMongoModel: The MongoDB model.
        """
        return cls(**model.model_dump())


T = TypeVar("T", bound=BaseMongoModel)


def mongo_model(
    collection_name: Optional[str] = None,
    schema_version: int = 1,
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator function for MongoDB models.

    All models must inherit from `BaseModel`. This decorator sets the collection name and schema version.

    This decorator is necessary when defining DAO classes using the `MongoDAO` class or when using the `MongoCollection` class.

    This decorator is also necessary when using `MongoMigrationManager` to manage schema migrations.

    Args:
        collection_name (Optional[str]): The name of the MongoDB collection.
        schema_version (int, optional): The version of the schema. Defaults to 1.

    Usage:

    ```python
    @mongo_model(collection_name="my_collection")
    class MyModel(BaseModel):
        field: str

    model = MyModel(field="value")

    ```

    Returns:
        Callable[[Type[T]], Type[T]]: The MongoDB model class.
    """

    def _mongo_model(model_class: Type[T]) -> Type[T]:
        snake_case_name = re.sub(
            pattern=r"(?<!^)(?=[A-Z])",
            repl="_",
            string=model_class.__name__,
        ).lower()

        p = inflect.engine()

        collection = collection_name or p.plural(snake_case_name)  # type: ignore

        model_class.__collection_name__ = collection
        model_class.__schema_version__ = schema_version
        model_class.__name__ = model_class.__name__

        return model_class

    return _mongo_model
