from apps.mongo.core.base_mongo_dao import BaseMongoDAO
from apps.mongo.models.periodo_contable import PeriodoContable


class PeriodoContableDAO(BaseMongoDAO[PeriodoContable]): ...
