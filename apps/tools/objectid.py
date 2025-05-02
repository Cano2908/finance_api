from typing import Any

import bson
import bson.errors
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class ObjectId(bson.ObjectId):
    """Custom ObjectId type with Pydantic support.

    This type is used to validate and serialize ObjectId values in Pydantic models.

    - Automatically validates strings and ObjectId instances as valid ObjectId values.
    - Automatically serializes ObjectId instances as strings when dumping to JSON.

    Also supported by FastAPI's JSON Schema generation.

    Example:

    ```
    class MyModel(BaseModel):
        my_field: ObjectId

    model = MyModel(my_field="65a804bc2828cacc454c7d53")

    model.my_field  # ObjectId('65a804bc2828cacc454c7d53')

    model.model_dump()  # {'my_field': ObjectId('65a804bc2828cacc454c7d53')}

    model.model_dump_json()  # '{"my_field": "65a804bc2828cacc454c7d53"}'
    ```

    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        We return a pydantic_core.CoreSchema that behaves in the following ways:

        * strings will be parsed as `ObjectId`
        * `ObjectId` instances will be parsed as `ObjectId` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a string
        """

        def validate_from_str(value: str) -> bson.ObjectId:
            try:
                result = bson.ObjectId(value)
                return result
            except bson.errors.InvalidId as e:
                raise ValueError(
                    f"'{value}' no es un ObjectId válido, por favor proporcione un ObjectId válido."
                ) from e

        def serialize(valuse: bson.ObjectId) -> str:
            return str(valuse)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        schema_objectid = core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(bson.ObjectId),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize, when_used="json"
            ),
        )

        return schema_objectid

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        schema_objectid = handler(core_schema.str_schema())
        schema_objectid.update(
            {"description": "A BSON ObjectId represented as a string"}
        )
        return schema_objectid
