from http import HTTPStatus
import posixpath

from fastapi import APIRouter

from apps.api.app import APP_NAME as app_name
from apps.api.app import VERSION as api_version
from apps.api.dependencies.response_model import ResponseModel
from apps.api.models.health_check import HealthCheck
from apps.tools.env import env

health_check_router = APIRouter(
    prefix=posixpath.join(env.API_PREFIX, "").removesuffix("/"),
)


@health_check_router.get(
    "/health_check/",
    status_code=HTTPStatus.OK,
    response_model=ResponseModel[HealthCheck, None],
    operation_id="HealthCheck",
)
async def health_check():
    """
    Health check endpoint.
    Returns response with the status and version of the application.
    """

    health_check = HealthCheck(
        status="OK",
        name=app_name,
        version=api_version,
    )

    return ResponseModel(
        status=True,
        detail="Health check successful",
        data=health_check,
    )
