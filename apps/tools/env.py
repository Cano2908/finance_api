import os
from typing import Protocol, TypeVar, runtime_checkable


@runtime_checkable
class Stringifiable(Protocol):
    def __str__(self) -> str: ...


T = TypeVar("T")


class MetaEnv(type):
    """
    A metaclass that provides dynamic attribute access to environment variables.

    This metaclass allows accessing environment variables as attributes of a class.
    If an attribute is not found, it checks if there is a corresponding environment variable
    with the same name and returns its value. If the environment variable is not found,
    it raises a `MissingEnvVarException`.

    Attributes:
        __getattr__ (classmethod): Retrieves the value of an environment variable.
        __setattr__ (classmethod): Sets the value of an environment variable.

    Raises:
        AttributeError: If the attribute starts and ends with double underscores.
        MissingEnvVarException: If the environment variable is not found.

    Note:
        This metaclass assumes that all environment variable values are of type string.
    """

    @classmethod
    def __getattr__(cls, __name: str) -> str:
        # special case for pytest fixtures
        if __name == "_pytestfixturefunction":
            raise AttributeError

        if __name.startswith("__") and __name.endswith("__"):
            raise AttributeError
        value = os.getenv(__name)
        if not value:
            raise MissingEnvVarException(__name)
        return value

    @classmethod
    def __setattr__(cls, __name: str, value: str | Stringifiable) -> None:  # type: ignore
        if not isinstance(value, (str, Stringifiable)):
            raise TypeError("Value must be a string or an Stringifiable object.")
        if isinstance(value, Stringifiable):
            value = str(value)

        os.environ[__name] = value


class env(metaclass=MetaEnv):
    """
    env class to handle environment variables

    This class provides methods to get and set environment variables.

    Usage:
    - Get an environment variable (through the attribute name):

        ```
        variable = env.VARIABLE_NAME
        # If the variable does not exist, a MissingEnvVarException is raised
        ```

    - Get an environment variable (through the get method):

        ```
        variable = env.get("VARIABLE_NAME")
        # If the variable does not exist, None is returned

        variable = env.get("VARIABLE_NAME", "value")
        # If the variable does not exist, the default value "value" is returned
        ```

    - Set an environment variable:

        ```
        env.VARIABLE_NAME = "value"
        ```
    """

    @classmethod
    def get(cls, __name: str, default: T = None) -> str | T:
        """
        Method to get an environment variable.

        Args:
            __name (str): The name of the variable.
            default (str | None, optional): The default value to return if the variable does not exist. Defaults to None.

        Returns:
            str | None: The value of the environment variable, or None if it does not exist and no default value is specified.
        """
        value = os.getenv(__name)
        if not value:
            return default
        return value


class MissingEnvVarException(BaseException):
    """Exception raised for missing environment variables."""

    def __init__(self, var_name) -> None:
        """Exception raised for missing environment variables."""
        self.message = f"Environment variable {var_name} not found."
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
