import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def json_base_model_encoder(
    self: JSONResponse, content: Any
) -> bytes:  # pylint: disable=unused-argument
    json_string = json.dumps(
        obj=content,
        ensure_ascii=False,
        allow_nan=False,
        indent=None,
        separators=(",", ":"),
        default=jsonable_encoder,
    )
    return json_string.encode("utf-8")
