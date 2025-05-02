from http import HTTPStatus

from apps.api.config.problems.base_problem import BaseProblem


class MongoDAOProblem(BaseProblem):
    title: str = "Problemas al acceder con recursos de MongoDAO"
    status: HTTPStatus = HTTPStatus.FORBIDDEN


class BaseMongoDAOException(Exception): ...


class MongoUpdateException(BaseMongoDAOException):
    """
    Exception raised when an update operation fails.
    """
