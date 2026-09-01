import { expect, test } from "@playwright/test";

test.describe("the assembled stack", () => {
  test("a tenth plus two tenths reads as three tenths, not as a float", async ({
    page,
  }) => {
    await page.goto("/");

    for (const key of [
      "Zero",
      "Decimal point",
      "One",
      "Add",
      "Zero",
      "Decimal point",
      "Two",
    ]) {
      await page.getByRole("button", { name: key, exact: true }).click();
    }
    await page.getByRole("button", { name: "Equals", exact: true }).click();

    // 0.30, not 0.30000000000000004. Every hop had to hold for this to read
    // correctly: exact decimal arithmetic, strings on the wire, and display
    // rounding that never re-enters a calculation.
    await expect(page.getByTestId("display")).toHaveText("0.30");
  });

  test("a third times three reads as one, because chaining uses the exact value", async ({
    page,
  }) => {
    await page.goto("/");

    for (const key of ["One", "Divide", "Three", "Equals"]) {
      await page.getByRole("button", { name: key, exact: true }).click();
    }
    await expect(page.getByTestId("display")).toHaveText("0.33");

    for (const key of ["Multiply", "Three", "Equals"]) {
      await page.getByRole("button", { name: key, exact: true }).click();
    }
    // 1.00 and not 0.99: what was carried forward was the full precision value,
    // not the two decimal places on screen.
    await expect(page.getByTestId("display")).toHaveText("1.00");
  });

  test("dividing by zero shows the reason the server gave", async ({
    page,
  }) => {
    await page.goto("/");

    for (const key of ["One", "Divide", "Zero", "Equals"]) {
      await page.getByRole("button", { name: key, exact: true }).click();
    }
    await expect(page.getByTestId("error")).toHaveText(/division by zero/i);
  });
});
