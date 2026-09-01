"""The served document against the contract.

Structural, not behavioural: these compare two documents rather than exercising
the service, so they stay ordinary pytest while the behaviour lives in Gherkin
under `features/`. See the class docstring for what each family can and cannot
catch.
"""

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from app.main import TITLES, app

JSONAPI = "application/vnd.api+json"

client = TestClient(app)

contract = yaml.safe_load((Path(__file__).parents[2] / "openapi.yaml").read_text())
served = app.openapi()


def _post(document: dict) -> dict:
    """The operation, or an empty dict, so a renamed path fails a test rather
    than raising at import and reporting as a collection error."""
    return document["paths"].get("/calculations", {}).get("post", {})


contract_post = _post(contract)
served_post = _post(served)


class TestNoDriftFromTheContract:
    """The contract is only authoritative if something checks that it is obeyed.

    `openapi.yaml` is hand-authored and `main.py` is hand-written, so neither is
    derived from the other and regenerating cannot compare them: `just generate`
    would produce identical output while a route, a status or a media type had
    quietly changed in the code. These tests are that comparison.

    Only what defines behaviour on the wire is compared. Descriptions, examples,
    titles and key order differ between a hand-written document and a generated
    one without meaning anything, so comparing them would produce noise instead
    of a signal.

    These tests catch drift in the *shape* of the interface and cannot catch
    drift in its *behaviour*. Changing the status the code returns for a wrong
    media type leaves the served document untouched, since the statuses are
    declared in the route decorator, so every test in this class still passes.
    The behavioural tests above are what catch that, and the division of labour
    is deliberate: these compare two documents, those exercise the service.
    Verified by introducing each drift and watching which suite went red.
    """

    def test_the_same_paths_are_served_as_are_promised(self):
        assert sorted(served["paths"]) == sorted(contract["paths"])

    def test_the_same_server_prefix_is_declared(self):
        assert [s["url"] for s in served["servers"]] == [s["url"] for s in contract["servers"]]

    def test_the_operation_is_named_the_same(self):
        assert served_post["operationId"] == contract_post["operationId"]

    def test_the_request_accepts_the_media_type_the_contract_promises(self):
        assert list(served_post["requestBody"]["content"]) == list(
            contract_post["requestBody"]["content"]
        )

    def test_the_same_statuses_are_answered(self):
        assert sorted(served_post["responses"]) == sorted(contract_post["responses"])

    @pytest.mark.parametrize("code", ["200", "400", "415", "422"])
    def test_each_response_uses_the_media_type_the_contract_promises(self, code: str):
        assert list(served_post["responses"][code]["content"]) == list(
            contract_post["responses"][code]["content"]
        )

    def test_every_error_code_in_the_contract_has_a_title(self):
        """The one hand-written table that the contract cannot generate.

        `TITLES` is keyed by the contract's enumeration but written by hand, so
        adding a code to the contract without adding its title would raise a
        KeyError on the first failure of that kind, in production, at the worst
        possible moment.
        """
        declared = set(contract["components"]["schemas"]["ErrorCode"]["enum"])
        assert declared == set(TITLES), declared.symmetric_difference(TITLES)
