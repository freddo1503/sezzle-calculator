import { describe, expect, it } from "vitest";
import { initial, type KeypadState, press } from "./keypad";

/** Press a sequence of keys, ignoring any calculation the machine asks for. */
function type(...keys: string[]): KeypadState {
  return keys.reduce((state, key) => press(state, { key }).state, initial);
}

/** Press keys and return the calculation the last press asked for, if any. */
function requestAfter(...keys: string[]) {
  let state = initial;
  let request: ReturnType<typeof press>["request"];
  for (const key of keys) {
    ({ state, request } = press(state, { key }));
  }
  return request;
}

describe("entering a number", () => {
  it("shows digits as they are typed", () => {
    expect(type("1", "2", "3").display).toBe("123");
  });

  it("starts from zero", () => {
    expect(initial.display).toBe("0");
  });

  it("replaces the leading zero rather than appending to it", () => {
    expect(type("0", "7").display).toBe("7");
  });

  it("accepts one decimal point and refuses a second", () => {
    expect(type("1", ".", "5", ".", "2").display).toBe("1.52");
  });

  it("puts a zero before a leading decimal point", () => {
    expect(type(".", "5").display).toBe("0.5");
  });

  it("clears back to the start", () => {
    expect(type("1", "2", "C").display).toBe("0");
  });
});

describe("asking for a calculation", () => {
  it("asks for nothing until an operator and a second operand are given", () => {
    expect(requestAfter("1", "2")).toBeUndefined();
    expect(requestAfter("1", "2", "+")).toBeUndefined();
    expect(requestAfter("1", "2", "+", "3")).toBeUndefined();
  });

  it("asks for the calculation when equals is pressed", () => {
    expect(requestAfter("1", "2", "+", "3", "=")).toEqual({
      operation: "add",
      operands: ["12", "3"],
    });
  });

  it("asks for the pending calculation when a second operator is pressed", () => {
    expect(requestAfter("1", "+", "2", "*")).toEqual({
      operation: "add",
      operands: ["1", "2"],
    });
  });

  it("asks immediately for a unary operation, needing no second operand", () => {
    expect(requestAfter("9", "sqrt")).toEqual({
      operation: "sqrt",
      operands: ["9"],
    });
  });

  it("does not repeat the last operation when equals is pressed twice", () => {
    // Repeating is a rule about what an operation means, which belongs in the
    // backend, and the backend holds no session. So the key does nothing.
    let state = initial;
    for (const key of ["1", "+", "2", "="]) ({ state } = press(state, { key }));
    ({ state } = press(state, { key: "resolved", value: "3" }));
    expect(press(state, { key: "=" }).request).toBeUndefined();
  });

  it("changes the operator when two are pressed in a row", () => {
    expect(requestAfter("1", "+", "-", "2", "=")).toEqual({
      operation: "subtract",
      operands: ["1", "2"],
    });
  });
});

describe("receiving an answer", () => {
  it("shows the answer", () => {
    let state = initial;
    for (const key of ["1", "+", "2", "="]) ({ state } = press(state, { key }));
    expect(press(state, { key: "resolved", value: "3" }).state.display).toBe(
      "3",
    );
  });

  it("chains on the exact answer, not on what the display shows", () => {
    // The guarantee: a third carried forward at full precision, not at two
    // decimal places, so a third times three reads as one.
    let state = initial;
    for (const key of ["1", "/", "3", "="]) ({ state } = press(state, { key }));
    ({ state } = press(state, {
      key: "resolved",
      value: "0.3333333333333333333333333333",
    }));
    const { request } = ["*", "3", "="].reduce(
      (carried, key) => press(carried.state, { key }),
      { state, request: undefined } as ReturnType<typeof press>,
    );
    expect(request?.operands[0]).toBe("0.3333333333333333333333333333");
  });

  it("starts a new number when a digit follows an answer", () => {
    let state = initial;
    for (const key of ["1", "+", "2", "="]) ({ state } = press(state, { key }));
    ({ state } = press(state, { key: "resolved", value: "3" }));
    expect(press(state, { key: "7" }).state.display).toBe("7");
  });

  it("shows the reason a calculation failed", () => {
    let state = initial;
    for (const key of ["1", "/", "0", "="]) ({ state } = press(state, { key }));
    const failed = press(state, {
      key: "failed",
      value: "Division by zero is undefined.",
    });
    expect(failed.state.error).toBe("Division by zero is undefined.");
  });

  it("clears the error on the next key", () => {
    let state = initial;
    for (const key of ["1", "/", "0", "="]) ({ state } = press(state, { key }));
    ({ state } = press(state, {
      key: "failed",
      value: "Division by zero is undefined.",
    }));
    expect(press(state, { key: "5" }).state.error).toBeUndefined();
  });
});
