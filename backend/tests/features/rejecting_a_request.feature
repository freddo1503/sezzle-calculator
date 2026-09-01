Feature: Rejecting a request that has no answer
  Every failure leaves in one shape, a JSON:API errors array, whatever went
  wrong. Three kinds of failure keep three different statuses, because
  collapsing them would tell a client less than it needs.

  Scenario Outline: A request that is not JSON:API is refused before it is read
    A wrong media type is wrong whatever the body holds, so it is answered
    before the body is parsed. The specification requires 415, media type
    parameters included.

    Given the request declares the media type "<media type>"
    When a valid calculation is submitted with that media type
    Then the response status is 415
    And the error code is "UNSUPPORTED_MEDIA_TYPE"
    And the response uses the JSON:API media type

    Examples:
      | media type                          |
      | application/json                    |
      | text/plain                          |
      | application/vnd.api+json; charset=utf-8 |

  Scenario: A body that is not JSON at all is malformed
    Given a request body that is not valid JSON
    When the request is submitted
    Then the response status is 400
    And the error code is "MALFORMED_REQUEST"

  Scenario: A body that parses but breaks the contract is invalid
    FastAPI has an error shape of its own. If it were allowed through, the
    service would answer schema failures in one format and everything else in
    another, and the single-error-shape promise would be false immediately.

    Given a request body that parses but does not match the contract
    When the request is submitted
    Then the response status is 422
    And the error code is "VALIDATION_ERROR"
    And the response holds no data alongside its errors

  Scenario Outline: The contract rejects the wrong number of operands
    Operand arity is stated in the contract, so it is refused before any
    arithmetic is attempted.

    Given a calculation applying "<operation>" to the operands <operands>
    When the calculation is submitted
    Then the response status is 422

    Examples:
      | operation | operands        |
      | add       | "1"             |
      | add       | "1", "2", "3"   |
      | sqrt      | "1", "2"        |

  Scenario Outline: The contract rejects an operand it does not accept
    Given a calculation applying "add" to "<a>" and "1"
    When the calculation is submitted
    Then the response status is 422

    Examples:
      | a                          | why                     |
      | abc                        | not a number            |
      | 1..2                       | two decimal points      |
      | 99999999999999999999999999 | beyond the stated bound |

  Scenario: An unknown operation is refused by the contract
    Given a calculation applying "tetrate" to "2" and "3"
    When the calculation is submitted
    Then the response status is 422

  Scenario: Dividing by zero points at the divisor
    The pointer is an RFC 6901 JSON Pointer into the request document, so the
    client learns which operand was at fault without knowing our conventions.

    Given a calculation applying "divide" to "1" and "0"
    When the calculation is submitted
    Then the response status is 422
    And the error code is "DIVISION_BY_ZERO"
    And the error points at "/data/attributes/operands/1"

  Scenario: A negative square root points at its only operand
    Given a calculation applying "sqrt" to "-1"
    When the calculation is submitted
    Then the error code is "NEGATIVE_SQRT"
    And the error points at "/data/attributes/operands/0"

  Scenario Outline: A calculation with no answer names its reason
    Given a calculation applying "<operation>" to "<a>" and "<b>"
    When the calculation is submitted
    Then the response status is 422
    And the error code is "<code>"

    Examples:
      | operation | a                         | b                         | code             |
      | power     | -8                        | 0.5                       | UNDEFINED_RESULT |
      | power     | 0                         | -1                        | UNDEFINED_RESULT |
      | power     | 9999999999999999999999999 | 9999999999999999999999999 | RESULT_OVERFLOW  |

  Scenario: An error carries a summary and a detail, and they are not the same
    JSON:API's title is the same for every occurrence of a code; the detail
    describes this occurrence.

    Given a calculation applying "divide" to "1" and "0"
    When the calculation is submitted
    Then the error carries a title and a detail that differ
