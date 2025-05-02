from http import HTTPStatus

from apps.api.config.problems.base_problem import BaseProblem


class BalanceGeneralProblem(BaseProblem):
    title: str = "Problemas al acceder con recursos de Balance General"
    status: HTTPStatus = HTTPStatus.NOT_FOUND


class BaseBalanceGeneralException(Exception): ...


class NoBalanceGeneralAvailableException(BaseBalanceGeneralException): ...
