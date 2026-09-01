"""Binds the Gherkin features to pytest.

The scenarios live in `tests/features/`; the steps live in `conftest.py`. This
file exists only to bind them, which is why it holds no assertions.
"""

from pytest_bdd import scenarios

scenarios("evaluating_a_calculation.feature")
scenarios("rejecting_a_request.feature")
