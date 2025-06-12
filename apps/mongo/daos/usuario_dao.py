from apps.mongo.core.base_mongo_dao import BaseMongoDAO
from apps.mongo.models.user import Usuario


class UsuarioDAO(BaseMongoDAO[Usuario]): ...