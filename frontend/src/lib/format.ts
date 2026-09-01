/**
 * Formatting a value for the display.
 *
 * Presentation only. The rounded string is never fed back into a calculation:
 * the keypad chains on the exact value the API returned. A business rule changes
 * what the answer is; a formatting choice changes only how it is shown.
 *
 * The rounding is done on the string rather than through `Number`, which would
 * be the obvious shortcut and the wrong one: parsing a 28-digit decimal into an
 * IEEE-754 double reintroduces exactly the error the whole design exists to
 * avoid, and `(1e24).toFixed(2)` does not even produce a plain number.
 */

const SCALE = 2;

/** Round a plain decimal string to `SCALE` places, half away from zero. */
function roundPlain(value: string): string {
  const negative = value.startsWith("-");
  const [whole, fraction = ""] = value.replace("-", "").split(".");

  if (fraction.length <= SCALE) {
    return `${negative ? "-" : ""}${whole}.${fraction.padEnd(SCALE, "0")}`;
  }

  const kept = fraction.slice(0, SCALE);
  const roundUp = Number(fraction[SCALE]) >= 5;

  // Carry through the kept digits and into the integer part, as string
  // arithmetic, so a 28-digit value never becomes a float.
  let digits = `${whole}${kept}`;
  if (roundUp) {
    digits = (BigInt(digits) + 1n).toString().padStart(digits.length, "0");
  }

  const cut = digits.length - SCALE;
  const integer = digits.slice(0, cut) || "0";
  return `${negative ? "-" : ""}${integer}.${digits.slice(cut)}`;
}

/**
 * The display form of an exact value.
 *
 * A value carrying an exponent is shown as it arrived: it is too large or too
 * small to write plainly, and two decimal places would say nothing about it.
 */
export function forDisplay(value: string): string {
  if (value.includes("e") || value.includes("E")) {
    return value;
  }
  return roundPlain(value);
}

/** What the display shows while a number is being typed, shown verbatim. */
export function asTyped(value: string): string {
  return value;
}
