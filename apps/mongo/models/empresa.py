from enum import Enum
from typing import Annotated

from pydantic import Field

from apps.mongo.core.base_mongo_model import BaseMongoModel, mongo_model


class StatusCompany(Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"


@mongo_model(collection_name="empresa", schema_version=1)
class Empresa(BaseMongoModel):
    nombre: Annotated[str, Field(alias="nombre")]
    rfc: Annotated[str, Field(alias="rfc")]
    status: Annotated[
        StatusCompany, Field(alias="status", default=StatusCompany.ACTIVO)
    ]
