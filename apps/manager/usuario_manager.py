from typing import Dict

from apps.api.config.exceptions.usuario_exception import NoUsuarioAvailableException
from apps.mongo.daos.usuario_dao import UsuarioDAO
from apps.mongo.models.user import Usuario


class UsuarioManager:
    def __init__(self) -> None:
        self._usuario_dao = UsuarioDAO()

    async def get_user(self, nom_user: str, contrasenia: str) -> Usuario:
        filters: Dict = {"nom_usuario": nom_user, "contrasenia": contrasenia}

        user: Usuario | None = await self._usuario_dao.get(**filters)

        if user is None:
            raise NoUsuarioAvailableException(
                f"Usuario o contraseña incorrectos, favor de validar"
            )

        return user
