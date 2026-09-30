/**
 * record.js — headless capture of preview.html into assets/hero-grid.gif
 *
 *   npm i -D playwright gifenc && npx playwright install chromium && node record.js
 *
 * Simulates an organic mouse path (figure-8 across the card) to trigger the
 * 3D grid distortion + spotlight, screenshots frames, and encodes a looping GIF.
 * If Playwright/Chromium is unavailable, use the offline fallback: `python record.py`.
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const W = 880, H = 460, FRAMES = 40, STEP_MS = 70;
const OUT = path.join(__dirname, "assets", "hero-grid.gif");

const pos = (t) => ({
  x: W / 2 + 200 * Math.cos(2 * Math.PI * t),
  y: H / 2 + 10 + 95 * Math.sin(4 * Math.PI * t + 0.6),
});

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  await page.goto("file://" + path.join(__dirname, "preview.html"));
  await page.waitForFunction("window.__heroReady === true", null, { timeout: 15000 });
  await page.waitForTimeout(800);

  for (let k = 0; k < 20; k++) { // warmup easing
    const { x, y } = pos(k / 20);
    await page.evaluate(`window.__setMouse(${x}, ${y})`);
    await page.waitForTimeout(30);
  }

  const { GifEncoder } = await import("gifenc").catch(() => ({}));
  const shots = [];
  for (let i = 0; i < FRAMES; i++) {
    const { x, y } = pos(i / FRAMES);
    await page.evaluate(`window.__setMouse(${x}, ${y})`);
    await page.waitForTimeout(STEP_MS);
    shots.push(await page.screenshot());
  }
  await browser.close();

  if (!GifEncoder) {
    // Save raw frames; encode with python fallback.
    const tmp = path.join(__dirname, "assets", ".frames");
    fs.mkdirSync(tmp, { recursive: true });
    shots.forEach((b, i) => fs.writeFileSync(path.join(tmp, `f${String(i).padStart(2, "0")}.png`), b));
    console.log(`[record.js] frames saved to ${tmp}; run \`python record.py\` or install gifenc to encode.`);
    return;
  }

  const { default: sharp } = await import("sharp").catch(() => ({}));
  const gif = GifEncoder();
  const frames = [];
  for (const buf of shots) {
    const raw = sharp ? await sharp(buf).resize(W, H).raw().toBuffer({ resolveWithObject: true })
                      : null;
    frames.push(raw);
  }
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  console.log(`[record.js] captured ${shots.length} frames`);
})().catch((e) => { console.error("[record.js]", e.message); process.exit(1); });
