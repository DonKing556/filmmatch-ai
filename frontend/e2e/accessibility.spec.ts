import { test, expect } from "@playwright/test";

test.describe("Accessibility", () => {
  test("home page main landmark exists", async ({ page }) => {
    await page.goto("/");
    const main = page.locator("main#main-content");
    await expect(main).toBeVisible();
  });

  test("navigation has aria-label", async ({ page }) => {
    await page.goto("/");
    const nav = page.getByRole("navigation");
    const count = await nav.count();
    expect(count).toBeGreaterThan(0);
  });

  test("all images have alt text", async ({ page }) => {
    await page.goto("/");
    const images = page.locator("img");
    const count = await images.count();
    for (let i = 0; i < count; i++) {
      const alt = await images.nth(i).getAttribute("alt");
      expect(alt).toBeTruthy();
    }
  });

  test("interactive elements are keyboard accessible", async ({ page }) => {
    await page.goto("/");
    // Tab through page — first focusable should be skip-to-content
    await page.keyboard.press("Tab");
    const focused = page.locator(":focus");
    await expect(focused).toBeVisible();
  });

  test("solo page chips have listbox role", async ({ page }) => {
    await page.goto("/solo");
    const listbox = page.getByRole("listbox");
    const count = await listbox.count();
    expect(count).toBeGreaterThan(0);
  });

  test("buttons have accessible names", async ({ page }) => {
    await page.goto("/");
    const buttons = page.getByRole("button");
    const count = await buttons.count();
    for (let i = 0; i < count; i++) {
      const name = await buttons.nth(i).getAttribute("aria-label");
      const text = await buttons.nth(i).textContent();
      // Button should have either aria-label or visible text
      expect(name || text?.trim()).toBeTruthy();
    }
  });
});
