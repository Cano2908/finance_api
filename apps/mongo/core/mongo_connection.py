from typing import Optional, Self

from pymongo import MongoClient
from pymongo.database import Database

from apps.tools.env import env


class MongoConnection:
    __instance: Optional[Self] = None
    client: MongoClient
    db: Database

    def __new__(cls) -> Self:
        if not cls.__instance:
            # DB_HOST = env.MONGODB_URL
            DB_HOST = env.MONGODB_URL
            DB_NAME = env.MONGODBNAME
            # DB_USER = env.get("DB_USER") or ""
            # DB_PWD = env.get("DB_PWD") or ""
            DB_PORT = int(env.get("DB_PORT") or 27017)

            cls.__instance = object.__new__(cls)
            cls.__instance.client = MongoClient(
                host=DB_HOST,
                port=DB_PORT,
                # username=DB_USER,
                # password=DB_PWD,
                serverSelectionTimeoutMS=5000,
            )
            cls.__instance.db = cls.__instance.client.get_database(DB_NAME)
        return cls.__instance

    @classmethod
    def new(
        cls,
        host: str,
        database: str,
        *,
        port: int = 27017,
        username: str = "",
        password: str = "",
    ) -> Self:
        new_instance = object.__new__(cls)
        new_instance.client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            serverSelectionTimeoutMS=5000,
        )
        new_instance.db = new_instance.client.get_database(database)
        return new_instance

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()
