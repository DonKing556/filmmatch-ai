import { test, expect } from "@playwright/test";

test.describe("Group Recommendation Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/group");
  });

  test("shows setup step with member inputs", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: /group watch/i }),
    ).toBeVisible();
    // Should have 2 member inputs by default
    const inputs = page.getByPlaceholder(/person.*name/i);
    const count = await inputs.count();
    expect(count).toBe(2);
  });

  test("can add a third member", async ({ page }) => {
    await page.getByText("+ Add another person").click();
    const inputs = page.getByPlaceholder(/person.*name/i);
    expect(await inputs.count()).toBe(3);
  });

  test("can remove a member when more than two exist", async ({ page }) => {
    // Add third member first
    await page.getByText("+ Add another person").click();
    expect(await page.getByPlaceholder(/person.*name/i).count()).toBe(3);

    // Remove buttons should be visible (X icons)
    const removeButtons = page.locator(
      "button:has(svg path[d='M6 18L18 6M6 6l12 12'])",
    );
    await removeButtons.last().click();
    expect(await page.getByPlaceholder(/person.*name/i).count()).toBe(2);
  });

  test("continue button is disabled until names are filled", async ({
    page,
  }) => {
    const continueBtn = page.getByRole("button", { name: /continue/i });
    await expect(continueBtn).toBeDisabled();

    // Fill both names
    const inputs = page.getByPlaceholder(/person.*name/i);
    await inputs.nth(0).fill("Alice");
    await inputs.nth(1).fill("Bob");

    await expect(continueBtn).toBeEnabled();
  });

  test("advancing to share step shows invite code", async ({ page }) => {
    const inputs = page.getByPlaceholder(/person.*name/i);
    await inputs.nth(0).fill("Alice");
    await inputs.nth(1).fill("Bob");

    await page.getByRole("button", { name: /continue/i }).click();

    await expect(
      page.getByRole("heading", { name: /invite your crew/i }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /set preferences/i }),
    ).toBeVisible();
  });

  test("set preferences shows member preference form", async ({ page }) => {
    // Setup -> Share -> Members
    const inputs = page.getByPlaceholder(/person.*name/i);
    await inputs.nth(0).fill("Alice");
    await inputs.nth(1).fill("Bob");
    await page.getByRole("button", { name: /continue/i }).click();
    await page.getByRole("button", { name: /set preferences/i }).click();

    // Should show Alice's preferences
    await expect(page.getByText(/Alice.*Preferences/i)).toBeVisible();
    await expect(page.getByText("Genres")).toBeVisible();
    await expect(page.getByText("Mood")).toBeVisible();
  });
});
