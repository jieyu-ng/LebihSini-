import { expect, test } from "@playwright/test";

const bahasaRequest =
  "Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.";
const urgentDeadline = "2026-06-21T09:30:00+08:00";

test("completes the core GreenProof browser journey with the real local backend", async ({
  page,
}) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: "LebihSini GreenProof" }),
  ).toBeVisible();

  await page.getByRole("textbox").fill(bahasaRequest);
  await page.getByRole("button", { name: "Submit Request" }).click();

  await expect(
    page.getByRole("heading", { name: "Confirm Requirement" }),
  ).toBeVisible();
  await expect(page.getByText("Demo fixture: Bahasa request")).toBeVisible();
  await expect(page.getByText(/high|medium|low/i).first()).toBeVisible();

  await page.getByRole("button", { name: "Confirm & Continue" }).click();

  await expect(
    page.getByRole("heading", { name: "Resource Discovery" }),
  ).toBeVisible();
  await expect(page.getByText("Site A")).toBeVisible();
  await expect(page.getByText("300 units selected")).toBeVisible();
  await expect(page.getByText("Site B")).toBeVisible();
  await expect(page.getByText("130 units selected")).toBeVisible();
  await expect(page.getByText("Supplier F")).toBeVisible();
  await expect(page.getByText("70 units")).toBeVisible();
  await expect(page.getByText("Site D")).toBeVisible();
  await expect(page.getByText(/Equipment: tile_cutter/i)).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Excluded from automatic recommendation" }),
  ).toBeVisible();
  await expect(page.getByText("Site E")).toBeVisible();
  await expect(
    page.getByText(/product label was unreadable/i),
  ).toBeVisible();

  await page.getByRole("button", { name: "Review Verdict" }).click();

  await expect(
    page.getByRole("heading", { name: "GreenProof Verdict" }),
  ).toBeVisible();
  await expect(page.getByText(/Selected materials:/)).toContainText(/Site A .*: 300/);
  await expect(page.getByText(/Selected materials:/)).toContainText(/Site B .*: 130/);
  await expect(page.getByText(/Supplier F shortfall:/)).toContainText("70");
  await expect(page.getByText(/Equipment:/)).toContainText(/Site D/);

  const recalcRequestPromise = page.waitForRequest((request) => {
    return request.method() === "POST" &&
      /\/api\/recommendations\/[^/]+\/recalculate$/.test(request.url());
  });

  await page
    .getByRole("button", { name: "Switch to three-hour urgency" })
    .click();

  const recalcRequest = await recalcRequestPromise;
  expect(recalcRequest.postDataJSON()).toEqual({
    revised_deadline_at: urgentDeadline,
  });

  await expect(page.getByText(/Selected materials:/)).toContainText(/Site A .*: 300/);
  await expect(page.getByText(/Selected materials:/)).not.toContainText(/Site B .*: 130/);
  await expect(page.getByText(/Supplier F shortfall:/)).toContainText("200");
  await expect(page.getByText("Site B")).toBeVisible();
  await expect(
    page.getByText(/cannot finish before the selected deadline/i),
  ).toBeVisible();

  const decisionRequestPromise = page.waitForRequest((request) => {
    return request.method() === "POST" &&
      /\/api\/recommendations\/[^/]+\/decision$/.test(request.url());
  });

  await page.getByRole("button", { name: "Approve Plan" }).click();

  const decisionRequest = await decisionRequestPromise;
  expect(decisionRequest.postDataJSON()).toMatchObject({
    decision_type: "approve",
  });

  await expect(
    page.getByRole("heading", { name: "GreenProof Evidence Record" }),
  ).toBeVisible();
  await expect(page.getByText(/Decision:\s*approve/i)).toBeVisible();
  await expect(page.getByText(/Site A .* - 300 units/i)).toBeVisible();
  await expect(page.getByText(/Site D .* - tile_cutter/i)).toBeVisible();
  await expect(page.getByText(/Safety Certificate/i)).toHaveCount(0);
  await expect(page.getByText(/Sustainability Certificate/i)).toHaveCount(0);
  await expect(page.getByText(/Official ESG Certificate/i)).toHaveCount(0);
});
