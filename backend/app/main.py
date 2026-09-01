"""The HTTP layer: it validates, delegates, and shapes the answer.

It never computes. Arithmetic lives in `app.engine`, which has no idea this file
exists, and the JSON:API rewrite proved the boundary holds: a complete change of
wire format reached no line of the engine. See `.claude/rules/principles.md`.

Everything about the wire format comes from `openapi.yaml` through the generated
models in `app.contract`, which are never edited by hand.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Annotated, Final
from uuid import uuid4

from fastapi import Body, FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError

from app.contract import (
    CalculationRequest,
    CalculationResponse,
    ErrorCode,
    ErrorDocument,
    ErrorObject,
    ErrorSource,
    EvaluatedCalculationResource,
    ResultAttributes,
)
from app.engine import CalculationError, evaluate

MEDIA_TYPE: Final = "application/vnd.api+json"

#: A short summary, the same for every occurrence of a code, as JSON:API asks.
TITLES: Final[dict[str, str]] = {
    "MALFORMED_REQUEST": "Malformed request",
    "UNSUPPORTED_MEDIA_TYPE": "Unsupported media type",
    "VALIDATION_ERROR": "Validation error",
    "UNKNOWN_OPERATION": "Unknown operation",
    "WRONG_OPERAND_COUNT": "Wrong operand count",
    "INVALID_OPERAND": "Invalid operand",
    "OPERAND_OUT_OF_RANGE": "Operand out of range",
    "DIVISION_BY_ZERO": "Division by zero",
    "NEGATIVE_SQRT": "Square root of a negative number",
    "UNDEFINED_RESULT": "Undefined result",
    "RESULT_OVERFLOW": "Result overflow",
}

app = FastAPI(
    title="Calculator API",
    version="1.0.0",
    summary="Exact decimal arithmetic, served as JSON:API.",
    # Declared rather than inferred from root_path, so the served document states
    # the same server as the contract whether or not a proxy is in front.
    servers=[{"url": "/api"}],
    # The proxy strips this prefix, so routes are declared without it and the
    # served document carries it as a server entry, matching openapi.yaml.
    root_path="/api",
)


def error_response(
    http_status: int,
    code: str,
    detail: str,
    pointer: str | None = None,
) -> Response:
    """Every failure leaves through here, so there is exactly one error shape."""
    document = ErrorDocument(
        errors=[
            ErrorObject(
                status=str(http_status),
                code=ErrorCode(code),
                title=TITLES[code],
                detail=detail,
                source=ErrorSource(pointer=pointer) if pointer else None,
            )
        ]
    )
    return Response(
        content=document.model_dump_json(exclude_none=True),
        status_code=http_status,
        media_type=MEDIA_TYPE,
    )


def operand_pointer(index: int | None) -> str | None:
    """An RFC 6901 pointer into the request document, per JSON:API's `source`."""
    if index is None:
        return None
    return f"/data/attributes/operands/{index}"


@app.middleware("http")
async def enforce_media_type(request: Request, call_next):
    """JSON:API requires 415 for anything but its own media type, parameters included.

    A middleware rather than a dependency, because it must answer before the body
    is parsed: a wrong media type is a wrong media type whatever the body holds.
    """
    if request.method == "POST" and request.headers.get("content-type", "") != MEDIA_TYPE:
        return error_response(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "UNSUPPORTED_MEDIA_TYPE",
            f"Requests must use {MEDIA_TYPE} with no media type parameters.",
        )
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def _validation_error(_: Request, exc: RequestValidationError) -> Response:
    """Keep FastAPI's own error shape from leaking as a second format.

    Without this the service would answer schema failures in FastAPI's `detail`
    envelope and everything else in JSON:API's, and the single-error-shape
    guarantee would be false from the first bad request.

    An unparseable body and a body that parses but does not match the contract
    are different failures, so they keep different statuses: 400 for the first,
    422 for the second.
    """
    errors = exc.errors()
    first = errors[0] if errors else {}

    if first.get("type") == "json_invalid":
        return error_response(
            status.HTTP_400_BAD_REQUEST,
            "MALFORMED_REQUEST",
            "Request body is not valid JSON.",
        )

    location = [str(part) for part in first.get("loc", ()) if part != "body"]
    return error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "VALIDATION_ERROR",
        str(first.get("msg", "The request does not match the contract.")),
        pointer="/" + "/".join(location) if location else None,
    )


@app.post(
    "/calculations",
    operation_id="createCalculation",
    summary="Evaluate one arithmetic operation.",
    response_class=Response,
    responses={
        200: {"content": {MEDIA_TYPE: {"schema": CalculationResponse.model_json_schema()}}},
        400: {"content": {MEDIA_TYPE: {"schema": ErrorDocument.model_json_schema()}}},
        415: {"content": {MEDIA_TYPE: {"schema": ErrorDocument.model_json_schema()}}},
        422: {"content": {MEDIA_TYPE: {"schema": ErrorDocument.model_json_schema()}}},
    },
)
async def create_calculation(
    document: Annotated[CalculationRequest, Body(media_type=MEDIA_TYPE)],
) -> Response:
    """Evaluate one operation and return it as a JSON:API resource.

    The body is a typed parameter rather than a hand-read stream so the document
    FastAPI serves actually describes the contract. Reading it by hand left the
    served document with no request body at all, which would have made the
    API-first claim false at the one place it is checkable.
    """
    attributes = document.data.attributes.root
    operation = getattr(attributes.operation, "value", attributes.operation)
    operand_strings = [str(operand.root) for operand in attributes.operands]

    try:
        operands = [Decimal(value) for value in operand_strings]
    except InvalidOperation:
        return error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "INVALID_OPERAND",
            "Operand is not a valid decimal number.",
        )

    try:
        result = evaluate(operation, operands)
    except CalculationError as exc:
        index = exc.details.get("operand_index")
        return error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            exc.code,
            exc.message,
            pointer=operand_pointer(index if isinstance(index, int) else None),
        )

    response = CalculationResponse(
        data=EvaluatedCalculationResource(
            type="calculations",
            id=str(uuid4()),
            attributes=ResultAttributes(
                operation=operation,
                operands=operand_strings,
                result=str(result),
            ),
        )
    )
    return Response(
        content=response.model_dump_json(),
        status_code=status.HTTP_200_OK,
        media_type=MEDIA_TYPE,
    )
