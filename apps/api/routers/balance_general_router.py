import posixpath
from http import HTTPStatus

from fastapi import APIRouter, UploadFile

from apps.api.config.exceptions.mongo_dao_exceptions import (
    BaseMongoDAOException,
    MongoDAOProblem,
)
from apps.api.config.exceptions.periodo_contable_exception import (
    BasePeriodoContableException,
    PeriodoContableProblem,
)
from apps.api.config.problems.problem_exception import Problem
from apps.api.dependencies.response_model import ResponseModel
from apps.manager.balance_general_manager import BalanceGeneralManager
from apps.mongo.models.extensions.balance_general import BalanceGeneral
from apps.tools.env import env
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
) -> ResponseModel[BalanceGeneral, None]:
    """
    Get balance general by periodo.
    Returns the balance general for the given periodo.
    """

    try:
        balance_general: BalanceGeneral = (
            await balance_general_manager.get_balance_general_by_periodo(
                id_periodo=id_periodo,
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Balance general retrieved successfully",
        data=balance_general,
    )


@balance_general_router.post(
    path="/{id_periodo}/balance_general/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseModel[BalanceGeneral, None],
    operation_id="CreateBalanceGeneral",
)
async def create_balance_general(
    id_periodo: ObjectId,
    balance_general: BalanceGeneral,
) -> ResponseModel[BalanceGeneral, None]:
    """
    Create balance general.
    Creates a new balance general for the given periodo.
    """

    try:
        created_balance_general: BalanceGeneral = (
            await balance_general_manager.create_balance_general(
                id_periodo=id_periodo,
                balance_general=balance_general,
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Balance general created successfully",
        data=created_balance_general,
    )


@balance_general_router.post(
    path="/{id_periodo}/balance_general/file/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseModel[BalanceGeneral, None],
    operation_id="CreateBalanceGeneralByFile",
)
async def create_balance_general_by_file(id_periodo: ObjectId, file: UploadFile):
    """
    Create balance general by file.
    Creates a new balance general for the given periodo using a file.
    """

    try:
        created_balance_general: BalanceGeneral = (
            await balance_general_manager.create_balance_general_by_file(
                id_periodo=id_periodo,
                file=file,
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Balance general created successfully",
        data=created_balance_general,
    )


@balance_general_router.put(
    path="/{id_periodo}/balance_general/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[BalanceGeneral, None],
    operation_id="UpdateBalanceGeneral",
)
async def update_balance_general(
    id_periodo: ObjectId,
    balance_general: BalanceGeneral,
) -> ResponseModel[BalanceGeneral, None]:
    """
    Update balance general.
    Updates the balance general for the given periodo.
    """

    try:
        updated_balance_general: BalanceGeneral = (
            await balance_general_manager.update_balance_general(
                id_periodo=id_periodo,
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
    path="/{id_periodo}/balance_general/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[None, None],
    operation_id="DeleteBalanceGeneral",
)
async def delete_balance_general(
    id_periodo: ObjectId,
) -> ResponseModel[None, None]:
    """
    Delete balance general.
    Deletes the balance general for the given periodo.
    """

    try:
        await balance_general_manager.delete_balance_general(id_periodo=id_periodo)
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Balance general deleted successfully",
        data=None,
    )
