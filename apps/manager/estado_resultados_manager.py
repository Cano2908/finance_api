from typing import Dict

from apps.api.config.exceptions.estado_resultados_exception import (
    NoEstadoResultadosAvailableException,
)
from apps.api.config.exceptions.mongo_dao_exceptions import MongoUpdateException
from apps.mongo.daos.estado_resultados_dao import EstadoResultadosDAO
from apps.mongo.models.estado_resultado import EstadoResultados
from apps.tools.objectid import ObjectId


class EstadoResultadosManager:
    def __init__(self) -> None:
        self._estado_resultados_dao = EstadoResultadosDAO()

    async def get_estado_resultados_by_periodo(
        self,
        id_periodo: ObjectId,
        filters: Dict,
    ) -> EstadoResultados:
        filters = {
            **filters,
            "id_periodo": id_periodo,
        }

        estado_resultados: EstadoResultados | None = (
            await self._estado_resultados_dao.get(**filters)
        )

        if estado_resultados is None:
            raise NoEstadoResultadosAvailableException(
                f"No hay estado de resultados disponible con el id_balance: {id_periodo}"
            )

        return estado_resultados

    async def update_estado_resultados(
        self,
        id_estado_resultados: ObjectId,
        estado_resultados: EstadoResultados,
    ) -> EstadoResultados:

        find_estado_resultados: EstadoResultados | None = (
            await self._estado_resultados_dao.get_by_id(
                item_id=id_estado_resultados,
            )
        )

        if find_estado_resultados is None:
            raise NoEstadoResultadosAvailableException(
                f"No hay estado de resultados disponible con el id: {id_estado_resultados}"
            )

        updated_estado_resultados: EstadoResultados | None = (
            await self._estado_resultados_dao.update_by_id(
                item_id=id_estado_resultados,
                data=estado_resultados,
            )
        )

        if updated_estado_resultados is None:
            raise MongoUpdateException(
                f"No se pudo actualizar el estado de resultados con el id: {id_estado_resultados}"
            )

        return updated_estado_resultados

    async def delete_estado_resultados(
        self,
        id_estado_resultados: ObjectId,
    ) -> None:

        find_estado_resultados: EstadoResultados | None = (
            await self._estado_resultados_dao.get_by_id(
                item_id=id_estado_resultados,
            )
        )

        if find_estado_resultados is None:
            raise NoEstadoResultadosAvailableException(
                f"No hay estado de resultados disponible con el id: {id_estado_resultados}"
            )

        await self._estado_resultados_dao.delete_by_id(
            item_id=id_estado_resultados,
        )
