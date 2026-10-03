import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const outDir = path.join(__dirname, '..', 'screenshots');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

async function capture() {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: true,
    defaultViewport: { width: 1440, height: 900 }
  });

  const page = await browser.newPage();

  // 1. Public Landing Page
  console.log('Capturing Public Landing Page...');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: path.join(outDir, 'landing_page.png') });

  // 2. Login to get token
  console.log('Logging in...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
  await page.type('input[type="email"]', 'analyst@odisha.gov.in');
  await page.type('input[type="password"]', 'Analyst@123');
  await page.click('button[type="submit"]');
  await new Promise(r => setTimeout(r, 1500));

  // 3. Dashboard
  console.log('Capturing Dashboard...');
  await page.goto('http://localhost:5173/app/dashboard', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: path.join(outDir, 'dashboard.png') });

  // 4. Skill Gaps Matrix
  console.log('Capturing Skill Gaps Matrix...');
  await page.goto('http://localhost:5173/app/skill-gaps', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: path.join(outDir, 'skill_gaps.png') });

  // 5. Forecasting Engine
  console.log('Capturing Forecasting Engine...');
  await page.goto('http://localhost:5173/app/forecast', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: path.join(outDir, 'forecast.png') });

  // 6. What-If Simulator
  console.log('Capturing What-If Simulator...');
  await page.goto('http://localhost:5173/app/simulator', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: path.join(outDir, 'simulator.png') });

  // 7. Early Warning System
  console.log('Capturing Early Warning System...');
  await page.goto('http://localhost:5173/app/early-warning', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: path.join(outDir, 'early_warning.png') });

  // 8. Model Evaluation
  console.log('Capturing Model Evaluation...');
  await page.goto('http://localhost:5173/app/model-evaluation', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: path.join(outDir, 'model_evaluation.png') });

  await browser.close();
  console.log('All screenshots saved in:', outDir);
}

capture().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
