import mimetypes
import posixpath
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import FileResponse

from apps.api.dependencies.response_model import ResponseModel
from apps.api.middleware.validate_company import ValidateCompanyMiddleware
from apps.manager.reporte_general_manager import ReporteGeneralManager
from apps.tools.env import env
from apps.tools.file_manager import FileManager
from apps.tools.objectid import ObjectId

reporte_general_router = APIRouter(
    prefix=posixpath.join(env.API_PREFIX, "empresa"),
)

reporte_general_manager = ReporteGeneralManager()


@reporte_general_router.get(
    path="/{id_empresa}/reporte_final/",
    status_code=HTTPStatus.OK,
    operation_id="GetReporteFinal",
)
async def get_reporte_final(
    id_empresa: Annotated[
        ObjectId,
        Depends(
            ValidateCompanyMiddleware(),
        ),
    ],
    anios: Annotated[
        list[int],
        Query(
            title="Años",
            description="Lista de años para el reporte final",
            example=[2021, 2022, 2023],
        ),
    ],
    background_tasks: BackgroundTasks,
):
    file_u, name = await reporte_general_manager.get_reporte_final(
        id_empresa=id_empresa,
        anios=anios,
    )

    file_manager = FileManager()
    local_path = file_manager.upload_from_bytes_and_schedule_delete(
        file_bytes=file_u.getvalue(),
        file_name=name,
        background_tasks=background_tasks,
    )

    mime_type, __ = mimetypes.guess_type(name)
    media_type = mime_type or "application/octet-stream"

    return FileResponse(
        path=local_path,
        filename=name,
        media_type=media_type,
    )
