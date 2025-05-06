import posixpath
from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.tools.env import env

API_PREFIX = env.API_PREFIX
APP_NAME = env.APP_NAME
VERSION = "0.3.0"


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("La aplicación ha iniciado correctamente...")
    yield
    print("La aplicación está cerrando...")


app = FastAPI(
    title=APP_NAME,
    docs_url=posixpath.join(API_PREFIX, "docs"),
    redoc_url=posixpath.join(API_PREFIX, "redoc"),
    openapi_url=posixpath.join(API_PREFIX, "openapi.json"),
    version=VERSION,
    lifespan=lifespan,
)
