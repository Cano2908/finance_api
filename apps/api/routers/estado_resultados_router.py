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
from apps.manager.estado_resultados_manager import EstadoResultadosManager
from apps.mongo.models.extensions.estado_resultados import EstadoResultados
from apps.tools.env import env
from apps.tools.objectid import ObjectId

estado_resultados_manager = EstadoResultadosManager()

estado_resultados_router = APIRouter(
    prefix=posixpath.join(env.API_PREFIX, "periodo_contable"),
)


@estado_resultados_router.get(
    path="/{id_periodo}/estado_resultados/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[EstadoResultados, None],
    operation_id="GetEstadoResultadosByPeriodo",
)
async def get_estado_resultados_by_periodo(
    id_periodo: ObjectId,
) -> ResponseModel[EstadoResultados, None]:
    """
    Get estado resultados by periodo.
    Returns the estado resultados for the given periodo.
    """

    try:
        estados_resultados: EstadoResultados = (
            await estado_resultados_manager.get_estado_resultados_by_periodo(
                id_periodo=id_periodo,
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Estado resultados retrieved successfully.",
        data=estados_resultados,
    )


@estado_resultados_router.post(
    path="/{id_periodo}/estado_resultados/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[EstadoResultados, None],
    operation_id="CreateEstadoResultados",
)
async def createate_estado_resultados(
    id_periodo: ObjectId,
    estado_resultados: EstadoResultados,
):
    """
    Create estado resultados.
    Returns the estado resultados created.
    """

    try:
        created_estado_resultados: EstadoResultados = (
            await estado_resultados_manager.create_estado_resultados(
                id_periodo=id_periodo,
                estado_resultados=estado_resultados,
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Estado resultados created successfully.",
        data=created_estado_resultados,
    )


@estado_resultados_router.post(
    path="/{id_periodo}/estado_resultados/file/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseModel[EstadoResultados, None],
    operation_id="CreateEstadoResultadosByFile",
)
async def create_estado_resultados_by_file(id_periodo: ObjectId, file: UploadFile) -> ResponseModel[EstadoResultados, None]:
    """
    Create estado resultados by file.
    Returns the estado resultados created.
    """

    try:
        created_estado_resultados: EstadoResultados = (
            await estado_resultados_manager.create_estado_resultados_by_file(
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
        detail="Estado resultados created successfully.",
        data=created_estado_resultados,
    )


@estado_resultados_router.put(
    path="/{id_periodo}/estado_resultados/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[EstadoResultados, None],
    operation_id="UpdateEstadoResultados",
)
async def update_estado_resultados(
    id_periodo: ObjectId,
    estado_resultados: EstadoResultados,
) -> ResponseModel[EstadoResultados, None]:
    """
    Update estado resultados.
    Returns the estado resultados updated.
    """

    try:
        updated_estado_resultados: EstadoResultados = (
            await estado_resultados_manager.update_estado_resultados(
                id_periodo=id_periodo,
                estado_resultados=estado_resultados,
            )
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Estado resultados updated successfully.",
        data=updated_estado_resultados,
    )


@estado_resultados_router.delete(
    path="/{id_periodo}/estado_resultados/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[None, None],
    operation_id="DeleteEstadoResultados",
)
async def delete_estado_resultados(
    id_periodo: ObjectId,
) -> ResponseModel[None, None]:
    """
    Delete estado resultados.
    Returns the estado resultados deleted.
    """

    try:
        await estado_resultados_manager.delete_estado_resultados(
            id_periodo=id_periodo,
        )
    except BasePeriodoContableException as e:
        raise Problem[PeriodoContableProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Estado resultados deleted successfully.",
        data=None,
    )
