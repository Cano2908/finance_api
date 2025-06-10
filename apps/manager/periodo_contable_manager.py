from apps.api.config.exceptions.mongo_dao_exceptions import MongoUpdateException
from apps.api.config.exceptions.periodo_contable_exception import (
    NoPeriodoContableAvailableException,
)
from apps.mongo.daos.periodo_contable_dao import PeriodoContableDAO
from apps.mongo.models.periodo_contable import PeriodoContable
from apps.tools.objectid import ObjectId


class PeriodoContableManager:
    def __init__(self) -> None:
        self._periodo_contable_dao = PeriodoContableDAO()

    async def get_periodo_contable_by_id(
        self, id_periodo_contable: ObjectId
    ) -> PeriodoContable:
        periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(item_id=id_periodo_contable)
        )

        if periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable disponible con el id: {id_periodo_contable}"
            )

        return periodo_contable

    async def create_periodo_contable(
        self, id_empresa: ObjectId, periodo_contable: PeriodoContable
    ) -> PeriodoContable:
        filters = {
            "id_empresa": id_empresa,
            "fecha_inicio": periodo_contable.fecha_inicio,
            "fecha_fin": periodo_contable.fecha_fin,
        }

        find_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get(**filters)
        )

        if find_periodo_contable is not None:
            raise NoPeriodoContableAvailableException(
                f"Ya existe un periodo contable con las fechas ingresadas: {find_periodo_contable.anio} "
            )

        return await self._periodo_contable_dao.create(data=periodo_contable)

    async def update_periodo_contable(
        self,
        _: ObjectId,
        id_periodo_contable: ObjectId,
        periodo_contable: PeriodoContable,
    ) -> PeriodoContable:
        find_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(item_id=id_periodo_contable)
        )

        if find_periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable disponible con el id: {id_periodo_contable}"
            )

        updated_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.update_by_id(
                item_id=id_periodo_contable,
                data=periodo_contable,
            )
        )

        if updated_periodo_contable is None:
            raise MongoUpdateException(
                f"No se ha podido actualizar el periodo contable con el id: {id_periodo_contable}"
            )

        return updated_periodo_contable

    async def delete_periodo_contable(
        self,
        _: ObjectId,
        id_periodo_contable: ObjectId,
    ) -> None:
        find_periodo_contable: PeriodoContable | None = (
            await self._periodo_contable_dao.get_by_id(item_id=id_periodo_contable)
        )

        if find_periodo_contable is None:
            raise NoPeriodoContableAvailableException(
                f"No hay periodo contable disponible con el id: {id_periodo_contable}"
            )

        await self._periodo_contable_dao.delete_by_id(item_id=id_periodo_contable)
