from apps.api.config.exceptions.mongo_dao_exceptions import MongoUpdateException
from apps.api.config.exceptions.periodo_contable_exception import (
    NoEstadoResultadosAvailableException,
    NoPeriodoContableAvailableException,
)
from apps.mongo.daos.periodo_contable_dao import PeriodoContableDAO
from apps.mongo.models.periodo_contable import EstadoResultados, PeriodoContable
from apps.tools.objectid import ObjectId


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
            await self._periodo_contable_dao.update(
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

        estado_resultados_existente: EstadoResultados | None = periodo_contable.estado_resultado

        if estado_resultados_existente is None:
            raise NoEstadoResultadosAvailableException(
                f"No hay estado de resultados disponible para el periodo contable con el id: {id_periodo}"
            )

        periodo_contable.estado_resultado = estado_resultados

        updated_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.update(
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

        estado_resultados_existente: EstadoResultados | None = periodo_contable.estado_resultado

        if estado_resultados_existente is None:
            raise NoEstadoResultadosAvailableException(
                f"No hay estado de resultados disponible para el periodo contable con el id: {id_periodo}"
            )

        periodo_contable.estado_resultado = None

        updated_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.update(
                item_id=id_periodo,
                data=periodo_contable,
            )
        )

        if updated_periodo_contable is None:
            raise MongoUpdateException(
                f"No se pudo actualizar el estado de resultados para el periodo contable con el id: {id_periodo}"
            )

