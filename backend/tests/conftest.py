"""Step definitions shared by every feature.

The steps speak about calculations and answers, not about JSON keys, so a
scenario reads as behaviour and the shape of the document stays in one place
here. See ADR-0005 and ADR-0010 for what that shape is.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then, when

from app.main import app

JSONAPI = "application/vnd.api+json"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def request_state() -> dict[str, Any]:
    """What the Given steps build and the When steps send."""
    return {"media_type": JSONAPI, "body": None, "attributes": None}


def document(attributes: object) -> str:
    return json.dumps({"data": {"type": "calculations", "attributes": attributes}})


def error_of(response) -> dict:
    body = response.json()
    assert body["errors"], "a failure must carry at least one error object"
    return body["errors"][0]


# --------------------------------------------------------------- given


@given(parsers.parse('a calculation applying "{operation}" to "{a}" and "{b}"'))
def binary_calculation(request_state, operation: str, a: str, b: str) -> None:
    request_state["attributes"] = {"operation": operation, "operands": [a, b]}
    request_state["body"] = document(request_state["attributes"])


@given(parsers.parse('a calculation applying "{operation}" to "{a}"'))
def unary_calculation(request_state, operation: str, a: str) -> None:
    request_state["attributes"] = {"operation": operation, "operands": [a]}
    request_state["body"] = document(request_state["attributes"])


@given(parsers.parse('a calculation applying "{operation}" to the operands {operands}'))
def calculation_with_operands(request_state, operation: str, operands: str) -> None:
    parsed = [value.strip().strip('"') for value in operands.split(",")]
    request_state["body"] = document({"operation": operation, "operands": parsed})


@given(parsers.parse('the request declares the media type "{media_type}"'))
def declared_media_type(request_state, media_type: str) -> None:
    request_state["media_type"] = media_type


@given("a request body that is not valid JSON")
def malformed_body(request_state) -> None:
    request_state["body"] = "{not json"


@given("a request body that parses but does not match the contract")
def off_contract_body(request_state) -> None:
    request_state["body"] = json.dumps({"nonsense": True})


# ---------------------------------------------------------------- when


def submit(client: TestClient, request_state) -> Any:
    return client.post(
        "/calculations",
        content=request_state["body"],
        headers={"Content-Type": request_state["media_type"]},
    )


@when("the calculation is submitted", target_fixture="response")
@when("the request is submitted", target_fixture="response")
def submit_request(client, request_state):
    return submit(client, request_state)


@when("a valid calculation is submitted with that media type", target_fixture="response")
def submit_valid_with_media_type(client, request_state):
    request_state["body"] = document({"operation": "add", "operands": ["1", "1"]})
    return submit(client, request_state)


@when("the calculation is submitted twice", target_fixture="responses")
def submit_twice(client, request_state):
    return [submit(client, request_state), submit(client, request_state)]


# ---------------------------------------------------------------- then


@then(parsers.parse("the response status is {status:d}"))
def status_is(response, status: int) -> None:
    assert response.status_code == status, response.text


@then(parsers.parse('the result is exactly "{expected}"'))
def result_is(response, expected: str) -> None:
    assert response.status_code == 200, response.text
    assert response.json()["data"]["attributes"]["result"] == expected


@then(parsers.parse('the result begins with "{prefix}"'))
def result_begins_with(response, prefix: str) -> None:
    assert response.json()["data"]["attributes"]["result"].startswith(prefix)


@then("the response uses the JSON:API media type")
def response_media_type(response) -> None:
    assert response.headers["content-type"].startswith(JSONAPI)


@then(parsers.parse('the resource type is "{expected}"'))
def resource_type_is(response, expected: str) -> None:
    assert response.json()["data"]["type"] == expected


@then("the resource carries an identifier")
def resource_has_identifier(response) -> None:
    from uuid import UUID

    assert UUID(response.json()["data"]["id"])


@then(parsers.parse('the echoed operation is "{expected}"'))
def echoed_operation(response, expected: str) -> None:
    assert response.json()["data"]["attributes"]["operation"] == expected


@then(parsers.parse('the echoed operands are "{a}" and "{b}"'))
def echoed_operands(response, a: str, b: str) -> None:
    assert response.json()["data"]["attributes"]["operands"] == [a, b]


@then("the two identifiers differ")
def identifiers_differ(responses) -> None:
    first, second = (r.json()["data"]["id"] for r in responses)
    assert first != second


@then(parsers.parse('the error code is "{code}"'))
def error_code_is(response, code: str) -> None:
    assert error_of(response)["code"] == code, response.text


@then(parsers.parse('the error points at "{pointer}"'))
def error_points_at(response, pointer: str) -> None:
    assert error_of(response)["source"]["pointer"] == pointer


@then("the response holds no data alongside its errors")
def no_data_with_errors(response) -> None:
    assert "data" not in response.json(), "JSON:API forbids data and errors from coexisting"


@then("the error carries a title and a detail that differ")
def title_and_detail_differ(response) -> None:
    error = error_of(response)
    assert error["title"] and error["detail"]
    assert error["title"] != error["detail"]
