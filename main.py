from fastapi import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse

from apps.api.app import app
from apps.api.config.exceptions.exception_handlers import (
    exception_handler,
    problem_handler,
)
from apps.api.config.exceptions.json_encoder import json_base_model_encoder
from apps.api.config.problems.problem_exception import Problem
from apps.api.routers.balance_general_router import balance_general_router
from apps.api.routers.empresa_router import empresa_router
from apps.api.routers.estado_resultados_router import estado_resultados_router
from apps.api.routers.health_check_router import health_check_router
from apps.api.routers.periodo_contable_router import periodo_contable_router
from apps.api.routers.usuario_router import usuario_router
from apps.tools.env import env

DEV_MODE = env.DEV_MODE


JSONResponse.media_type = "application/json; charset=utf-8"
JSONResponse.render = json_base_model_encoder

app.include_router(health_check_router, tags=["Health Check"])
app.include_router(empresa_router, tags=["Empresa"])
app.include_router(periodo_contable_router, tags=["Periodo Contable"])
app.include_router(balance_general_router, tags=["Balance General"])
app.include_router(estado_resultados_router, tags=["Estado Resultados"])
app.include_router(usuario_router, tags=["Usuarios"])

app.exception_handler(Exception)(exception_handler)
app.exception_handler(HTTPException)(http_exception_handler)
app.exception_handler(Problem)(problem_handler)
