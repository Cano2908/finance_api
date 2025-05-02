from http import HTTPStatus

from apps.api.config.problems.base_problem import BaseProblem


class EstadoResultadosProblem(BaseProblem):
    title: str = "Problemas al acceder con recursos de Estado Resultados"
    status: HTTPStatus = HTTPStatus.NOT_FOUND


class BaseEstadoResultadosException(Exception): ...


class NoEstadoResultadosAvailableException(BaseEstadoResultadosException): ...
