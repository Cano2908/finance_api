import posixpath
from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.tools.env import env
from fastapi.middleware.cors import CORSMiddleware

API_PREFIX = env.API_PREFIX
APP_NAME = env.APP_NAME
VERSION = "0.3.1"


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)