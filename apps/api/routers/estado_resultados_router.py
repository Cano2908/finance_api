import posixpath
from http import HTTPStatus
from typing import Annotated, Dict

from fastapi import APIRouter, Depends

from apps.api.config.exceptions.estado_resultados_exception import (
    BaseEstadoResultadosException,
    EstadoResultadosProblem,
)
from apps.api.config.exceptions.mongo_dao_exceptions import (
    BaseMongoDAOException,
    MongoDAOProblem,
)
from apps.api.config.problems.problem_exception import Problem
from apps.api.dependencies.model_filters import get_model_filters
from apps.api.dependencies.response_model import ResponseModel
from apps.manager.estado_resultados_manager import EstadoResultadosManager
from apps.mongo.daos.estado_resultados_dao import EstadoResultadosDAO
from apps.mongo.models.estado_resultado import EstadoResultados
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
    filters: Annotated[
        Dict,
        Depends(
            get_model_filters(EstadoResultados, exclude=["id", "id_periodo"]),
        ),
    ],
) -> ResponseModel[EstadoResultados, None]:
    """
    Get estado resultados by periodo.
    Returns the estado resultados for the given periodo.
    """

    try:
        estados_resultados: EstadoResultados = (
            await estado_resultados_manager.get_estado_resultados_by_periodo(
                id_periodo=id_periodo,
                filters=filters,
            )
        )
    except BaseEstadoResultadosException as e:
        raise Problem[EstadoResultadosProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Estado resultados retrieved successfully.",
        data=estados_resultados,
    )


@estado_resultados_router.post(
    path="/estado_resultados/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[EstadoResultados, None],
    operation_id="CreateEstadoResultados",
)
async def createate_estado_resultados(
    estado_resultados: EstadoResultados,
):
    """
    Create estado resultados.
    Returns the estado resultados created.
    """

    estado_resultados_dao = EstadoResultadosDAO()
    created_estado_resultados: EstadoResultados = await estado_resultados_dao.create(
        data=estado_resultados,
    )

    return ResponseModel(
        status=True,
        detail="Estado resultados created successfully.",
        data=created_estado_resultados,
    )


@estado_resultados_router.put(
    path="/estado_resultados/{id_estado_resultados}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[EstadoResultados, None],
    operation_id="UpdateEstadoResultados",
)
async def update_estado_resultados(
    id_estado_resultados: ObjectId,
    estado_resultados: EstadoResultados,
) -> ResponseModel[EstadoResultados, None]:
    """
    Update estado resultados.
    Returns the estado resultados updated.
    """

    try:
        updated_estado_resultados: EstadoResultados = (
            await estado_resultados_manager.update_estado_resultados(
                id_estado_resultados=id_estado_resultados,
                estado_resultados=estado_resultados,
            )
        )
    except BaseEstadoResultadosException as e:
        raise Problem[EstadoResultadosProblem](detail=str(e))
    except BaseMongoDAOException as e:
        raise Problem[MongoDAOProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Estado resultados updated successfully.",
        data=updated_estado_resultados,
    )


@estado_resultados_router.delete(
    path="/estado_resultados/{id_estado_resultados}",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[None, None],
    operation_id="DeleteEstadoResultados",
)
async def delete_estado_resultados(
    id_estado_resultados: ObjectId,
) -> ResponseModel[None, None]:
    """
    Delete estado resultados.
    Returns the estado resultados deleted.
    """

    try:
        await estado_resultados_manager.delete_estado_resultados(
            id_estado_resultados=id_estado_resultados,
        )
    except BaseEstadoResultadosException as e:
        raise Problem[EstadoResultadosProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Estado resultados deleted successfully.",
        data=None,
    )
