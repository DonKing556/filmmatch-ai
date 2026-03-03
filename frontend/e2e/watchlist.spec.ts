import { test, expect } from "@playwright/test";

test.describe("Watchlist Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/watchlist");
  });

  test("renders page with heading", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: /my watchlist/i }),
    ).toBeVisible();
  });

  test("shows empty state when no items", async ({ page }) => {
    // The page should show the empty state since there's no auth/data
    await expect(page.getByText(/no movies yet/i)).toBeVisible();
    await expect(
      page.getByText(/movies you save will appear here/i),
    ).toBeVisible();
  });

  test("has navigation elements", async ({ page }) => {
    const nav = page.getByRole("navigation");
    await expect(nav.first()).toBeVisible();
  });
});
