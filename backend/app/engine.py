"""Exact decimal arithmetic.

This module knows nothing about HTTP. It takes decimals, returns a decimal, and
raises `CalculationError` when an operation has no answer. That ignorance is what
lets every operation and every edge case be tested as a pure function, with no
server running and no request object in sight.

Precision is Python's default of 28 significant digits with banker's rounding,
reached for rather than configured because `decimal` ships with the standard
library and its defaults need no defence. See ADR-0004 and
.claude/rules/principles.md.
"""

from __future__ import annotations

import decimal
from collections.abc import Callable, Sequence
from decimal import Decimal, localcontext
from typing import Final

__all__ = ["ARITY", "CalculationError", "evaluate"]

# 28 significant digits, ROUND_HALF_EVEN. Every trap that matters is raised
# rather than silently producing a special value, so a failure surfaces as an
# error code instead of an Infinity or a NaN reaching the client.
PRECISION: Final = 28
ROUNDING: Final = decimal.ROUND_HALF_EVEN


class CalculationError(Exception):
    """An operation that cannot be evaluated.

    `code` is the stable, machine-readable reason from the contract's enumeration.
    `message` is for a human and its wording belongs to the server.
    """

    def __init__(self, code: str, message: str, **details: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def _context() -> decimal.Context:
    return decimal.Context(
        prec=PRECISION,
        rounding=ROUNDING,
        traps=[decimal.Overflow, decimal.InvalidOperation, decimal.DivisionByZero],
    )


def add(a: Decimal, b: Decimal) -> Decimal:
    return a + b


def subtract(a: Decimal, b: Decimal) -> Decimal:
    return a - b


def multiply(a: Decimal, b: Decimal) -> Decimal:
    return a * b


def divide(a: Decimal, b: Decimal) -> Decimal:
    if b.is_zero():
        raise CalculationError(
            "DIVISION_BY_ZERO",
            "Division by zero is undefined.",
            operation="divide",
            operand_index=1,
        )
    return a / b


def power(base: Decimal, exponent: Decimal) -> Decimal:
    if base.is_zero() and exponent < 0:
        raise CalculationError(
            "UNDEFINED_RESULT",
            "Zero raised to a negative power is undefined.",
            operation="power",
            operand_index=1,
        )
    if base < 0 and exponent != exponent.to_integral_value():
        raise CalculationError(
            "UNDEFINED_RESULT",
            "A negative base with a fractional exponent has no real-valued result.",
            operation="power",
            operand_index=1,
        )
    return base**exponent


def percent(a: Decimal, b: Decimal) -> Decimal:
    """`a` percent of `b`. See the contract's BinaryOperation description."""
    return a / Decimal(100) * b


def square_root(a: Decimal) -> Decimal:
    if a < 0:
        raise CalculationError(
            "NEGATIVE_SQRT",
            "The square root of a negative number is not a real number.",
            operation="sqrt",
            operand_index=0,
        )
    return a.sqrt()


_UNARY: Final[dict[str, Callable[[Decimal], Decimal]]] = {"sqrt": square_root}

_BINARY: Final[dict[str, Callable[[Decimal, Decimal], Decimal]]] = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "power": power,
    "percent": percent,
}

#: How many operands each operation takes. The contract states this too, which is
#: not duplication: the contract binds the wire, this binds the engine, and the
#: engine must stand alone for anything that calls it without going through HTTP.
ARITY: Final[dict[str, int]] = {name: 1 for name in _UNARY} | {name: 2 for name in _BINARY}


def evaluate(operation: str, operands: Sequence[Decimal]) -> Decimal:
    """Evaluate one operation, or raise `CalculationError` explaining why not."""
    expected = ARITY.get(operation)
    if expected is None:
        raise CalculationError(
            "UNKNOWN_OPERATION",
            f"Unknown operation: {operation!r}.",
            operation=operation,
        )
    if len(operands) != expected:
        raise CalculationError(
            "WRONG_OPERAND_COUNT",
            f"Operation {operation!r} takes {expected} operand(s), got {len(operands)}.",
            operation=operation,
            expected=expected,
            received=len(operands),
        )

    with localcontext(_context()):
        try:
            if expected == 1:
                return _UNARY[operation](operands[0])
            return _BINARY[operation](*operands)
        except decimal.Overflow as exc:
            raise CalculationError(
                "RESULT_OVERFLOW",
                "The result is too large for the decimal context.",
                operation=operation,
            ) from exc
        except decimal.DivisionByZero as exc:
            raise CalculationError(
                "DIVISION_BY_ZERO",
                "Division by zero is undefined.",
                operation=operation,
                operand_index=1,
            ) from exc
        except decimal.InvalidOperation as exc:
            raise CalculationError(
                "UNDEFINED_RESULT",
                "The result is mathematically undefined.",
                operation=operation,
            ) from exc
