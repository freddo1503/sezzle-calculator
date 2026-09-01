"""The arithmetic engine, tested as pure functions.

No HTTP here, by design: the engine has no request object, no status code and no
framework import, which is what lets these cases be exhaustive and fast. See
.claude/rules/principles.md, "Separation of concerns".
"""

from decimal import Decimal

import pytest

from app.engine import CalculationError, evaluate

D = Decimal


def calc(operation: str, *operands: str) -> Decimal:
    return evaluate(operation, [D(o) for o in operands])


def failure(operation: str, *operands: str) -> str:
    with pytest.raises(CalculationError) as caught:
        calc(operation, *operands)
    return caught.value.code


class TestExactness:
    """The claim the whole submission rests on."""

    def test_one_tenth_plus_two_tenths_is_exactly_three_tenths(self):
        assert calc("add", "0.1", "0.2") == D("0.3")

    def test_the_float_answer_is_not_produced(self):
        # What binary floating point would give, and what we must not give.
        assert 0.1 + 0.2 == 0.30000000000000004
        assert str(calc("add", "0.1", "0.2")) == "0.3"

    def test_a_tenth_of_a_cent_survives_a_large_total(self):
        assert calc("add", "999999999999.99", "0.01") == D("1000000000000.00")

    def test_repeated_addition_does_not_drift(self):
        total = D("0")
        for _ in range(10):
            total = evaluate("add", [total, D("0.1")])
        assert total == D("1.0")


class TestOperations:
    @pytest.mark.parametrize(
        ("operation", "a", "b", "expected"),
        [
            ("add", "2", "3", "5"),
            ("add", "-2", "3", "1"),
            ("subtract", "5", "3", "2"),
            ("subtract", "3", "5", "-2"),
            ("multiply", "4", "2.5", "10.0"),
            ("multiply", "-4", "2", "-8"),
            ("divide", "10", "4", "2.5"),
            ("divide", "-9", "3", "-3"),
            ("power", "2", "10", "1024"),
            ("power", "9", "0.5", "3"),
            ("power", "2", "-2", "0.25"),
            ("percent", "20", "50", "10"),
            ("percent", "50", "20", "10"),
            ("percent", "0", "99", "0"),
        ],
    )
    def test_binary_operations(self, operation: str, a: str, b: str, expected: str):
        assert calc(operation, a, b) == D(expected)

    @pytest.mark.parametrize(
        ("operand", "expected"),
        [("4", "2"), ("0", "0"), ("2.25", "1.5"), ("0.25", "0.5")],
    )
    def test_square_root(self, operand: str, expected: str):
        assert calc("sqrt", operand) == D(expected)

    def test_square_root_of_two_is_irrational_and_therefore_truncated(self):
        # Honest about the boundary: 28 significant digits, not the real number.
        root = calc("sqrt", "2")
        assert str(root).startswith("1.41421356237309504880168872")
        assert len(str(root).replace(".", "").lstrip("0")) == 28


class TestDomainErrors:
    def test_division_by_zero(self):
        assert failure("divide", "1", "0") == "DIVISION_BY_ZERO"

    def test_zero_divided_by_zero_is_still_division_by_zero(self):
        assert failure("divide", "0", "0") == "DIVISION_BY_ZERO"

    def test_square_root_of_a_negative_number(self):
        assert failure("sqrt", "-1") == "NEGATIVE_SQRT"

    def test_negative_base_with_a_fractional_exponent_has_no_real_result(self):
        assert failure("power", "-8", "0.5") == "UNDEFINED_RESULT"

    def test_zero_to_a_negative_power_is_undefined(self):
        assert failure("power", "0", "-1") == "UNDEFINED_RESULT"

    def test_a_result_too_large_for_the_decimal_context(self):
        huge = "9" * 25
        assert failure("power", huge, huge) == "RESULT_OVERFLOW"

    def test_an_unknown_operation_is_rejected(self):
        assert failure("tetrate", "2", "3") == "UNKNOWN_OPERATION"

    @pytest.mark.parametrize(
        ("operation", "operands"),
        [("add", ["1"]), ("add", ["1", "2", "3"]), ("sqrt", ["1", "2"]), ("sqrt", [])],
    )
    def test_the_wrong_number_of_operands_is_rejected(self, operation, operands):
        with pytest.raises(CalculationError) as caught:
            evaluate(operation, [D(o) for o in operands])
        assert caught.value.code == "WRONG_OPERAND_COUNT"


class TestChaining:
    """Quality scenario Q6, at the level where the guarantee is created.

    Chaining on the exact value keeps a third of a third of a whole readable as
    one. Chaining on a rounded display value would not, and this is the only
    place that difference can be established.
    """

    def test_a_third_times_three_stays_within_a_rounding_of_one(self):
        third = calc("divide", "1", "3")
        assert evaluate("multiply", [third, D("3")]) > D("0.99999999999999999999999")

    def test_chaining_on_a_rounded_value_would_lose_it(self):
        # The mistake this design avoids: two decimal places carried forward.
        rounded_third = D("0.33")
        assert evaluate("multiply", [rounded_third, D("3")]) == D("0.99")


class TestErrorsCarryContext:
    def test_a_failure_names_its_operation_and_operand(self):
        with pytest.raises(CalculationError) as caught:
            calc("divide", "1", "0")
        assert caught.value.details == {"operation": "divide", "operand_index": 1}

    def test_a_failure_carries_a_human_readable_message(self):
        with pytest.raises(CalculationError) as caught:
            calc("sqrt", "-1")
        assert "negative" in caught.value.message.lower()
