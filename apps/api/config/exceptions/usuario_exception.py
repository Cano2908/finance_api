from http import HTTPStatus

from apps.api.config.problems.base_problem import BaseProblem


class UsuarioProblem(BaseProblem):
    title: str = "Problemas al acceder con recursos de Usuario"
    status: HTTPStatus = HTTPStatus.NOT_FOUND


class BaseUsuarioException(Exception): ...


class NoUsuarioAvailableException(BaseUsuarioException): ...
