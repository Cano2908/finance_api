import mimetypes
import posixpath
from http import HTTPStatus
from typing import Annotated, Dict

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import PositiveInt

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
from apps.api.dependencies.response_model import ResponseModel
from apps.api.middleware.validate_company import ValidateCompanyMiddleware
from apps.manager.balance_general_manager import BalanceGeneralManager
from apps.mongo.daos.balance_general_dao import BalanceGeneralDAO
from apps.mongo.models.balance_general import BalanceGeneral
from apps.tools.env import env
from apps.tools.file_manager import FileManager
from apps.tools.objectid import ObjectId

balance_general_manager = BalanceGeneralManager()

balance_general_router = APIRouter(
    prefix=posixpath.join(env.API_PREFIX, "periodo_contable"),
)


@balance_general_router.get(
    path="/{id_periodo}/balance_general/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[BalanceGeneral, None],
    operation_id="GetBalanceGeneralByPeriodo",
)
async def get_balance_general_by_periodo(
    id_periodo: ObjectId,
    filters: Annotated[
        Dict,
        Depends(
            get_model_filters(BalanceGeneral, exclude=["id", "id_periodo"]),
        ),
    ],
) -> ResponseModel[BalanceGeneral, None]:
    """
    Get balance general by periodo.
    Returns the balance general for the given periodo.
    """

    try:
        balance_general: BalanceGeneral = (
            await balance_general_manager.get_balance_general_by_periodo(
                id_periodo=id_periodo,
                filters=filters,
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Balance general retrieved successfully",
        data=balance_general,
    )


@balance_general_router.get(
    path="/balance_general/analisis_horizontal/empresa/{id_empresa}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[None, None],
    operation_id="GetAnalisisHorizontalByBalanceGeneral",
)
async def get_analisis_horizontal_by_balance_general(
    id_empresa: Annotated[
        ObjectId,
        Depends(
            ValidateCompanyMiddleware(),
        ),
    ],
    periodo_inicio: PositiveInt,
    periodo_fin: PositiveInt,
    background_tasks: BackgroundTasks,
):
    """
    Get analisis horizontal by balance general.
    Returns the analisis horizontal for the given periodo.
    """

    file_u, name = (
        await balance_general_manager.get_analisis_horizontal_by_balance_general(
            id_empresa=id_empresa,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
        )
    )

    file_manager = FileManager()
    local_path = file_manager.upload_from_bytes_and_schedule_delete(
        file_bytes=file_u.getvalue(),
        file_name=name,
        background_tasks=background_tasks,
    )

    mime_type, __ = mimetypes.guess_type(name)
    media_type = mime_type or "application/octet-stream"

    return FileResponse(
        path=local_path,
        filename=name,
        media_type=media_type,
    )


@balance_general_router.get(
    path="/balance_general/analisis_vertical/empresa/{id_empresa}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[None, None],
    operation_id="GetAnalisisVerticalByBalanceGeneral",
)
async def get_analisis_vertical_by_balance_general(
    id_empresa: Annotated[
        ObjectId,
        Depends(
            ValidateCompanyMiddleware(),
        ),
    ],
    periodo_inicio: PositiveInt,
    periodo_fin: PositiveInt,
    background_tasks: BackgroundTasks,
) -> FileResponse:
    """
    Get analisis vertical by balance general.
    Returns the analisis vertical for the given periodo.
    """

    file_u, name = (
        await balance_general_manager.get_analisis_vertical_by_balance_general(
            id_empresa=id_empresa,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
        )
    )

    file_manager = FileManager()
    local_path = file_manager.upload_from_bytes_and_schedule_delete(
        file_bytes=file_u.getvalue(),
        file_name=name,
        background_tasks=background_tasks,
    )

    mime_type, __ = mimetypes.guess_type(name)
    media_type = mime_type or "application/octet-stream"

    return FileResponse(
        path=local_path,
        filename=name,
        media_type=media_type,
    )


@balance_general_router.post(
    path="/balance_general/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseModel[BalanceGeneral, None],
    operation_id="CreateBalanceGeneral",
)
async def create_balance_general(
    balance_general: BalanceGeneral,
) -> ResponseModel[BalanceGeneral, None]:
    """
    Create balance general.
    Creates a new balance general for the given periodo.
    """

    balance_general_dao = BalanceGeneralDAO()
    created_balance_general: BalanceGeneral = await balance_general_dao.create(
        data=balance_general,
    )

    return ResponseModel(
        status=True,
        detail="Balance general created successfully",
        data=created_balance_general,
    )


@balance_general_router.put(
    path="/balance_general/{id_balance_general}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[BalanceGeneral, None],
    operation_id="UpdateBalanceGeneral",
)
async def update_balance_general(
    id_balance_general: ObjectId,
    balance_general: BalanceGeneral,
) -> ResponseModel[BalanceGeneral, None]:
    """
    Update balance general.
    Updates the balance general for the given periodo.
    """

    try:
        updated_balance_general: BalanceGeneral = (
            await balance_general_manager.update_balance_general(
                id_balance_general=id_balance_general,
                balance_general=balance_general,
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Balance general updated successfully",
        data=updated_balance_general,
    )


@balance_general_router.delete(
    path="/balance_general/{id_balance_general}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[None, None],
    operation_id="DeleteBalanceGeneral",
)
async def delete_balance_general(
    id_balance_general: ObjectId,
) -> ResponseModel[None, None]:
    """
    Delete balance general.
    Deletes the balance general for the given periodo.
    """

    try:
        await balance_general_manager.delete_balance_general(
            id_balance_general=id_balance_general
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Balance general deleted successfully",
        data=None,
    )
