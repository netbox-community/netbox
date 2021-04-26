const Bundler = require('parcel-bundler');

const options = {
  watch: false,
  minify: true,
  outDir: './dist',
  publicUrl: '/static',
  logLevel: 2,
  cache: true,
};

const args = process.argv.slice(2);

if (args.includes('--no-cache')) {
  options.cache = false;
}

const styles = [
  ['main.scss', 'netbox.css'],
  ['rack_elevation.scss', 'rack_elevation.css'],
];

const scripts = [
  ['src/index.ts', 'netbox.js'],
  ['src/jobs.ts', 'jobs.js'],
  ['src/device/lldp.ts', 'lldp.js'],
  ['src/device/config.ts', 'config.js'],
  ['src/device/status.ts', 'status.js'],
];

async function bundleStyles() {
  for (const [input, outFile] of styles) {
    const instance = new Bundler(input, { outFile, ...options });
    await instance.bundle();
  }
}

async function bundleScripts() {
  for (const [input, outFile] of scripts) {
    const instance = new Bundler(input, { outFile, ...options });
    await instance.bundle();
  }
}

async function bundleAll() {
  if (args.includes('--styles')) {
    return await bundleStyles();
  } else if (args.includes('--scripts')) {
    return await bundleScripts();
  }
  await bundleStyles();
  await bundleScripts();
}

bundleAll();
