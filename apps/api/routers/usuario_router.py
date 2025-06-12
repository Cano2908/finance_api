import posixpath
from http import HTTPStatus

from fastapi import APIRouter

from apps.api.config.exceptions.usuario_exception import (
    BaseUsuarioException,
    UsuarioProblem,
)
from apps.api.config.problems.problem_exception import Problem
from apps.api.dependencies.response_model import ResponseModel
from apps.manager.usuario_manager import UsuarioManager
from apps.mongo.models.user import Usuario
from apps.tools.env import env

usuario_router = APIRouter(prefix=posixpath.join(env.API_PREFIX, "auth"))

usuario_manager = UsuarioManager()


@usuario_router.get(
    path="/login/{nom_user}/{contrasenia}/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[Usuario, None],
    operation_id="GetUsuario",
)
async def get_usuario(nom_user: str, contrasenia: str) -> ResponseModel[Usuario, None]:
    try:
        usuario: Usuario = await usuario_manager.get_user(
            nom_user=nom_user, contrasenia=contrasenia
        )
    except BaseUsuarioException as e:
        raise Problem[UsuarioProblem](detail=str(e))

    return ResponseModel(
        status=True,
        detail="Periodo contable retrieved successfully",
        data=usuario,
    )
