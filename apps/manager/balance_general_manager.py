from apps.api.config.exceptions.mongo_dao_exceptions import MongoUpdateException
from apps.api.config.exceptions.periodo_contable_exception import (
    NoBalanceGeneralAvailableException,
    NoPeriodoContableAvailableException,
)
from apps.mongo.daos.periodo_contable_dao import PeriodoContableDAO
from apps.mongo.models.periodo_contable import BalanceGeneral, PeriodoContable
from apps.tools.objectid import ObjectId


class BalanceGeneralManager:
    def __init__(self) -> None:
        self._periodo_contable_dao = PeriodoContableDAO()

    async def get_balance_general_by_periodo(
        self,
        id_periodo: ObjectId,
    ) -> BalanceGeneral:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(
                item_id=id_periodo,
            )
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable con el id: {id_periodo}"
            )

        balance_general: BalanceGeneral | None = periodo_contable.balance_general

        if balance_general is None:
            raise NoBalanceGeneralAvailableException(
                f"No hay balance general disponible para el periodo contable con el id: {id_periodo}"
            )

        return balance_general

    # async def get_analisis_horizontal_by_balance_general(
    #     self,
    #     id_empresa: ObjectId,
    #     periodo_inicio: PositiveInt,
    #     periodo_fin: PositiveInt,
    # ):
    #     years: list[PositiveInt] = [
    #         periodo_inicio + i for i in range(periodo_fin - periodo_inicio + 1)
    #     ]

    #     balances_generales: list[BalanceGeneral] = []
    #     periodos_descartados = []
    #     periodos_encontrados = []
    #     for year in years:
    #         filters: Dict = {
    #             "id_empresa": id_empresa,
    #             "fecha_inicio": Date(year, 1, 1).start_of_year,
    #             "fecha_fin": Date(year, 12, 31).end_of_year,
    #         }

    #         periodo_contable: PeriodoContable | None = (
    #             await self._periodo_contable_dao.get(**filters)
    #         )

    #         if periodo_contable is None:
    #             periodos_descartados.append(year)
    #             continue

    #         balance_general: BalanceGeneral | None = (
    #             await self._balance_general_dao.get(
    #                 id_periodo=periodo_contable.id,
    #             )
    #         )

    #         if balance_general is None:
    #             periodos_descartados.append(year)
    #             continue

    #         balances_generales.append(balance_general)
    #         periodos_encontrados.append(year)

    #     analisis_horizontal = AnalisisHorizontalBalanceGeneral()
    #     excel_file = analisis_horizontal.calcular_analisis_horizontal(
    #         years=periodos_encontrados,
    #         balances=balances_generales,
    #     )

    #     return excel_file, f"analisis_horizontal_{periodo_inicio}_{periodo_fin}.xlsx"

    # async def get_analisis_vertical_by_balance_general(
    #     self,
    #     id_empresa: ObjectId,
    #     periodo_inicio: PositiveInt,
    #     periodo_fin: PositiveInt,
    # ):
    #     years: list[PositiveInt] = [
    #         periodo_inicio + i for i in range(periodo_fin - periodo_inicio + 1)
    #     ]

    #     balances_generales: list[BalanceGeneral] = []
    #     periodos_descartados = []
    #     periodos_encontrados = []
    #     for year in years:
    #         filters: Dict = {
    #             "id_empresa": id_empresa,
    #             "fecha_inicio": Date(year, 1, 1).start_of_year,
    #             "fecha_fin": Date(year, 12, 31).end_of_year,
    #         }

    #         periodo_contable: PeriodoContable | None = (
    #             await self._periodo_contable_dao.get(**filters)
    #         )

    #         if periodo_contable is None:
    #             periodos_descartados.append(year)
    #             continue

    #         balance_general: BalanceGeneral | None = (
    #             await self._balance_general_dao.get(
    #                 id_periodo=periodo_contable.id,
    #             )
    #         )

    #         if balance_general is None:
    #             periodos_descartados.append(year)
    #             continue

    #         balances_generales.append(balance_general)
    #         periodos_encontrados.append(year)

    #     analisis_vertical = AnalisisVerticalBalanceGeneral()
    #     excel_file = analisis_vertical.calcular_analisis_vertical(
    #         years=periodos_encontrados,
    #         balances=balances_generales,
    #     )

    #     return excel_file, f"analisis_vertical_{periodo_inicio}_{periodo_fin}.xlsx"

    async def create_balance_general(
        self,
        id_periodo: ObjectId,
        balance_general: BalanceGeneral,
    ) -> BalanceGeneral:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(
                item_id=id_periodo,
            )
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable con el id: {id_periodo}"
            )

        if periodo_contable.balance_general is not None:
            raise NoBalanceGeneralAvailableException(
                f"Ya existe un balance general para el periodo contable con el id: {id_periodo}"
            )

        periodo_contable.balance_general = balance_general

        mongo_update: PeriodoContable | None = await self._periodo_contable_dao.update_by_id(
            item_id=id_periodo,
            data=periodo_contable,
        )

        if mongo_update is None:
            raise MongoUpdateException(
                f"No se pudo crear el balance general para el periodo contable con el id: {id_periodo}"
            )

        return balance_general

    async def update_balance_general(
        self,
        id_periodo: ObjectId,
        balance_general: BalanceGeneral,
    ) -> BalanceGeneral:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(
                item_id=id_periodo,
            )
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable con el id: {id_periodo}"
            )

        balance: BalanceGeneral | None = periodo_contable.balance_general

        if balance is None:
            raise NoBalanceGeneralAvailableException(
                f"No hay balance general disponible para el periodo contable con el id: {id_periodo}"
            )

        periodo_contable.balance_general = balance_general

        mongo_update: PeriodoContable | None = await self._periodo_contable_dao.update_by_id(
            item_id=id_periodo,
            data=periodo_contable,
        )

        if mongo_update is None:
            raise MongoUpdateException(
                f"No se pudo actualizar el balance general para el periodo contable con el id: {id_periodo}"
            )

        return balance_general

    async def delete_balance_general(self, id_periodo: ObjectId) -> None:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(
                item_id=id_periodo,
            )
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable con el id: {id_periodo}"
            )

        balance: BalanceGeneral | None = periodo_contable.balance_general

        if balance is None:
            raise NoBalanceGeneralAvailableException(
                f"No hay balance general disponible para el periodo contable con el id: {id_periodo}"
            )

        periodo_contable.balance_general = None

        mongo_update: PeriodoContable | None = await self._periodo_contable_dao.update_by_id(
            item_id=id_periodo,
            data=periodo_contable,
        )

        if mongo_update is None:
            raise MongoUpdateException(
                f"No se pudo actualizar el balance general para el periodo contable con el id: {id_periodo}"
            )
