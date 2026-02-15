import { test, expect } from "@playwright/test";

test.describe("Solo Recommendation Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/solo");
  });

  test("shows genre selection step", async ({ page }) => {
    await expect(page.getByText(/genres/i)).toBeVisible();
    // Genre chips should be visible
    await expect(page.getByText("Action")).toBeVisible();
    await expect(page.getByText("Drama")).toBeVisible();
    await expect(page.getByText("Comedy")).toBeVisible();
  });

  test("can select genres and advance to mood step", async ({ page }) => {
    // Select a genre
    await page.getByText("Drama").click();
    await page.getByText("Thriller").click();

    // Advance to next step
    const nextButton = page.getByRole("button", { name: /next|continue/i });
    await expect(nextButton).toBeVisible();
    await nextButton.click();

    // Should now be on mood step
    await expect(page.getByText(/mood/i)).toBeVisible();
  });

  test("can select mood and advance to details step", async ({ page }) => {
    // Step 1: genres
    await page.getByText("Drama").click();
    await page.getByRole("button", { name: /next|continue/i }).click();

    // Step 2: mood
    await expect(page.getByText(/mood/i)).toBeVisible();
    await page.getByText("Intense").click();
    await page.getByRole("button", { name: /next|continue/i }).click();

    // Step 3: details
    await expect(
      page.getByText(/details|anything else|dealbreaker/i)
    ).toBeVisible();
  });

  test("step indicator shows progress", async ({ page }) => {
    // Step indicator should show first step active
    const steps = page.locator("[data-step-indicator] span, [class*='step']");
    const stepIndicator = page.getByText(/genres/i);
    await expect(stepIndicator).toBeVisible();
  });

  test("bottom navigation is visible on mobile", async ({ page, isMobile }) => {
    test.skip(!isMobile, "Only for mobile viewports");
    const nav = page.getByRole("navigation", { name: /main/i });
    await expect(nav).toBeVisible();
  });
});
