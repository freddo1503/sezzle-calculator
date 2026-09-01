"""The HTTP layer, tested against the contract rather than the implementation.

Every assertion here traces to something `openapi.yaml` states: the media type,
the document shape, the status codes, the error codes and the JSON Pointers. If
a test needs changing because the implementation changed, the test was wrong.
"""

from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.main import app

JSONAPI = "application/vnd.api+json"

client = TestClient(app)


def post(attributes: object, content_type: str = JSONAPI):
    return client.post(
        "/calculations",
        content=__import__("json").dumps(
            {"data": {"type": "calculations", "attributes": attributes}}
        ),
        headers={"Content-Type": content_type},
    )


def calculate(operation: str, *operands: str):
    return post({"operation": operation, "operands": list(operands)})


def only_error(response) -> dict:
    body = response.json()
    assert "data" not in body, "JSON:API forbids data and errors from coexisting"
    assert len(body["errors"]) == 1
    return body["errors"][0]


class TestSuccess:
    def test_the_exact_answer_crosses_the_wire_intact(self):
        response = calculate("add", "0.1", "0.2")
        assert response.status_code == 200
        assert response.json()["data"]["attributes"]["result"] == "0.3"

    def test_the_response_uses_the_jsonapi_media_type(self):
        assert calculate("add", "1", "1").headers["content-type"].startswith(JSONAPI)

    def test_the_response_is_a_jsonapi_resource(self):
        data = calculate("multiply", "6", "7").json()["data"]
        assert data["type"] == "calculations"
        assert UUID(data["id"])

    def test_the_request_is_echoed_back_since_nothing_is_stored(self):
        attributes = calculate("subtract", "10", "3").json()["data"]["attributes"]
        assert attributes["operation"] == "subtract"
        assert attributes["operands"] == ["10", "3"]
        assert attributes["result"] == "7"

    def test_a_unary_operation_takes_one_operand(self):
        assert calculate("sqrt", "9").json()["data"]["attributes"]["result"] == "3"

    def test_full_precision_is_returned_not_a_rounded_value(self):
        result = calculate("divide", "1", "3").json()["data"]["attributes"]["result"]
        assert result.startswith("0.3333333333333333333333333333")

    def test_every_identifier_is_distinct(self):
        first = calculate("add", "1", "1").json()["data"]["id"]
        second = calculate("add", "1", "1").json()["data"]["id"]
        assert first != second


class TestMediaType:
    def test_a_plain_json_content_type_is_refused(self):
        response = post({"operation": "add", "operands": ["1", "1"]}, "application/json")
        assert response.status_code == 415
        assert only_error(response)["code"] == "UNSUPPORTED_MEDIA_TYPE"

    def test_media_type_parameters_are_refused_as_the_specification_requires(self):
        response = post({"operation": "add", "operands": ["1", "1"]}, f"{JSONAPI}; charset=utf-8")
        assert response.status_code == 415

    def test_an_error_response_also_uses_the_jsonapi_media_type(self):
        response = post({"operation": "add", "operands": ["1", "1"]}, "text/plain")
        assert response.headers["content-type"].startswith(JSONAPI)


class TestRejectedRequests:
    def test_an_unparseable_body_is_a_400(self):
        response = client.post(
            "/calculations", content="{not json", headers={"Content-Type": JSONAPI}
        )
        assert response.status_code == 400
        assert only_error(response)["code"] == "MALFORMED_REQUEST"

    def test_a_schema_violation_is_a_422_in_our_envelope_not_fastapi_s(self):
        response = client.post(
            "/calculations", json={"nonsense": True}, headers={"Content-Type": JSONAPI}
        )
        assert response.status_code == 422
        error = only_error(response)
        assert error["code"] == "VALIDATION_ERROR"
        assert error["status"] == "422"

    @pytest.mark.parametrize(
        ("operation", "operands"),
        [("add", ["1"]), ("add", ["1", "2", "3"]), ("sqrt", ["1", "2"])],
    )
    def test_the_contract_rejects_the_wrong_operand_count(self, operation, operands):
        response = post({"operation": operation, "operands": operands})
        assert response.status_code == 422

    def test_an_unknown_operation_is_rejected_by_the_contract(self):
        assert post({"operation": "tetrate", "operands": ["2", "3"]}).status_code == 422

    def test_an_operand_that_is_not_a_decimal_is_rejected(self):
        assert calculate("add", "1", "abc").status_code == 422

    def test_scientific_notation_is_not_accepted(self):
        assert calculate("add", "1e10", "1").status_code == 422

    def test_an_operand_beyond_the_declared_bound_is_rejected(self):
        assert calculate("add", "9" * 26, "1").status_code == 422


class TestDomainErrors:
    def test_division_by_zero_points_at_the_divisor(self):
        response = calculate("divide", "1", "0")
        assert response.status_code == 422
        error = only_error(response)
        assert error["code"] == "DIVISION_BY_ZERO"
        assert error["source"]["pointer"] == "/data/attributes/operands/1"

    def test_a_negative_square_root_points_at_its_only_operand(self):
        response = calculate("sqrt", "-1")
        assert response.status_code == 422
        error = only_error(response)
        assert error["code"] == "NEGATIVE_SQRT"
        assert error["source"]["pointer"] == "/data/attributes/operands/0"

    def test_a_negative_base_with_a_fractional_exponent_is_undefined(self):
        assert only_error(calculate("power", "-8", "0.5"))["code"] == "UNDEFINED_RESULT"

    def test_a_result_too_large_for_the_context_overflows(self):
        huge = "9" * 25
        assert only_error(calculate("power", huge, huge))["code"] == "RESULT_OVERFLOW"

    def test_an_error_carries_a_title_and_a_detail(self):
        error = only_error(calculate("divide", "1", "0"))
        assert error["title"]
        assert error["detail"]
        assert error["title"] != error["detail"]


class TestContract:
    def test_the_served_document_declares_the_same_path_as_the_contract(self):
        assert "/calculations" in app.openapi()["paths"]

    def test_the_served_document_declares_the_jsonapi_media_type(self):
        operation = app.openapi()["paths"]["/calculations"]["post"]
        assert JSONAPI in operation["requestBody"]["content"]
