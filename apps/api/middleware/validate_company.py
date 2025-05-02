from apps.api.config.exceptions.company_exception import CompanyProblem
from apps.api.config.problems.problem_exception import Problem
from apps.mongo.daos.empresa_dao import EmpresaDAO
from apps.mongo.models.empresa import Empresa, StatusCompany
from apps.tools.objectid import ObjectId


class ValidateCompanyMiddleware:
    def __init__(self):
        self._empresa_dao = EmpresaDAO()

    async def __call__(self, id_empresa: ObjectId) -> ObjectId:
        """
        Validate if the company exists in the database.
        """
        company: Empresa | None = await self._empresa_dao.get_by_id(item_id=id_empresa)

        if company is None:
            raise Problem[CompanyProblem](
                f"No hay empresa disponible con el id: {id_empresa}"
            )

        if company.status == StatusCompany.INACTIVO:
            raise Problem[CompanyProblem](
                f"La empresa con el id: {id_empresa} está inactiva"
            )

        return id_empresa
