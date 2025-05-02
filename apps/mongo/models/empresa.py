from enum import Enum
from typing import Optional

from apps.mongo.core.base_mongo_model import BaseMongoModel, mongo_model
from apps.tools.date import Date


class StatusCompany(Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"


@mongo_model(collection_name="empresa", schema_version=1)
class Empresa(BaseMongoModel):
    nombre: str
    descripcion: Optional[str] = None
    status: StatusCompany
    fecha_creacion: Date
