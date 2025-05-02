from http import HTTPStatus
from typing import TypeVar

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from apps.api.config.problems.base_problem import BaseProblem
from apps.api.config.problems.problem_exception import Problem


def exception_handler(request, exc: Exception):
    problem = Problem[BaseProblem](
        title="Error interno del servidor",
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=str(exc),
    )

    problem_details = problem.get_problem_details(request.url.path)

    return JSONResponse(
        status_code=problem_details.status,
        content=problem_details.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )


P = TypeVar("P", bound=BaseProblem)


def problem_handler(request: Request, exc: Problem[P]) -> Response:
    problem_details = exc.get_problem_details(request.url.path)
    problem_details_dump = problem_details.model_dump(exclude_none=True)

    return JSONResponse(
        status_code=problem_details.status,
        content=problem_details_dump,
        media_type="application/problem+json",
    )
