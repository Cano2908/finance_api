from apps.mongo.core.base_mongo_model import BaseMongoModel, mongo_model
from apps.tools.date import Date
from apps.tools.objectid import ObjectId


@mongo_model(collection_name="periodo_contable", schema_version=1)
class PeriodoContable(BaseMongoModel):
    id_empresa: ObjectId
    nombre: str
    fecha_inicio: Date
    fecha_fin: Date
