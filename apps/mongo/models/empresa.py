from enum import Enum
from re import S
from typing import Annotated

from pydantic import Field

from apps.mongo.core.base_mongo_model import BaseMongoModel, mongo_model


class StatusCompany(Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"


@mongo_model(collection_name="empresa", schema_version=1)
class Empresa(BaseMongoModel):
    nombre: str
    rfc: str
    status: StatusCompany = StatusCompany.ACTIVO
