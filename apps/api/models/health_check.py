from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str
    name: str
    version: str