from typing import Annotated

from pydantic import Field
from apps.mongo.core.base_mongo_model import BaseMongoModel, mongo_model


@mongo_model(collection_name="usuario", schema_version=1)
class Usuario(BaseMongoModel):
    nom_usuario: str
    contrasenia: str
