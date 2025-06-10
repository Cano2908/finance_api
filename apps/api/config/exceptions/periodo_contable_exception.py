from http import HTTPStatus

from apps.api.config.problems.base_problem import BaseProblem


class PeriodoContableProblem(BaseProblem):
    title: str = "Problemas al acceder con recursos de Periodo Contable"
    status: HTTPStatus = HTTPStatus.NOT_FOUND


class BasePeriodoContableException(Exception): ...


class NoPeriodoContableAvailableException(BasePeriodoContableException): ...

class NoBalanceGeneralAvailableException(BasePeriodoContableException): ...

class NoEstadoResultadosAvailableException(BasePeriodoContableException): ...
