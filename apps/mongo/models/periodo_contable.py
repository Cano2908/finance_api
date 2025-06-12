from typing import Annotated, Optional

from pydantic import BaseModel, Field

from apps.mongo.core.base_mongo_model import BaseMongoModel, mongo_model
from apps.tools.date import Date
from apps.tools.objectid import ObjectId


class EstadoResultados(BaseModel):
    ventas_netas: float
    costo_ventas: float
    utilidad_bruta: float
    gastos_operativos: float
    utilidad_operativa: float
    resultado_financieros: float
    utilidad_ante_impuestos: float
    impuesto_utilidad: float
    utilidad_neta: float


class BalanceGeneral(BaseModel):
    efectivo_equivalentes: float
    cuentas_por_cobrar: float
    inventarios: float
    otros_activos_circulantes: float
    propiedades_plantas_equipos: float
    total_activo_circulante: float
    activos_intangibles: float
    otros_activos_no_circulantes: float
    total_activo_no_circulante: float
    total_activo: float
    cuentas_por_pagar: float
    pasivos_acumulados: float
    deuda_a_corto_plazo: float
    total_pasivo_circulante: float
    deuda_a_largo_plazo: float
    otros_pasivos_a_largo_plazo: float
    total_pasivo_a_largo_plazo: float
    total_pasivo: float
    capital_social_y_utilidades_retenidas: float
    total_pasivo_y_capital_contable: float


@mongo_model(collection_name="periodo_contable", schema_version=1)
class PeriodoContable(BaseMongoModel):
    id_empresa: ObjectId
    anio: int
    fecha_inicio: Date
    fecha_fin: Date
    estado_resultado: Optional[EstadoResultados] = None
    balance_general: Optional[BalanceGeneral] = None
