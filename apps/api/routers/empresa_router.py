import posixpath
from http import HTTPStatus
from typing import Annotated, Dict

from fastapi import APIRouter, Depends

from apps.api.config.exceptions.company_exception import (
    BaseCompanyException,
    CompanyProblem,
)
from apps.api.config.exceptions.mongo_dao_exceptions import (
    BaseMongoDAOException,
    MongoDAOProblem,
)
from apps.api.config.problems.problem_exception import Problem
from apps.api.dependencies.model_filters import get_model_filters
from apps.api.dependencies.pagination_filters import PaginatorCallable, get_paginator
from apps.api.dependencies.response_model import ResponseModel
from apps.manager.empresa_manager import EmpresaManager
from apps.mongo.daos.empresa_dao import EmpresaDAO
from apps.mongo.models.empresa import Empresa
from apps.tools.env import env
from apps.tools.objectid import ObjectId
from apps.tools.paginator import PaginationMetadata

company_manager = EmpresaManager()

company_router = APIRouter(
    prefix=posixpath.join(env.API_PREFIX, "empresa"),
)


@company_router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[list[Empresa], PaginationMetadata],
    operation_id="GetAllCompanies",
)
async def get_all_companies(
    filters: Annotated[
        Dict,
        Depends(
            get_model_filters(Empresa, exclude=["id", "descripcion", "fecha_creacion"]),
        ),
    ],
    paginator: Annotated[PaginatorCallable[Empresa], Depends(get_paginator(Empresa))],
) -> ResponseModel[list[Empresa], PaginationMetadata]:
    """
    Get all companies.
    Returns a list of all companies in the database.
    """

    company_dao = EmpresaDAO()
    companies: list[Empresa] = await company_dao.get_all(**filters)

    companies, pagination_metadata = paginator(companies)
    return ResponseModel(
        status=True,
        detail="Companies retrieved successfully",
        data=companies,
        metadata=pagination_metadata,
    )


@company_router.get(
    "/{id_empresa}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[Empresa, None],
    operation_id="GetCompanyById",
)
async def get_company_by_id(id_empresa: ObjectId):
    """
    Get company by id.
    Returns a company with the given id.
    """

    try:
        company: Empresa = await company_manager.get_company_by_id(
            id_empresa=id_empresa
        )
    except BaseCompanyException as e:
        raise Problem[CompanyProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Company retrieved successfully",
        data=company,
    )


@company_router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseModel[Empresa, None],
    operation_id="CreateCompany",
)
async def create_company(company: Empresa) -> ResponseModel[Empresa, None]:
    """
    Create a new company.
    Returns the created company.
    """

    created_company: Empresa = await company_manager.create_company(company=company)

    return ResponseModel(
        status=True,
        detail="Company created successfully",
        data=created_company,
    )


@company_router.put(
    "/{id_empresa}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[Empresa, None],
    operation_id="UpdateCompany",
)
async def update_company(
    id_empresa: ObjectId,
    company: Empresa,
) -> ResponseModel[Empresa, None]:
    """
    Update a company by id.
    Returns the updated company.
    """

    try:
        updated_company: Empresa = await company_manager.update_company(
            id_empresa=id_empresa,
            company=company,
        )
    except BaseCompanyException as e:
        raise Problem[CompanyProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Company updated successfully",
        data=updated_company,
    )


@company_router.delete(
    "/{id_empresa}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[None, None],
    operation_id="DeleteCompany",
)
async def delete_company(id_empresa: ObjectId) -> ResponseModel[None, None]:
    """
    Delete a company by id.
    Returns a message indicating the company was deleted successfully.
    """

    try:
        await company_manager.delete_company(id_empresa=id_empresa)
    except BaseCompanyException as e:
        raise Problem[CompanyProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Company deleted successfully",
        data=None,
    )
