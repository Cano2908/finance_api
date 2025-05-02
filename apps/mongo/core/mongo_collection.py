import enum
import typing
from types import UnionType
from typing import (
    Any,
    AsyncGenerator,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    get_args,
    get_origin,
)
from uuid import UUID

from pydantic import BaseModel
from pymongo import DeleteMany, DeleteOne, InsertOne, ReplaceOne, UpdateMany, UpdateOne
from pymongo.collection import Collection
from typing_extensions import get_original_bases

from apps.mongo.core.base_mongo_model import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)


class MongoCollection(Generic[T]):
    """Wrapper class for pymongo collection

    This class provides a set of methods to interact with a pymongo collection.

    Usage:

    Direclty use the class to interact with a collection:

    ```python
    from pymongo import MongoClient
    from app.models.usuario import Usuario

    client = MongoClient("mongodb://localhost:27017/")
    db = client["test"]
    collection = db["usuarios"]

    usuarios_collection = MongoCollection(collection, Usuario)

    usuario = await usuarios_collection.find_one({"email": "user@example.com"})

    ```

    Subclass the class to create a DAO:

    ```python
    from pymongo import MongoClient
    from app.models.usuario import Usuario

    class UsuariosCollection(MongoCollection[Usuario]):
        pass # No implementation needed

    usuarios_collection = UsuariosCollection(collection) # when subclassing, the model class is inferred

    usuario = await usuarios_collection.find_one({"email": "user@example.com"})

    """

    _collection: Collection
    _model_class: Type[T] | Tuple[Type[T], ...]

    def __init__(self, collection, model_class: Optional[Type[T]] = None):
        self._collection = collection

        if model_class is not None:
            self._model_class = model_class
        else:
            self._model_class = self._get_model_class()

    def _get_model_class(self) -> Type[T]:
        bases = get_original_bases(self.__class__)
        args = get_args(bases[0])
        return args[0]

    def find_many_sync(
        self,
        filters: Optional[dict] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[T]:
        if filters is None:
            filters = {}

        result = self._collection.find(filters)

        if page is not None and page_size is not None:
            result = result.skip(page * page_size).limit(page_size)

        items: List[T] = [self._parse_model_validator(item) for item in result]
        return items

    async def find_one(self, filters: dict[str, Any]) -> Optional[T]:
        """Find one document in the collection

        Args:
            `filter: dict`  Filter to find the document

        Returns:
            `Optional[T]` The document found or None
        """
        result = self._collection.find_one(filters)
        if result:
            return self._parse_model_validator(result)
        return None

    def find_one_sync(self, filters: dict[str, Any]) -> Optional[T]:
        result = self._collection.find_one(filters)
        if result:
            return self._parse_model_validator(result)
        return None

    async def find_many(
        self,
        filters: Optional[dict] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[T]:
        """Find many documents in the collection

        Args:
            `filter: dict`  Filter to find the documents

        Returns:
            `List[T]` The documents found
        """
        if filters is None:
            filters = {}
        result = self._collection.find(filters)

        if page is not None and page_size is not None:
            result = result.skip(page * page_size).limit(page_size)

        items: List[T] = [self._parse_model_validator(item) for item in result]
        return items

    async def find_many_generator(
        self,
        filters: Optional[dict] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> AsyncGenerator[T, None]:
        """Find many documents in the collection

        Use this method when you want to iterate over the results asynchronously. Recommended when processing large amounts of data, as it avoids loading all the data into memory.

        Args:
            `filter: dict`  Filter to find the documents

        Returns:
            `AsyncGenerator[T, None]` The documents found
        """
        if filters is None:
            filters = {}
        result = self._collection.find(filters)

        if page is not None and page_size is not None:
            result = result.skip(page * page_size).limit(page_size)

        for item in result:
            yield self._parse_model_validator(item)

    async def insert_one(self, model: T) -> T:
        """Insert one document in the collection
        å
                Args:
                    `model: T`  The document to insert

                Returns:
                    `T` The document inserted
        """
        self._parse_model_validator(model)
        model_dump = self._get_model_dump(model)
        model_dump["schema_version"] = self._get_schema_version(model)
        model_dump = self._enum_to_value(model_dump)

        result = self._collection.insert_one(model_dump)
        model.id = result.inserted_id
        return model

    async def insert_many(self, models: List[T]) -> List[T]:
        """Insert many documents in the collection

        Args:
            `models: List[T]`  The documents to insert

        Returns:
            `List[T]` The documents inserted
        """
        json_models: List[dict] = []
        for model in models:
            self._parse_model_validator(model)
            json_model = self._get_model_dump(model)
            json_model["schema_version"] = self._get_schema_version(model)
            json_model = self._enum_to_value(json_model)
            if isinstance(json_model, dict):
                json_models.append(json_model)
            else:
                raise TypeError("Expected json_model to be a dictionary")

        result = self._collection.insert_many(json_models)
        for i, model in enumerate(models):
            model.id = result.inserted_ids[i]
        return models

    async def update_one(
        self,
        filters: dict,
        model: T,
        upsert: bool = False,
    ) -> Optional[T]:
        """Update one document in the collection

        Args:
            `filter: dict`  Filter to find the document
            `model: T`  The document to update

        Returns:
            `Optional[T]` The document updated or None
        """
        self._parse_model_validator(model)
        model_dump = self._get_model_dump(model)
        model_dump["schema_version"] = self._get_schema_version(model)
        model_dump = self._enum_to_value(model_dump)

        result = self._collection.update_one(
            filters, {"$set": model_dump}, upsert=upsert
        )
        if result.matched_count == 0:
            raise DocumentNotFoundException("No document found to update")
        if result.modified_count == 1:
            return model
        return None

    async def update(
        self,
        filters: Optional[dict] = None,
        update: Optional[dict] = None,
    ) -> bool:
        """
        Updates documents in the collection that match the given filter with the specified update.

        Args:
            filter (dict): The filter criteria to select the documents to update.
            update (dict): The update to apply to the selected documents.

        Returns:
            bool: True if at least one document was modified, False otherwise.
        """
        if filters is None:
            filters = {}
        if update is None:
            update = {}
        self._parse_model_validator(update)
        update_dump = self._get_model_dump(update)
        update_dump = self._enum_to_value(update_dump)

        result = self._collection.update_many(filters, update_dump)

        if result.matched_count == 0:
            raise DocumentNotFoundException("No document found to update")
        if result.modified_count > 0:
            return True
        return False

    async def delete_one(self, filters: dict) -> bool:
        result = self._collection.delete_one(filters)
        if result.deleted_count == 1:
            return True
        return False

    async def delete_many(self, filters: dict) -> bool:
        result = self._collection.delete_many(filters)
        if result.deleted_count > 0:
            return True
        return False

    async def purge(self) -> bool:
        result = self._collection.delete_many({})
        if result.deleted_count > 0:
            return True
        return False

    async def count(self, filters: dict) -> int:
        result = self._collection.count_documents(filters)
        return result

    async def aggregate(self, pipeline: List[dict]) -> List[dict]:
        result = self._collection.aggregate(pipeline)
        result_list = list(result)
        return result_list

    async def distinct(self, field: str, filters: dict) -> List[dict]:
        result = self._collection.distinct(field, filters)
        return result

    async def bulk_write(
        self,
        operations: List[
            InsertOne | DeleteOne | UpdateOne | DeleteMany | ReplaceOne | UpdateMany
        ],
    ) -> Any:
        result = self._collection.bulk_write(operations)
        return result

    def _get_schema_version(self, model: T | dict) -> int:
        schema_version: Optional[int] = None

        if self._model_class.__class__ is UnionType:
            args = get_args(self._model_class)
            for model_class in args:
                if not isinstance(model, model_class):
                    continue

                schema_version = model_class.__schema_version__
                break

        elif isinstance(self._model_class, tuple):
            for model_class in self._model_class:
                if not isinstance(model, model_class):
                    continue

                schema_version = model_class.__schema_version__
                break
        else:
            schema_version = self._model_class.__schema_version__

        return schema_version or 1

    def _get_model_dump(self, model: Any) -> Any:
        if isinstance(model, dict):
            model_dump = model
            for key, value in model_dump.items():
                model_dump[key] = self._get_model_dump(value)

        elif isinstance(model, BaseMongoModel):
            model_dump = model.model_dump(exclude={"id"}, by_alias=True)
        elif isinstance(model, BaseModel):
            model_dump = model.model_dump()
        elif isinstance(model, list):
            model_dump = [self._get_model_dump(item) for item in model]
        elif isinstance(model, (int, str, float, bool)):
            model_dump = model
        else:
            model_dump = model

        if isinstance(model_dump, dict):
            for key, value in model_dump.items():
                if isinstance(value, (UUID)):
                    model_dump[key] = str(value)
                if isinstance(value, enum.Enum):
                    model_dump[key] = value.value

        return model_dump

    def _parse_model_validator(self, model: dict | T) -> T:
        model_class_candidates = self._collect_model_classes_mongo(self._model_class)

        try_errors: dict[Type[T], Exception] = {}

        for model_class in model_class_candidates:
            try:
                parsed_item = model_class.model_validate(model)
                return parsed_item
            except Exception as e:
                try_errors[model_class] = e

        raise ModelParsingException("Unable to validate model", try_errors)

    def _collect_model_classes_mongo(self, model_class: Type[T] | Tuple[Type[T], ...]):
        """Recursively collects candidate model classes from nested Unions and Tuples."""
        candidates: list[Type[T]] = []

        origin_model = get_origin(model_class)
        args_model = get_args(model_class)

        if model_class.__class__ is UnionType or origin_model is typing.Union:
            for arg in args_model:
                candidates.extend(self._collect_model_classes_mongo(arg))
        elif isinstance(model_class, tuple):
            for sub_class in model_class:
                candidates.extend(self._collect_model_classes_mongo(sub_class))
        else:
            if issubclass(model_class, BaseMongoModel):
                candidates.append(model_class)
        return candidates

    def _enum_to_value(self, data: Any):
        if isinstance(data, enum.Enum):
            return data.value
        if isinstance(data, dict):
            return {k: self._enum_to_value(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._enum_to_value(item) for item in data]
        return data


class ModelParsingException(Exception, Generic[T]):
    errors: dict[Type[T], Exception]

    def __init__(self, message: str, errors: dict[Type[T], Exception]):
        super().__init__(message)
        self.errors = errors

    def __str__(self):
        return f"{super().__str__()} {self.errors}"


class DocumentNotFoundException(Exception):
    pass
