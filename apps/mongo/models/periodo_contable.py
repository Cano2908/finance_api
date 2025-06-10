from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from apps.mongo.core.base_mongo_model import BaseMongoModel, mongo_model
from apps.tools.date import Date
from apps.tools.objectid import ObjectId


class EstadoResultados(BaseModel):
    ventas_netas: Annotated[float, Field(alias="ventasNetas")]
    costo_ventas: Annotated[float, Field(alias="costoVentas")]
    utilidad_bruta: Annotated[float, Field(alias="utilidadBruta")]
    gastos_operativos: Annotated[float, Field(alias="gastosOperativos")]
    utilidad_operativa: Annotated[float, Field(alias="utilidadOperativa")]
    resultado_financieros: Annotated[float, Field(alias="resultadoFinancieros")]
    utilidad_ante_impuestos: Annotated[float, Field(alias="utilidadAnteImpuestos")]
    impuesto_utilidad: Annotated[float, Field(alias="impuestoUtilidad")]
    utilidad_neta: Annotated[float, Field(alias="utilidadNeta")]


class BalanceGeneral(BaseModel):
    efectivo_equivalentes: Annotated[float, Field(alias="efectivoEquivalentes")]
    cuentas_por_cobrar: Annotated[float, Field(alias="cuentasPorCobrar")]
    inventarios: Annotated[float, Field(alias="inventarios")]
    otros_activos_circulantes: Annotated[float, Field(alias="otrosActivosCirculantes")]
    propiedades_plantas_equipos: Annotated[
        float, Field(alias="propiedadesPlantasEquipos")
    ]
    total_activo_circulante: Annotated[float, Field(alias="totalActivoCirculante")]
    activos_intangibles: Annotated[float, Field(alias="activosIntangibles")]
    otros_activos_no_circulantes: Annotated[
        float, Field(alias="otrosActivosNoCirculantes")
    ]
    total_activo_no_circulante: Annotated[float, Field(alias="totalActivoNoCirculante")]
    total_activo: Annotated[float, Field(alias="totalActivo")]
    cuentas_por_pagar: Annotated[float, Field(alias="cuentasPorPagar")]
    pasivos_acumulados: Annotated[float, Field(alias="pasivosAcumulados")]
    deuda_a_corto_plazo: Annotated[float, Field(alias="deudaACortoPlazo")]
    total_pasivo_circulante: Annotated[float, Field(alias="totalPasivoCirculante")]
    deuda_a_largo_plazo: Annotated[float, Field(alias="deudaALargoPlazo")]
    otros_pasivos_a_largo_plazo: Annotated[
        float, Field(alias="otrosPasivosALargoPlazo")
    ]
    total_pasivo_a_largo_plazo: Annotated[float, Field(alias="totalPasivoALargoPlazo")]
    total_pasivo: Annotated[float, Field(alias="totalPasivo")]
    capital_social_y_utilidades_retenidas: Annotated[
        float, Field(alias="capitalSocialYUtilidadesRetenidas")
    ]
    total_pasivo_y_capital_contable: Annotated[
        float, Field(alias="totalPasivoYCapitalContable")
    ]


@mongo_model(collection_name="periodo_contable", schema_version=1)
class PeriodoContable(BaseMongoModel):
    id_empresa: Annotated[ObjectId, Field(alias="idEmpresa")]
    anio: Annotated[int, Field(alias="anio")]
    fecha_inicio: Annotated[Date, Field(alias="fechaInicio")]
    fecha_fin: Annotated[Date, Field(alias="fechaFin")]
    estado_resultado: Annotated[
        Optional[EstadoResultados], Field(alias="estadosResultados", default=None)
    ]
    balance_general: Annotated[Optional[BalanceGeneral], Field(alias="balanceGeneral", default=None)]
