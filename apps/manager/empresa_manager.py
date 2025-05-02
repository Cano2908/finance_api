from apps.api.config.exceptions.company_exception import NoCompanyAvailableException
from apps.api.config.exceptions.mongo_dao_exceptions import MongoUpdateException
from apps.mongo.daos.empresa_dao import EmpresaDAO
from apps.mongo.models.empresa import Empresa, StatusCompany
from apps.tools.objectid import ObjectId


class EmpresaManager:
    def __init__(self) -> None:
        self._empresa_dao = EmpresaDAO()

    async def get_company_by_id(self, id_empresa: ObjectId) -> Empresa:
        company: Empresa | None = await self._empresa_dao.get_by_id(item_id=id_empresa)

        if company is None:
            raise NoCompanyAvailableException(
                f"No hay proyecto disponible con el id: {id_empresa}"
            )

        return company

    async def create_company(self, company: Empresa) -> Empresa:
        return await self._empresa_dao.create(data=company)

    async def update_company(self, id_empresa: ObjectId, company: Empresa) -> Empresa:
        find_company: Empresa | None = await self._empresa_dao.get_by_id(
            item_id=id_empresa
        )

        if find_company is None:
            raise NoCompanyAvailableException(
                f"No hay Empresa disponible con el id: {id_empresa}"
            )

        updated_company: Empresa | None = await self._empresa_dao.update_by_id(
            item_id=id_empresa,
            data=company,
        )

        if updated_company is None:
            raise MongoUpdateException(
                f"No se ha podido actualizar la empresa con el id: {id_empresa}"
            )

        return updated_company

    async def delete_company(self, id_empresa: ObjectId) -> None:
        find_company: Empresa | None = await self._empresa_dao.get_by_id(
            item_id=id_empresa
        )

        if find_company is None:
            raise NoCompanyAvailableException(
                f"No hay Empresa disponible con el id: {id_empresa}"
            )

        find_company.status = StatusCompany.INACTIVO

        updated_company: Empresa | None = await self._empresa_dao.update_by_id(
            item_id=id_empresa,
            data=find_company,
        )

        if updated_company is None:
            raise MongoUpdateException(
                f"No se ha podido eliminar la empresa con el id: {id_empresa}"
            )
