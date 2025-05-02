from typing import Any
from uuid import UUID

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class UUIDStr(UUID):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        We return a pydantic_core.CoreSchema that behaves in the following ways:

        * strings will be parsed as `UUID`
        * `UUID` instances will be parsed as `UUID` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a string
        """

        def validate_from_str(value: str) -> UUID:
            try:
                result = UUID(value)
                return result
            except ValueError as e:
                raise ValueError(
                    f"'{value}' no es un UUID válido, por favor proporcione un UUID válido."
                ) from e

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        schema_uuid = core_schema.json_or_python_schema(
            json_schema={
                **from_str_schema,
            },
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(UUID),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )

        return schema_uuid

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        schema_uuid = handler(core_schema.str_schema())
        schema_uuid.update({"description": "A UUID represented as a string"})
        return schema_uuid
