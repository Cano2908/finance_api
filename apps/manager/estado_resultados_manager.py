import io
from typing import Set

import pandas as pd
from fastapi import UploadFile

from apps.api.config.exceptions.mongo_dao_exceptions import MongoUpdateException
from apps.api.config.exceptions.periodo_contable_exception import (
    InvalidNameByFileException,
    MissingColumnsByFileException,
    MissingConceptsByFileException,
    NoEstadoResultadosAvailableException,
    NoPeriodoContableAvailableException,
)
from apps.mongo.daos.periodo_contable_dao import PeriodoContableDAO
from apps.mongo.models.extensions.estado_resultados import EstadoResultados
from apps.mongo.models.periodo_contable import (
    PeriodoContable,
    parse_amount,
)
from apps.tools.objectid import ObjectId

ER_CONCEPTOS_MAP = {
    "ventas_netas": "ventas_netas",
    "costo_ventas": "costo_ventas",
    "utilidad_bruta": "utilidad_bruta",
    "gastos_operativos": "gastos_operativos",
    "utilidad_operativa": "utilidad_operativa",
    "resultado_financieros": "resultado_financieros",
    "utilidad_ante_impuestos": "utilidad_ante_impuestos",
    "impuesto_utilidad": "impuesto_utilidad",
    "utilidad_neta": "utilidad_neta",
}


class EstadoResultadosManager:
    def __init__(self) -> None:
        self._periodo_contable_dao = PeriodoContableDAO()

    async def get_estado_resultados_by_periodo(
        self,
        id_periodo: ObjectId,
    ) -> EstadoResultados:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(
                item_id=id_periodo,
            )
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable con el id: {id_periodo}"
            )

        estado_resultados: EstadoResultados | None = periodo_contable.estado_resultado

        if estado_resultados is None:
            raise NoEstadoResultadosAvailableException(
                f"No hay estado de resultados disponible para el periodo contable con el id: {id_periodo}"
            )

        return estado_resultados

    async def create_estado_resultados_by_file(
        self,
        id_periodo: ObjectId,
        file: UploadFile,
    ) -> EstadoResultados:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(item_id=id_periodo)
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable con el id: {id_periodo}"
            )

        if periodo_contable.estado_resultado is not None:
            raise NoEstadoResultadosAvailableException(
                f"Ya existe un estado de resultados para el periodo contable con el id: {id_periodo}"
            )

        contents = await file.read()
        filename = file.filename

        if not filename:
            raise InvalidNameByFileException("El archivo no tiene un nombre válido.")

        # Leer archivo
        if filename.endswith(".xlsx"):
            df: pd.DataFrame = pd.read_excel(io.BytesIO(contents))
        else:
            df: pd.DataFrame = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # Validar columnas necesarias
        required_columns: Set[str] = {"Concepto", "Cantidad"}
        missing_columns: Set[str] = required_columns - set(df.columns)

        if missing_columns:
            raise MissingColumnsByFileException(
                f"El archivo no contiene las columnas requeridas: {missing_columns}"
            )

        df["Concepto"] = df["Concepto"].str.strip()
        df["Cantidad"] = df["Cantidad"].apply(parse_amount)

        # Obtener campos válidos del modelo
        modelo_campos: Set[str] = set(EstadoResultados.model_fields.keys())

        # Validar que todos los conceptos del modelo estén en el archivo
        conceptos_archivo = set(df["Concepto"])
        conceptos_faltantes: Set[str] = modelo_campos - conceptos_archivo
        if conceptos_faltantes:
            raise MissingConceptsByFileException(
                f"Faltan los siguientes conceptos del modelo en el archivo: {conceptos_faltantes}"
            )

        # Construir dict con los datos
        data_dict = {
            row["Concepto"]: row["Cantidad"]
            for _, row in df.iterrows()
            if row["Concepto"] in modelo_campos
        }

        estado_resultados = EstadoResultados(**data_dict)

        # Guardar en el periodo contable
        periodo_contable.estado_resultado = estado_resultados

        updated_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.update_by_id(
                item_id=id_periodo,
                data=periodo_contable,
            )
        )

        if updated_periodo_contable is None:
            raise MongoUpdateException(
                f"No se pudo crear el estado de resultados para el periodo contable con el id: {id_periodo}"
            )

        return estado_resultados

    async def create_estado_resultados(
        self,
        id_periodo: ObjectId,
        estado_resultados: EstadoResultados,
    ) -> EstadoResultados:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(
                item_id=id_periodo,
            )
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable con el id: {id_periodo}"
            )

        if periodo_contable.estado_resultado is not None:
            raise NoEstadoResultadosAvailableException(
                f"Ya existe un estado de resultados para el periodo contable con el id: {id_periodo}"
            )

        periodo_contable.estado_resultado = estado_resultados

        updated_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.update_by_id(
                item_id=id_periodo,
                data=periodo_contable,
            )
        )

        if updated_periodo_contable is None:
            raise MongoUpdateException(
                f"No se pudo crear el estado de resultados para el periodo contable con el id: {id_periodo}"
            )

        return estado_resultados

    async def update_estado_resultados(
        self,
        id_periodo: ObjectId,
        estado_resultados: EstadoResultados,
    ) -> EstadoResultados:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(
                item_id=id_periodo,
            )
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable con el id: {id_periodo}"
            )

        estado_resultados_existente: EstadoResultados | None = (
            periodo_contable.estado_resultado
        )

        if estado_resultados_existente is None:
            raise NoEstadoResultadosAvailableException(
                f"No hay estado de resultados disponible para el periodo contable con el id: {id_periodo}"
            )

        periodo_contable.estado_resultado = estado_resultados

        updated_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.update_by_id(
                item_id=id_periodo,
                data=periodo_contable,
            )
        )

        if updated_periodo_contable is None:
            raise MongoUpdateException(
                f"No se pudo actualizar el estado de resultados para el periodo contable con el id: {id_periodo}"
            )

        return estado_resultados

    async def delete_estado_resultados(
        self,
        id_periodo: ObjectId,
    ) -> None:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(
                item_id=id_periodo,
            )
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable con el id: {id_periodo}"
            )

        estado_resultados_existente: EstadoResultados | None = (
            periodo_contable.estado_resultado
        )

        if estado_resultados_existente is None:
            raise NoEstadoResultadosAvailableException(
                f"No hay estado de resultados disponible para el periodo contable con el id: {id_periodo}"
            )

        periodo_contable.estado_resultado = None

        updated_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.update_by_id(
                item_id=id_periodo,
                data=periodo_contable,
            )
        )

        if updated_periodo_contable is None:
            raise MongoUpdateException(
                f"No se pudo actualizar el estado de resultados para el periodo contable con el id: {id_periodo}"
            )
