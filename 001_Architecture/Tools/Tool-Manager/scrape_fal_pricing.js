/**
 * scrape_fal_pricing.js
 * Scrapes pricing for fal.ai models using the local Chrome profile (cookies/session).
 * Outputs JSON to stdout: { "model_id": { price, unit }, ... }
 *
 * Usage:
 *   node scrape_fal_pricing.js
 *   node scrape_fal_pricing.js --headful   (show browser window)
 */

const { chromium } = require('playwright');
const path = require('path');

const CHROME_PROFILE = path.join(
  process.env.HOME, 'Library/Application Support/Google/Chrome'
);

const MODELS = [
  { id: 'mirelo-ai/sfx-v1.5/video-to-audio',  url: 'https://fal.ai/models/mirelo-ai/sfx-v1.5' },
  { id: 'kling-video/video-to-audio',          url: 'https://fal.ai/models/kling-video/video-to-audio' },
  { id: 'sonilo/v1.1/video-to-music',          url: 'https://fal.ai/models/sonilo/v1.1/video-to-music' },
  { id: 'sam-audio/visual-separate',           url: 'https://fal.ai/models/sam-audio/visual-separate' },
];

// Patterns to find pricing text on fal.ai model pages
const PRICE_PATTERNS = [
  /\$([0-9]+\.?[0-9]*)\s*\/\s*(second|sec|minute|min|video|image|request|generation|clip|output)/i,
  /([0-9]+\.?[0-9]*)\s*cents?\s*\/\s*(second|sec|minute|min|video|image|request)/i,
  /price[:\s]+\$([0-9]+\.?[0-9]*)/i,
  /billing[:\s]+\$([0-9]+\.?[0-9]*)/i,
  /\$([0-9]+\.?[0-9]*)\s+per\s+(second|minute|video|image|request|generation)/i,
];

async function scrapePricing() {
  const headful = process.argv.includes('--headful');
  const results = {};

  // Try with Chrome profile first (has session cookies)
  let browser;
  try {
    browser = await chromium.launchPersistentContext(CHROME_PROFILE, {
      headless: !headful,
      channel: 'chrome',
      args: ['--no-first-run', '--no-default-browser-check'],
    });
  } catch (e) {
    // Chrome profile may be locked (Chrome is open) — fall back to fresh Chromium
    process.stderr.write(`Chrome profile locked, using fresh Chromium: ${e.message}\n`);
    const b = await chromium.launch({ headless: !headful });
    browser = await b.newContext();
  }

  const page = 'newPage' in browser ? await browser.newPage() : await browser.newPage();

  for (const model of MODELS) {
    process.stderr.write(`\nScraping: ${model.url}\n`);
    try {
      await page.goto(model.url, { waitUntil: 'domcontentloaded', timeout: 20000 });

      // Wait a moment for JS to render pricing
      await page.waitForTimeout(3000);

      // Grab all visible text
      const bodyText = await page.evaluate(() => document.body.innerText);

      // Try to find pricing
      let price = null;
      let unit = null;

      for (const pattern of PRICE_PATTERNS) {
        const match = bodyText.match(pattern);
        if (match) {
          price = parseFloat(match[1]);
          unit = match[2] ? `per ${match[2].toLowerCase()}` : 'per request';
          break;
        }
      }

      // Also look for a dedicated pricing/billing section
      if (!price) {
        // Look for structured pricing table text
        const pricingSection = bodyText
          .split('\n')
          .filter(l => /\$|price|billing|cost|credit/i.test(l))
          .slice(0, 10)
          .join(' | ');
        if (pricingSection) {
          process.stderr.write(`  Pricing section text: ${pricingSection}\n`);
        }
      }

      results[model.id] = { price, unit, url: model.url };
      process.stderr.write(`  → price=${price} unit=${unit}\n`);

    } catch (err) {
      process.stderr.write(`  ERROR: ${err.message}\n`);
      results[model.id] = { price: null, unit: null, url: model.url, error: err.message };
    }
  }

  await browser.close();
  process.stdout.write(JSON.stringify(results, null, 2) + '\n');
}

scrapePricing().catch(err => {
  process.stderr.write(`Fatal: ${err.message}\n`);
  process.exit(1);
});
