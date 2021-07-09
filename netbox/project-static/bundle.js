/**
 * ParcelJS Bundle Configuration.
 *
 * @see https://parceljs.org/api.html
 */

const Bundler = require('parcel-bundler');

// Bundler options common to all bundle jobs.
const options = {
  logLevel: 2,
  cache: true,
  watch: false,
  minify: true,
  outDir: './dist',
  publicUrl: '/static',
};

// Get CLI arguments for optional overrides.
const args = process.argv.slice(2);

// Allow cache disabling.
if (args.includes('--no-cache')) {
  options.cache = false;
}

// Style (SCSS) bundle jobs. Generally, everything should be bundled into netbox.css from main.scss
// unless there is a specific reason to do otherwise.
const styles = [
  ['_external.scss', 'netbox-external.css'],
  ['_light.scss', 'netbox-light.css'],
  ['_dark.scss', 'netbox-dark.css'],
  ['_elevations.scss', 'rack_elevation.css'],
];

// Script (JavaScript) bundle jobs. Generally, everything should be bundled into netbox.js from
// index.ts unless there is a specific reason to do otherwise.
const scripts = [
  ['src/index.ts', 'netbox.js'],
  ['src/jobs.ts', 'jobs.js'],
  ['src/device/lldp.ts', 'lldp.js'],
  ['src/device/config.ts', 'config.js'],
  ['src/device/status.ts', 'status.js'],
];

/**
 * Run style bundle jobs.
 */
async function bundleStyles() {
  for (const [input, outFile] of styles) {
    const instance = new Bundler(input, { outFile, ...options });
    await instance.bundle();
  }
}

/**
 * Run script bundle jobs.
 */
async function bundleScripts() {
  for (const [input, outFile] of scripts) {
    const instance = new Bundler(input, { outFile, ...options });
    await instance.bundle();
  }
}

/**
 * Run all bundle jobs.
 */
async function bundleAll() {
  if (args.includes('--styles')) {
    // Only run style jobs.
    return await bundleStyles();
  } else if (args.includes('--scripts')) {
    // Only run script jobs.
    return await bundleScripts();
  }
  await bundleStyles();
  await bundleScripts();
}

bundleAll();
