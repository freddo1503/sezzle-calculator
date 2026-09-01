/**
 * The keypad's input state machine.
 *
 * It tracks what has been typed, which operator is waiting, and whether the
 * display currently holds an answer. It performs no arithmetic and decides no
 * arithmetic semantics: when a calculation is due it *asks* for one, and the
 * caller sends that request to the API.
 *
 * Two consequences of that rule, both deliberate:
 *
 * - Pressing equals twice does not repeat the last operation. Repetition is a
 *   rule about what an operation means when reapplied, which belongs in the
 *   backend, and the backend holds no session state to reapply it from.
 * - Chaining carries the exact value the API returned, never the rounded string
 *   on screen. Rounding is presentation and must not re-enter a calculation.
 *
 * See `.claude/rules/principles.md` and ADR-0004.
 */

/** The operations the contract names, keyed by what the keypad shows. */
export const OPERATIONS = {
  "+": "add",
  "-": "subtract",
  "*": "multiply",
  "/": "divide",
  "^": "power",
  "%": "percent",
} as const;

export type OperatorKey = keyof typeof OPERATIONS;

export type CalculationRequest = {
  operation: string;
  operands: string[];
};

export type KeypadState = {
  /** What the user is typing now, or null when the display holds an answer. */
  entry: string | null;
  /** The exact left operand, as the API returned it. */
  accumulator: string | null;
  /** The operator waiting for its right operand. */
  pending: OperatorKey | null;
  /** What the display shows, before formatting. */
  display: string;
  /** The reason the last calculation failed, if it did. */
  error?: string;
};

export type Press = { key: string; value?: string };

export type Transition = { state: KeypadState; request?: CalculationRequest };

export const initial: KeypadState = {
  entry: null,
  accumulator: null,
  pending: null,
  display: "0",
};

const isDigit = (key: string) => key.length === 1 && key >= "0" && key <= "9";

function withEntry(state: KeypadState, entry: string): KeypadState {
  return { ...state, entry, display: entry, error: undefined };
}

export function press(state: KeypadState, { key, value }: Press): Transition {
  if (key === "resolved" && value !== undefined) {
    return {
      state: {
        ...state,
        accumulator: value,
        entry: null,
        pending: null,
        display: value,
      },
    };
  }

  if (key === "failed") {
    return { state: { ...state, entry: null, pending: null, error: value } };
  }

  if (key === "C") {
    return { state: initial };
  }

  if (isDigit(key)) {
    const current = state.entry;
    if (current === null || current === "0") {
      return {
        state: withEntry(
          { ...state, accumulator: state.pending ? state.accumulator : null },
          key,
        ),
      };
    }
    return { state: withEntry(state, current + key) };
  }

  if (key === ".") {
    const current = state.entry ?? "0";
    if (current.includes(".")) {
      return { state: { ...state, error: undefined } };
    }
    return { state: withEntry(state, `${current}.`) };
  }

  if (key === "sqrt") {
    const operand = state.entry ?? state.accumulator;
    if (operand === null) {
      return { state };
    }
    return {
      state: { ...state, error: undefined },
      request: { operation: "sqrt", operands: [operand] },
    };
  }

  if (key in OPERATIONS) {
    const operator = key as OperatorKey;

    // Two operators in a row: the second replaces the first, nothing is due.
    if (state.entry === null && state.pending !== null) {
      return { state: { ...state, pending: operator, error: undefined } };
    }

    // An operand is waiting on a pending operator, so that calculation is due
    // before this operator can take its place.
    if (
      state.entry !== null &&
      state.pending !== null &&
      state.accumulator !== null
    ) {
      return {
        state: { ...state, pending: operator, entry: null, error: undefined },
        request: {
          operation: OPERATIONS[state.pending],
          operands: [state.accumulator, state.entry],
        },
      };
    }

    return {
      state: {
        ...state,
        accumulator: state.entry ?? state.accumulator,
        entry: null,
        pending: operator,
        error: undefined,
      },
    };
  }

  if (key === "=") {
    if (
      state.pending === null ||
      state.entry === null ||
      state.accumulator === null
    ) {
      return { state: { ...state, error: undefined } };
    }
    return {
      state: { ...state, error: undefined },
      request: {
        operation: OPERATIONS[state.pending],
        operands: [state.accumulator, state.entry],
      },
    };
  }

  return { state };
}
