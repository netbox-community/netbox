const esbuild = require('esbuild');
const { sassPlugin } = require('esbuild-sass-plugin');

// Bundler options common to all bundle jobs.
const options = {
  outdir: './dist',
  bundle: true,
  minify: true,
  sourcemap: true,
  logLevel: 'error',
  publicPath: '/static',
};

// Get CLI arguments for optional overrides.
const ARGS = process.argv.slice(2);

/**
 * Run script bundle jobs.
 */
async function bundleScripts() {
  const entryPoints = {
    netbox: 'src/index.ts',
    jobs: 'src/jobs.ts',
    lldp: 'src/device/lldp.ts',
    config: 'src/device/config.ts',
    status: 'src/device/status.ts',
  };
  try {
    let result = await esbuild.build({
      ...options,
      entryPoints,
      target: 'es2016',
    });
    if (result.errors.length === 0) {
      for (const [targetName, sourceName] of Object.entries(entryPoints)) {
        const source = sourceName.split('/')[1];
        console.log(`✅ Bundled source file '${source}' to '${targetName}.js'`);
      }
    }
  } catch (err) {
    console.error(err);
  }
}

/**
 * Run style bundle jobs.
 */
async function bundleStyles() {
  try {
    const entryPoints = {
      'netbox-external': 'styles/_external.scss',
      'netbox-light': 'styles/_light.scss',
      'netbox-dark': 'styles/_dark.scss',
      rack_elevations: 'styles/_rack_elevations.scss',
      cable_trace: 'styles/_cable_trace.scss',
    };
    const pluginOptions = { outputStyle: 'compressed' };
    // Allow cache disabling.
    if (ARGS.includes('--no-cache')) {
      pluginOptions.cache = false;
    }
    let result = await esbuild.build({
      ...options,
      entryPoints,
      plugins: [sassPlugin(pluginOptions)],
      loader: {
        '.eot': 'file',
        '.woff': 'file',
        '.woff2': 'file',
        '.svg': 'file',
        '.ttf': 'file',
      },
    });
    if (result.errors.length === 0) {
      for (const [targetName, sourceName] of Object.entries(entryPoints)) {
        const source = sourceName.split('/')[1];
        console.log(`✅ Bundled source file '${source}' to '${targetName}.css'`);
      }
    }
  } catch (err) {
    console.error(err);
  }
}

/**
 * Run all bundle jobs.
 */
async function bundleAll() {
  if (ARGS.includes('--styles')) {
    // Only run style jobs.
    return await bundleStyles();
  } else if (ARGS.includes('--scripts')) {
    // Only run script jobs.
    return await bundleScripts();
  }
  await bundleStyles();
  await bundleScripts();
}

bundleAll();
