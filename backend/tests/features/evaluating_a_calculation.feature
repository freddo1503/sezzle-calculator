Feature: Evaluating a calculation
  A client posts one arithmetic operation and gets back an exact decimal answer.
  Every expectation here comes from openapi.yaml, never from the implementation.

  Scenario: A tenth plus two tenths is exactly three tenths
    This is the claim the whole submission rests on. Binary floating point
    answers 0.30000000000000004 and that answer is wrong.

    Given a calculation applying "add" to "0.1" and "0.2"
    When the calculation is submitted
    Then the response status is 200
    And the result is exactly "0.3"

  Scenario Outline: The four required operations
    Given a calculation applying "<operation>" to "<a>" and "<b>"
    When the calculation is submitted
    Then the result is exactly "<result>"

    Examples:
      | operation | a  | b   | result |
      | add       | 2  | 3   | 5      |
      | add       | -2 | 3   | 1      |
      | subtract  | 5  | 3   | 2      |
      | subtract  | 3  | 5   | -2     |
      | multiply  | 4  | 2.5 | 10     |
      | divide    | 10 | 4   | 2.5    |
      | divide    | -9 | 3   | -3     |

  Scenario Outline: The three optional operations
    Percentage is "a percent of b", so 20 percent of 50 is 10. The postfix
    percent of physical calculators is deliberately not implemented.

    Given a calculation applying "<operation>" to "<a>" and "<b>"
    When the calculation is submitted
    Then the result is exactly "<result>"

    Examples:
      | operation | a  | b   | result |
      | power     | 2  | 10  | 1024   |
      | power     | 9  | 0.5 | 3      |
      | power     | 2  | -2  | 0.25   |
      | percent   | 20 | 50  | 10     |
      | percent   | 50 | 20  | 10     |

  Scenario Outline: Square root takes a single operand
    Given a calculation applying "sqrt" to "<a>"
    When the calculation is submitted
    Then the result is exactly "<result>"

    Examples:
      | a    | result |
      | 9    | 3      |
      | 0    | 0      |
      | 2.25 | 1.5    |

  Scenario: The full precision crosses the wire, not a rounded value
    Rounding for display belongs to the client and must never re-enter a
    calculation, so the service returns every digit it computed.

    Given a calculation applying "divide" to "1" and "3"
    When the calculation is submitted
    Then the result begins with "0.3333333333333333333333333333"

  Scenario Outline: Trailing zeros left by the arithmetic are not shown
    Twenty percent of fifty computes as 10.0 and four times 2.5 as 10.0, both
    exact and both wrong to show. Stripping them does not change the value, so
    a client chaining on the answer gets the same result either way.

    Given a calculation applying "<operation>" to "<a>" and "<b>"
    When the calculation is submitted
    Then the result is exactly "<result>"

    Examples:
      | operation | a             | b    | result        |
      | percent   | 20            | 50   | 10            |
      | multiply  | 4             | 2.5  | 10            |
      | add       | 1000000000000 | 0.00 | 1000000000000 |
      | subtract  | 5             | 5    | 0             |

  Scenario: A result too large to write plainly keeps its exponent
    Seventy-five digits is already unreadable and the largest allowed operands
    reach a quarter of a million, so an exponent is the honest answer rather
    than a wall of zeros.

    Given a calculation applying "power" to "9999999999999999999999999" and "3"
    When the calculation is submitted
    Then the result is exactly "9.999999999999999999999997E+74"

  Scenario Outline: A result can be fed straight back in as an operand
    A calculator chains, so operands and results share one grammar. An operand
    type narrower than the result type would be a service that cannot accept its
    own output: a third has 28 significant digits and its square would be
    refused.

    Given a calculation applying "multiply" to "<a>" and "<b>"
    When the calculation is submitted
    Then the response status is 200

    Examples:
      | a                             | b | why                          |
      | 0.3333333333333333333333333333 | 3 | 28 digits, as division returns |
      | 9.999E+74                      | 1 | an exponent, as power returns  |

  Scenario: The answer comes back as a JSON:API resource
    Given a calculation applying "multiply" to "6" and "7"
    When the calculation is submitted
    Then the response uses the JSON:API media type
    And the resource type is "calculations"
    And the resource carries an identifier

  Scenario: The request is echoed back, because nothing is stored
    No calculation is persisted, so a client cannot fetch it again to see what
    was asked. The response therefore carries the question with the answer.

    Given a calculation applying "subtract" to "10" and "3"
    When the calculation is submitted
    Then the echoed operation is "subtract"
    And the echoed operands are "10" and "3"

  Scenario: Two identical calculations are two distinct evaluations
    Given a calculation applying "add" to "1" and "1"
    When the calculation is submitted twice
    Then the two identifiers differ
