import posixpath
from http import HTTPStatus
from typing import Annotated, Dict

from fastapi import APIRouter, Depends

from apps.api.config.exceptions.mongo_dao_exceptions import (
    BaseMongoDAOException,
    MongoDAOProblem,
)
from apps.api.config.exceptions.periodo_contable_exception import (
    BasePeriodoContableException,
    PeriodoContableProblem,
)
from apps.api.config.problems.problem_exception import Problem
from apps.api.dependencies.model_filters import get_model_filters
from apps.api.dependencies.pagination_filters import PaginatorCallable, get_paginator
from apps.api.dependencies.response_model import ResponseModel
from apps.api.middleware.validate_company import ValidateCompanyMiddleware
from apps.manager.periodo_contable_manager import PeriodoContableManager
from apps.mongo.daos.periodo_contable_dao import PeriodoContableDAO
from apps.mongo.models.periodo_contable import PeriodoContable
from apps.tools.env import env
from apps.tools.objectid import ObjectId
from apps.tools.paginator import PaginationMetadata

periodo_contable_manager = PeriodoContableManager()

periodo_contable_router = APIRouter(prefix=posixpath.join(env.API_PREFIX, "empresa"))


@periodo_contable_router.get(
    path="/{id_empresa}/periodo_contable/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[list[PeriodoContable], PaginationMetadata],
    operation_id="GetAllPeriodosContables",
)
async def get_all_periodos_contables(
    id_empresa: Annotated[
        ObjectId,
        Depends(
            ValidateCompanyMiddleware(),
        ),
    ],
    filters: Annotated[
        Dict,
        Depends(
            get_model_filters(PeriodoContable, exclude=["id", "id_empresa"]),
        ),
    ],
    paginator: Annotated[
        PaginatorCallable[PeriodoContable], Depends(get_paginator(PeriodoContable))
    ],
) -> ResponseModel[list[PeriodoContable], PaginationMetadata]:
    """
    Get all periodos contables.
    Returns a list of all periodos contables in the database.
    """

    filters = {
        **filters,
        "id_empresa": id_empresa,
    }

    periodo_contable_dao = PeriodoContableDAO()
    periodos_contables: list[PeriodoContable] = await periodo_contable_dao.get_all(
        **filters
    )

    periodos_contables, pagination_metadata = paginator(periodos_contables)
    return ResponseModel(
        status=True,
        detail="Periodos contables retrieved successfully",
        data=periodos_contables,
        metadata=pagination_metadata,
    )


@periodo_contable_router.post(
    path="/{id_empresa}/periodo_contable/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseModel[PeriodoContable, None],
    operation_id="CreatePeriodoContable",
)
async def create_periodo_contable(
    id_empresa: Annotated[
        ObjectId,
        Depends(
            ValidateCompanyMiddleware(),
        ),
    ],
    periodo_contable: PeriodoContable,
) -> ResponseModel[PeriodoContable, None]:
    """
    Create a new periodo contable.
    Returns the created periodo contable.
    """

    try:
        periodo_contable_created: PeriodoContable = (
            await periodo_contable_manager.create_periodo_contable(
                id_empresa=id_empresa, periodo_contable=periodo_contable
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Periodo contable created successfully",
        data=periodo_contable_created,
    )


@periodo_contable_router.put(
    path="/{id_empresa}/periodo_contable/{id_periodo_contable}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[PeriodoContable, None],
    operation_id="UpdatePeriodoContable",
)
async def update_periodo_contable(
    id_periodo_contable: ObjectId,
    id_empresa: Annotated[
        ObjectId,
        Depends(
            ValidateCompanyMiddleware(),
        ),
    ],
    periodo_contable: PeriodoContable,
) -> ResponseModel[PeriodoContable, None]:
    """
    Update a periodo contable.
    Returns the updated periodo contable.
    """

    try:
        periodo_contable_updated: PeriodoContable = (
            await periodo_contable_manager.update_periodo_contable(
                _=id_empresa,
                id_periodo_contable=id_periodo_contable,
                periodo_contable=periodo_contable,
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Periodo contable updated successfully",
        data=periodo_contable_updated,
    )


@periodo_contable_router.delete(
    path="/{id_empresa}/periodo_contable/{id_periodo_contable}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[None, None],
    operation_id="DeletePeriodoContable",
)
async def delete_periodo_contable(
    id_periodo_contable: ObjectId,
    id_empresa: Annotated[
        ObjectId,
        Depends(
            ValidateCompanyMiddleware(),
        ),
    ],
) -> ResponseModel[None, None]:
    """
    Delete a periodo contable.
    Returns a message indicating the deletion status.
    """

    try:
        await periodo_contable_manager.delete_periodo_contable(
            _=id_empresa,
            id_periodo_contable=id_periodo_contable,
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Periodo contable deleted successfully",
    )
