import { test, expect } from "@playwright/test";

test.describe("Onboarding Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/onboarding");
  });

  test("shows vibe selection as first step", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: /what vibes are you into/i }),
    ).toBeVisible();
    await expect(page.getByText("Thrilling")).toBeVisible();
    await expect(page.getByText("Cozy")).toBeVisible();
    await expect(page.getByText("Mind-Bending")).toBeVisible();
  });

  test("step indicator shows all 4 steps", async ({ page }) => {
    await expect(page.getByText("Vibes")).toBeVisible();
    await expect(page.getByText("Genres")).toBeVisible();
    await expect(page.getByText("Preferences")).toBeVisible();
    await expect(page.getByText("Services")).toBeVisible();
  });

  test("next button is disabled until a vibe is selected", async ({
    page,
  }) => {
    const nextBtn = page.getByRole("button", { name: /next/i });
    await expect(nextBtn).toBeDisabled();

    // Select a vibe
    await page.getByText("Thrilling").click();
    await expect(nextBtn).toBeEnabled();
  });

  test("can advance to genre step after selecting a vibe", async ({
    page,
  }) => {
    await page.getByText("Cozy").click();
    await page.getByRole("button", { name: /next/i }).click();

    await expect(
      page.getByRole("heading", { name: /pick your favorite genres/i }),
    ).toBeVisible();
    await expect(page.getByText("Action")).toBeVisible();
    await expect(page.getByText("Drama")).toBeVisible();
  });

  test("skip button navigates to home", async ({ page }) => {
    await page.getByRole("button", { name: /skip/i }).click();
    await expect(page).toHaveURL("/");
  });

  test("genre step requires at least 3 selections", async ({ page }) => {
    // Step 1: select a vibe
    await page.getByText("Cozy").click();
    await page.getByRole("button", { name: /next/i }).click();

    // Step 2: genres
    const nextBtn = page.getByRole("button", { name: /next/i });
    await expect(nextBtn).toBeDisabled();

    await page.getByText("Drama").click();
    await page.getByText("Comedy").click();
    await expect(nextBtn).toBeDisabled();

    await page.getByText("Romance").click();
    await expect(nextBtn).toBeEnabled();
  });
});
