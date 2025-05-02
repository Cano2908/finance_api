import typing
from enum import Enum
from types import UnionType
from typing import Any, Generic, Optional, Tuple, Type, TypeVar, get_args, get_origin

from bson import CodecOptions
from bson.codec_options import TypeEncoder, TypeRegistry
from typing_extensions import get_original_bases

from apps.mongo.core.base_mongo_model import BaseMongoModel
from apps.mongo.core.mongo_collection import MongoCollection
from apps.mongo.core.mongo_connection import MongoConnection
from apps.tools.cache import CacheMap
from apps.tools.objectid import ObjectId

T = TypeVar("T", bound=BaseMongoModel)


class BaseMongoDAO(Generic[T]):
    """
    All Mongo DAOs must extend this class and provide a model class as a type hint.

    Example:
    ```
    from clients.mongo.core.abc_mongo_dao import BaseMongoDAO
    from clients.mongo.core.base_mongo_model import BaseMongoModel, mongo_model

    @mongo_model()
    class Fruit(BaseMongoModel):
        name: str
        color: str

    class FruitsDAO(MongoDAO[Fruit]):
        pass

    dao = FruitsDAO()

    fruit = Fruit(name="apple", color="red")
    saved_fruit = await dao.create(fruit)

    retrieved_fruit = await dao.get_by_id(saved_fruit.id)
    ```
    """

    _collection: MongoCollection[T]

    def __init__(
        self,
        connection: MongoConnection = MongoConnection(),
    ) -> None:

        db = connection.db
        model_class = self._get_model_class()
        collection_name = self._get_collection_name(model_class)
        codec_options = self._get_codec_options()
        collection = db.get_collection(collection_name, codec_options=codec_options)
        self._caching = CacheMap()

        class TypedCollection(MongoCollection[model_class]):
            pass

        self._collection = TypedCollection(collection=collection)

    async def get_all(
        self,
        *,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        use_cache: Optional[bool] = False,
        **filters: Any,
    ) -> list[T]:
        """retrieve all documents from the collection that match the filters"""
        cache_key = self._get_cache_key("get_all", page, page_size, **filters)

        if use_cache:
            cached_result = self._get_from_cache(cache_key)

            if cached_result is not None:
                return cached_result

        result = await self._collection.find_many(
            filters=filters,
            page=page,
            page_size=page_size,
        )
        self._set_cache(cache_key, result)

        return result

    def get_all_sync(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        use_cache: Optional[bool] = False,
        **filters: Any,
    ) -> list[T]:
        """retrieve all documents from the collection that match the filters"""
        cache_key = self._get_cache_key("get_all_sync", page, page_size, **filters)

        if use_cache:
            cached_result = self._get_from_cache(cache_key)

            if cached_result is not None:
                return cached_result

        result = self._collection.find_many_sync(
            filters=filters,
            page=page,
            page_size=page_size,
        )
        self._set_cache(cache_key, result)

        return result

    async def get_all_generator(
        self,
        *,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> typing.AsyncGenerator[T, None]:
        """retrieve all documents from the collection that match the filters"""
        return self._collection.find_many_generator(
            page=page,
            page_size=page_size,
            filters=filters,
        )

    async def get_by_id(
        self,
        item_id: ObjectId,
        use_cache: Optional[bool] = False,
    ) -> Optional[T]:
        """retrieve a document by its id"""
        cache_key = self._get_cache_key("get_by_id", item_id)

        if use_cache:
            cached_result = self._get_from_cache(cache_key)

            if cached_result is not None:
                return cached_result

        result = await self._collection.find_one({"_id": item_id})

        self._set_cache(cache_key, result)
        return result

    def get_by_id_sync(
        self,
        item_id: ObjectId,
        use_cache: Optional[bool] = False,
    ) -> Optional[T]:
        """retrieve a document by its id"""
        cache_key = self._get_cache_key("get_by_id", item_id)

        if use_cache:
            cached_result = self._get_from_cache(cache_key)

            if cached_result is not None:
                return cached_result

        result = self._collection.find_one_sync({"_id": item_id})

        self._set_cache(cache_key, result)
        return result

    async def get(
        self, use_cache: Optional[bool] = False, **filters: Any
    ) -> Optional[T]:
        """retrieve a document that matches the filters"""
        cache_key = self._get_cache_key("get", **filters)

        if use_cache:
            cached_result = self._get_from_cache(cache_key)

            if cached_result is not None:
                return cached_result

        result = await self._collection.find_one(filters)

        self._set_cache(cache_key, result)
        return result

    def get_sync(
        self, use_cache: Optional[bool] = False, **filters: Any
    ) -> Optional[T]:
        """retrieve a document that matches the filters"""
        cache_key = self._get_cache_key("get", **filters)

        if use_cache:
            cached_result = self._get_from_cache(cache_key)

            if cached_result is not None:
                return cached_result

        result = self._collection.find_one_sync(filters)

        self._set_cache(cache_key, result)
        return result

    async def create(self, data: T) -> T:
        """create a new document in the collection"""
        result = await self._collection.insert_one(data)
        self._caching.cache.clear()
        return result

    async def update_by_id(self, item_id: ObjectId, data: T) -> Optional[T]:
        """update a document in the collection"""
        del data.id
        updated = await self._collection.update_one({"_id": item_id}, data)
        if updated:
            updated.id = item_id
            self._caching.cache.clear()
        return updated

    async def update(self, data: T, **filters: Any) -> Optional[T]:
        """update a document in the collection"""
        del data.id
        updated = await self._collection.update_one(filters, data)
        if updated:
            self._caching.cache.clear()
            return data
        return None

    async def update_many(self, filters: dict, data: dict) -> bool:
        """update many documents in the collection"""
        result = await self._collection.update(filters, data)

        if result:
            self._caching.cache.clear()
        return result

    async def delete(self, **filters: Any) -> bool:
        """delete documents from the collection"""
        result = await self._collection.delete_many(filters)

        if result:
            self._caching.cache.clear()
        return result

    async def delete_by_id(self, item_id: ObjectId) -> bool:
        """delete a document from the collection"""
        result = await self._collection.delete_one({"_id": item_id})

        if result:
            self._caching.cache.clear()
        return result

    def _get_collection_name(self, model_class: Type[T] | Tuple[Type[T], ...]) -> str:
        model_candidates = self._collect_model_classes(model_class)

        collection_names = set()
        for candidate in model_candidates:
            try:
                collection_name = candidate.__collection_name__
                if not collection_name:
                    continue

                collection_names.add(collection_name)
            except AttributeError:
                pass

        if len(collection_names) > 1:
            raise ValueError(
                "All model classes in a Union or Tuple must have the same collection name."
            )
        if len(collection_names) == 1:
            return collection_names.pop()

        raise ValueError(
            "Model class must be a subclass of BaseMongoModel, a Union of BaseMongoModels or a Tuple of BaseMongoModels."
        )

    def _get_model_class(self) -> Type[T]:
        orig_bases = get_original_bases(self.__class__)
        args = get_args(orig_bases[0])
        return args[0]

    def _collect_model_classes(
        self, model_class: Type[T] | Tuple[Type[T], ...]
    ) -> list[type[T]]:
        """Recursively collects candidate model classes from nested Unions and Tuples."""
        candidates: list[Type[T]] = []

        origin = get_origin(model_class)
        args = get_args(model_class)

        if model_class.__class__ is UnionType or origin is typing.Union:
            for arg in args:
                candidates.extend(self._collect_model_classes(arg))
        elif isinstance(model_class, tuple):
            for sub_class in model_class:
                candidates.extend(self._collect_model_classes(sub_class))
        else:
            if issubclass(model_class, BaseMongoModel):
                candidates.append(model_class)
        return candidates

    def _get_codec_options(self):
        # Add custom encoders for user defined classes
        encoders = []

        encoders.extend(self._get_enum_encoders())

        type_registry = TypeRegistry(encoders)
        codec_options = CodecOptions(type_registry=type_registry)
        return codec_options

    def _get_enum_encoders(self):
        encoders = []

        user_defined_enums = get_user_defined_enums(["models"])

        for subclass in user_defined_enums:

            class EnumEncoder(TypeEncoder):
                bson_type = str
                python_type = subclass  # type: ignore

                def transform_python(self, value):
                    return value.value

                def transform_bson(self, value: str):
                    return value

            encoders.append(EnumEncoder())

        return encoders

    def _get_cache_key(self, method: str, *args: Any, **kwargs: Any) -> str:
        return f"{__class__}.{method}.{args}.{kwargs}"

    def _get_from_cache(self, key: str) -> Optional[Any]:
        return self._caching.get(key)

    def _set_cache(self, key: str, value: Any) -> None:
        self._caching.set(key, value)


def get_user_defined_enums(app_modules: list[str]):
    return filter(
        lambda enum_class: enum_class.__module__.startswith(tuple(app_modules)),
        Enum.__subclasses__(),
    )
