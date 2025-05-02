from apps.mongo.core.base_mongo_dao import BaseMongoDAO
from apps.mongo.models.balance_general import BalanceGeneral


class BalanceGeneralDAO(BaseMongoDAO[BalanceGeneral]): ...
