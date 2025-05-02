from apps.api.config.exceptions.company_exception import NoCompanyAvailableException
from apps.api.config.exceptions.mongo_dao_exceptions import MongoUpdateException
from apps.mongo.daos.empresa_dao import EmpresaDAO
from apps.mongo.models.empresa import Empresa, StatusCompany
from apps.tools.objectid import ObjectId


class EmpresaManager:
    def __init__(self) -> None:
        self._empresa_dao = EmpresaDAO()

    async def get_empresa_by_id(self, id_empresa: ObjectId) -> Empresa:
        empresa: Empresa | None = await self._empresa_dao.get_by_id(item_id=id_empresa)

        if empresa is None:
            raise NoCompanyAvailableException(
                f"No hay proyecto disponible con el id: {id_empresa}"
            )

        return empresa

    async def create_empresa(self, company: Empresa) -> Empresa:
        return await self._empresa_dao.create(data=company)

    async def update_empresa(self, id_empresa: ObjectId, company: Empresa) -> Empresa:
        find_empresa: Empresa | None = await self._empresa_dao.get_by_id(
            item_id=id_empresa
        )

        if find_empresa is None:
            raise NoCompanyAvailableException(
                f"No hay Empresa disponible con el id: {id_empresa}"
            )

        updated_empresa: Empresa | None = await self._empresa_dao.update_by_id(
            item_id=id_empresa,
            data=company,
        )

        if updated_empresa is None:
            raise MongoUpdateException(
                f"No se ha podido actualizar la empresa con el id: {id_empresa}"
            )

        return updated_empresa

    async def delete_empresa(self, id_empresa: ObjectId) -> None:
        find_empresa: Empresa | None = await self._empresa_dao.get_by_id(
            item_id=id_empresa
        )

        if find_empresa is None:
            raise NoCompanyAvailableException(
                f"No hay Empresa disponible con el id: {id_empresa}"
            )

        find_empresa.status = StatusCompany.INACTIVO

        updated_empresa: Empresa | None = await self._empresa_dao.update_by_id(
            item_id=id_empresa,
            data=find_empresa,
        )

        if updated_empresa is None:
            raise MongoUpdateException(
                f"No se ha podido eliminar la empresa con el id: {id_empresa}"
            )
