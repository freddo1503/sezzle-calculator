/**
 * The keypad.
 *
 * It holds no business rules. Validation arrives as Zod schemas generated from
 * the contract, arithmetic semantics stay in the backend, and error wording
 * comes back in the response rather than from a table here. Its own job is to
 * collect input, ask for a calculation, and show what came back.
 */

import { useCallback, useEffect, useState } from "react";
import { createCalculation } from "@/api/calculator";
import {
  CreateCalculationBody,
  CreateCalculationResponse,
} from "@/api/schemas.zod";
import { Button } from "@/components/ui/button";
import { forDisplay } from "@/lib/format";
import {
  type CalculationRequest,
  initial,
  type KeypadState,
  press,
} from "@/lib/keypad";
import { cn } from "@/lib/utils";

type Key = {
  label: string;
  press: string;
  name: string;
  variant?: "default" | "secondary" | "outline";
  wide?: boolean;
};

const KEYS: Key[] = [
  { label: "C", press: "C", name: "Clear", variant: "outline" },
  { label: "√", press: "sqrt", name: "Square root", variant: "outline" },
  { label: "xʸ", press: "^", name: "Power", variant: "outline" },
  { label: "÷", press: "/", name: "Divide", variant: "secondary" },
  { label: "7", press: "7", name: "Seven" },
  { label: "8", press: "8", name: "Eight" },
  { label: "9", press: "9", name: "Nine" },
  { label: "×", press: "*", name: "Multiply", variant: "secondary" },
  { label: "4", press: "4", name: "Four" },
  { label: "5", press: "5", name: "Five" },
  { label: "6", press: "6", name: "Six" },
  { label: "−", press: "-", name: "Subtract", variant: "secondary" },
  { label: "1", press: "1", name: "One" },
  { label: "2", press: "2", name: "Two" },
  { label: "3", press: "3", name: "Three" },
  { label: "+", press: "+", name: "Add", variant: "secondary" },
  { label: "0", press: "0", name: "Zero", wide: true },
  { label: ".", press: ".", name: "Decimal point" },
  { label: "%", press: "%", name: "Percent", variant: "outline" },
  { label: "=", press: "=", name: "Equals", variant: "secondary" },
];

/** Keyboard keys that mean the same thing as a keypad key. */
const FROM_KEYBOARD: Record<string, string> = {
  Enter: "=",
  Escape: "C",
  Backspace: "C",
  x: "*",
  ",": ".",
};

async function evaluate(
  request: CalculationRequest,
): Promise<{ ok: true; value: string } | { ok: false; reason: string }> {
  // Validated against the contract before it leaves, so a request the contract
  // forbids never reaches the network.
  const body = CreateCalculationBody.safeParse({
    data: { type: "calculations", attributes: request },
  });
  if (!body.success) {
    return {
      ok: false,
      reason: "That is not a calculation this service accepts.",
    };
  }

  const response = await createCalculation(body.data as never);

  if (response.status === 200) {
    // Generated types are erased at build time and check nothing at runtime, so
    // the response is validated against the contract here, at the boundary,
    // where a violation fails loudly instead of surfacing far from its cause.
    const parsed = CreateCalculationResponse.safeParse(response.data);
    if (!parsed.success) {
      return {
        ok: false,
        reason: "The service returned something unexpected.",
      };
    }
    return { ok: true, value: parsed.data.data.attributes.result };
  }

  const errors = (
    response.data as { errors?: { detail?: string; title?: string }[] }
  ).errors;
  const first = errors?.[0];
  return {
    ok: false,
    reason: first?.detail ?? first?.title ?? "The calculation failed.",
  };
}

export function Calculator() {
  const [state, setState] = useState<KeypadState>(initial);
  const [busy, setBusy] = useState(false);

  const handle = useCallback((key: string) => {
    setState((current) => {
      const { state: next, request } = press(current, { key });
      if (request) {
        setBusy(true);
        evaluate(request)
          .then((outcome) =>
            setState((now) =>
              outcome.ok
                ? press(now, { key: "resolved", value: outcome.value }).state
                : press(now, { key: "failed", value: outcome.reason }).state,
            ),
          )
          .finally(() => setBusy(false));
      }
      return next;
    });
  }, []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const key = FROM_KEYBOARD[event.key] ?? event.key;
      if (KEYS.some((candidate) => candidate.press === key)) {
        event.preventDefault();
        handle(key);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [handle]);

  const shown = state.entry !== null ? state.entry : forDisplay(state.display);

  return (
    <main className="mx-auto flex min-h-dvh max-w-sm flex-col justify-center gap-4 p-4">
      <h1 className="sr-only">Calculator</h1>

      <output
        aria-live="polite"
        data-testid="display"
        className={cn(
          "rounded-xl border bg-muted px-4 py-6 text-right font-mono text-4xl tabular-nums break-all",
          busy && "opacity-60",
        )}
      >
        {shown}
      </output>

      <p
        role="status"
        data-testid="error"
        className="min-h-5 text-sm text-destructive"
      >
        {state.error ?? ""}
      </p>

      <div className="grid grid-cols-4 gap-2">
        {KEYS.map((key) => (
          <Button
            key={key.press}
            type="button"
            aria-label={key.name}
            variant={key.variant ?? "default"}
            disabled={busy}
            onClick={() => handle(key.press)}
            className={cn("h-14 text-lg", key.wide && "col-span-2")}
          >
            {key.label}
          </Button>
        ))}
      </div>
    </main>
  );
}
