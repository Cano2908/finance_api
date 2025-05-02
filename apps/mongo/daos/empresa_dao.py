from apps.mongo.core.base_mongo_dao import BaseMongoDAO
from apps.mongo.models.empresa import Empresa


class EmpresaDAO(BaseMongoDAO[Empresa]): ...
