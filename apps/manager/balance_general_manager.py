from typing import Dict

from apps.api.config.exceptions.mongo_dao_exceptions import MongoUpdateException
from apps.api.config.exceptions.periodo_contable_exception import (
    NoPeriodoContableAvailableException,
)
from apps.mongo.daos.balance_general_dao import BalanceGeneralDAO
from apps.mongo.models.balance_general import BalanceGeneral
from apps.tools.objectid import ObjectId


class BalanceGeneralManager:
    def __init__(self) -> None:
        self._balance_general_dao = BalanceGeneralDAO()

    async def get_balance_general_by_periodo(
        self,
        id_periodo: ObjectId,
        filters: Dict,
    ) -> BalanceGeneral:
        filters = {
            **filters,
            "id_periodo": id_periodo,
        }

        periodo_contable: BalanceGeneral | None = await self._balance_general_dao.get(
            **filters
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay balance general disponible con el id_balance: {id_periodo}"
            )

        return periodo_contable

    async def update_balance_general(
        self,
        id_balance_general: ObjectId,
        balance_general: BalanceGeneral,
    ) -> BalanceGeneral:

        find_balance_general: BalanceGeneral | None = (
            await self._balance_general_dao.get_by_id(
                item_id=id_balance_general,
            )
        )

        if find_balance_general is None:
            raise NoPeriodoContableAvailableException(
                f"No hay balance general disponible con el id: {id_balance_general}"
            )

        updated_balance_general: BalanceGeneral | None = (
            await self._balance_general_dao.update_by_id(
                item_id=id_balance_general,
                data=balance_general,
            )
        )

        if updated_balance_general is None:
            raise MongoUpdateException(
                f"No se pudo actualizar el balance general con el id: {id_balance_general}"
            )

        return updated_balance_general

    async def delete_balance_general(self, id_balance_general: ObjectId) -> None:
        find_balance_general: BalanceGeneral | None = (
            await self._balance_general_dao.get_by_id(item_id=id_balance_general)
        )

        if find_balance_general is None:
            raise NoPeriodoContableAvailableException(
                f"No hay balance general disponible con el id: {id_balance_general}"
            )

        await self._balance_general_dao.delete_by_id(item_id=id_balance_general)
