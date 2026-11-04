const { test, expect } = require("@playwright/test");

// Keep checks independent of external banner servers and live Last.fm availability.
test.beforeEach(async ({ page, baseURL }) => {
  await page.route("**/*", (route) => {
    const url = route.request().url();
    if (url.startsWith(baseURL) && !url.includes("/_vercel/")) return route.continue();
    return route.fulfill({ status: 204, body: "" });
  });
});

async function mockTrack(page, track) {
  await page.route("https://ws.audioscrobbler.com/**", (route) =>
    route.fulfill({ json: { recenttracks: { track } } }),
  );
}

for (const width of [390, 700, 1050, 1440]) {
  test(`home fits ${width}px and switches between hosts`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await mockTrack(page, [
      { name: "A song", artist: { "#text": "An artist" }, "@attr": { nowplaying: "true" } },
    ]);
    await page.goto("/");
    await expect(page.locator("#local-clock")).toHaveText(/\d{2}:\d{2}:\d{2}/);
    await expect(page.locator(".listening-status")).toHaveText("Listening now");
    await expect(page.locator("#fetch-specs dd")).toHaveCount(9);
    await page.getByRole("button", { name: "HOMELAB", exact: true }).click();
    await expect(page.locator("#fetch-user")).toHaveText("root@pve");
    await expect(page.locator("#fetch-specs dd").first()).toContainText("Proxmox");
    await expect(page.locator("#fetch-logo")).not.toHaveAttribute("aria-pressed");
    await page.getByRole("button", { name: "PC", exact: true }).click();
    await expect(page.locator("#fetch-specs dd").first()).toContainText("Debian");
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true,
    );
  });
}

test("Last.fm handles a past track and an empty history", async ({ page }) => {
  await mockTrack(page, [
    {
      name: "A song",
      artist: { "#text": "An artist" },
      date: { uts: String(Math.floor(Date.now() / 1000) - 600) },
    },
  ]);
  await page.goto("/");
  await expect(page.locator(".listening-status")).toHaveText(/Last listened · 10 min ago/);
  await page.unroute("https://ws.audioscrobbler.com/**");
  await mockTrack(page, []);
  await page.reload();
  await expect(page.locator(".listening-status")).toHaveText("Nothing played yet");
});

test("album opens the original and supports keyboard navigation", async ({ page }) => {
  await page.goto("/albums/teriberka.html");
  const photoCount = await page.locator(".album figure").count();
  await page.locator(".album figure a").first().click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog.locator(".viewer-image")).toHaveAttribute("src", "../assets/teriberka.png");
  await expect(dialog.locator(".viewer-count")).toHaveText(`1 / ${photoCount}`);
  await page.keyboard.press("ArrowRight");
  await expect(dialog.locator(".viewer-count")).toHaveText(`2 / ${photoCount}`);
  await page.keyboard.press("ArrowLeft");
  await expect(dialog.locator(".viewer-count")).toHaveText(`1 / ${photoCount}`);
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe("");
});

test("banner HTML can be copied", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.goto("/banner.html");
  await page.getByRole("button", { name: "Copy HTML" }).click();
  await expect(page.getByRole("status")).toHaveText("Copied.");
  expect(await page.evaluate(() => navigator.clipboard.readText())).toContain(
    "https://laptos.fun/assets/laptos-88x31.svg",
  );
});
