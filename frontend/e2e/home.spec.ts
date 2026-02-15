import { test, expect } from "@playwright/test";

test.describe("Home Page", () => {
  test("renders hero section with CTA buttons", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(page.getByText("AI-Powered")).toBeVisible();

    const soloButton = page.getByRole("button", { name: /find my movie/i });
    const groupButton = page.getByRole("button", { name: /group watch/i });
    await expect(soloButton).toBeVisible();
    await expect(groupButton).toBeVisible();
  });

  test("solo CTA navigates to /solo", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /find my movie/i }).click();
    await expect(page).toHaveURL(/\/solo/);
  });

  test("group CTA navigates to /group", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /group watch/i }).click();
    await expect(page).toHaveURL(/\/group/);
  });

  test("skip-to-content link exists", async ({ page }) => {
    await page.goto("/");
    const skipLink = page.getByRole("link", { name: /skip to content/i });
    await expect(skipLink).toBeAttached();
  });

  test("page has no accessibility violations for heading hierarchy", async ({
    page,
  }) => {
    await page.goto("/");
    const headings = page.locator("h1, h2, h3");
    const count = await headings.count();
    expect(count).toBeGreaterThan(0);

    // First heading should be h1
    const firstTag = await headings.first().evaluate((el) => el.tagName);
    expect(firstTag).toBe("H1");
  });
});
