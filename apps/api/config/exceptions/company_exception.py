from http import HTTPStatus

from apps.api.config.problems.base_problem import BaseProblem


class CompanyProblem(BaseProblem):
    title: str = "Problemas al acceder con recursos de Empresa"
    status: HTTPStatus = HTTPStatus.NOT_FOUND


class BaseCompanyException(Exception): ...


class NoCompanyAvailableException(BaseCompanyException):
    """
    Exception raised when no company is available.
    """
