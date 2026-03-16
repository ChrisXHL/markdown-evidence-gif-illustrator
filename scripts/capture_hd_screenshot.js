#!/usr/bin/env node
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

function arg(name, fallback = undefined) {
  const idx = process.argv.indexOf(name);
  if (idx === -1 || idx + 1 >= process.argv.length) return fallback;
  return process.argv[idx + 1];
}

(async () => {
  const url = arg('--url');
  const output = arg('--output');
  const waitMs = parseInt(arg('--wait-ms', '2500'), 10);
  const fullPage = process.argv.includes('--full-page');
  const viewportWidth = parseInt(arg('--width', '2200'), 10);
  const viewportHeight = parseInt(arg('--height', '1600'), 10);
  const deviceScaleFactor = parseFloat(arg('--scale', '2'));
  const selector = arg('--selector');
  const text = arg('--text');
  const clipX = arg('--clip-x');
  const clipY = arg('--clip-y');
  const clipW = arg('--clip-w');
  const clipH = arg('--clip-h');

  if (!url || !output) {
    console.error('Usage: capture_hd_screenshot.js --url <url> --output <path> [--wait-ms 2500] [--width 2200] [--height 1600] [--scale 2] [--selector <css>] [--text <text>] [--full-page]');
    process.exit(1);
  }

  fs.mkdirSync(path.dirname(output), { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: viewportWidth, height: viewportHeight },
    deviceScaleFactor,
  });

  await page.goto(url, { waitUntil: 'networkidle', timeout: 120000 });
  await page.waitForTimeout(waitMs);

  if (text) {
    const locator = page.getByText(text, { exact: false }).first();
    if (await locator.count()) {
      await locator.scrollIntoViewIfNeeded();
      await page.waitForTimeout(800);
    }
  }

  if (selector) {
    const locator = page.locator(selector).first();
    if (await locator.count()) {
      await locator.scrollIntoViewIfNeeded();
      await page.waitForTimeout(800);
      await locator.screenshot({ path: output });
      await browser.close();
      return;
    }
  }

  if (clipX && clipY && clipW && clipH) {
    await page.screenshot({
      path: output,
      clip: {
        x: parseInt(clipX, 10),
        y: parseInt(clipY, 10),
        width: parseInt(clipW, 10),
        height: parseInt(clipH, 10),
      },
    });
    await browser.close();
    return;
  }

  await page.screenshot({ path: output, fullPage });
  await browser.close();
})();
