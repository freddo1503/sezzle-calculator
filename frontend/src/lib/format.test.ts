import { describe, expect, it } from "vitest";
import { forDisplay } from "./format";

describe("formatting a value for the display", () => {
  it.each([
    ["0.3", "0.30"],
    ["3", "3.00"],
    ["0", "0.00"],
    ["-2", "-2.00"],
    ["2.5", "2.50"],
    ["10", "10.00"],
  ])("pads %s to two places as %s", (value, expected) => {
    expect(forDisplay(value)).toBe(expected);
  });

  it.each([
    ["0.3333333333333333333333333333", "0.33"],
    ["0.999", "1.00"],
    ["1.005", "1.01"],
    ["-0.999", "-1.00"],
    ["9.996", "10.00"],
  ])("rounds %s to %s", (value, expected) => {
    expect(forDisplay(value)).toBe(expected);
  });

  it("does not lose an integer too large for a double", () => {
    // Number("1000000000000000000000001") is 1e24 and the last digit is gone.
    expect(forDisplay("1000000000000000000000001")).toBe(
      "1000000000000000000000001.00",
    );
  });

  it("shows an exponent as it arrived, since two places would say nothing", () => {
    expect(forDisplay("9.999999999999999999999997E+74")).toBe(
      "9.999999999999999999999997E+74",
    );
  });

  it("keeps every digit of an exact third, once rounded for display only", () => {
    const exact = "0.3333333333333333333333333333";
    expect(forDisplay(exact)).toBe("0.33");
    expect(exact).toHaveLength(30);
  });
});
