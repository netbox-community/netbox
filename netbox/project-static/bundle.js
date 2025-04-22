const esbuild = require('esbuild');
const { sassPlugin } = require('esbuild-sass-plugin');
const util = require('util');
const fs = require('fs');
const copyFilePromise = util.promisify(fs.copyFile);

// Bundler options common to all bundle jobs.
const options = {
  outdir: './dist',
  bundle: true,
  minify: true,
  sourcemap: 'linked',
  logLevel: 'error',
};

// Get CLI arguments for optional overrides.
const ARGS = process.argv.slice(2);

function copyFiles(files) {
    return Promise.all(files.map(f => {
       return copyFilePromise(f.source, f.dest);
    }));
}

async function bundleGraphIQL() {
  let fileMap = [
    {
      source: './node_modules/react/umd/react.production.min.js',
      dest: './dist/graphiql/react.production.min.js'
    },
    {
      source: './node_modules/react-dom/umd/react-dom.production.min.js',
      dest: './dist/graphiql/react-dom.production.min.js'
    },
    {
      source: './node_modules/js-cookie/dist/js.cookie.min.js',
      dest: './dist/graphiql/js.cookie.min.js'
    },
    {
      source: './node_modules/graphiql/graphiql.min.js',
      dest: './dist/graphiql/graphiql.min.js'
    },
    {
      source: './node_modules/@graphiql/plugin-explorer/dist/index.umd.js',
      dest: './dist/graphiql/index.umd.js'
    },
    {
      source: './node_modules/graphiql/graphiql.min.css',
      dest: './dist/graphiql/graphiql.min.css'
    },
    {
      source: './node_modules/@graphiql/plugin-explorer/dist/style.css',
      dest: './dist/graphiql/plugin-explorer-style.css'
    }
  ];

  try {
    if (!fs.existsSync('./dist/graphiql/')) {
      fs.mkdirSync('./dist/graphiql/');
    }
  } catch (err) {
    console.error(err);
  }

  copyFiles(fileMap).then(() => {
     console.log('✅ Copied graphiql files');
  }).catch(err => {
     console.error(err);
  });
}

/**
 * Bundle Core NetBox JavaScript.
 */
async function bundleNetBox() {
  const entryPoints = {
    netbox: 'src/index.ts',
  };
  try {
    const result = await esbuild.build({
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
 * Run script bundle jobs.
 */
async function bundleScripts() {
  for (const bundle of [bundleNetBox, bundleGraphIQL]) {
    await bundle();
  }
}

/**
 * Run style bundle jobs.
 */
async function bundleStyles() {
  try {
    const entryPoints = {
      'netbox-external': 'styles/external.scss',
      'netbox': 'styles/netbox.scss',
      rack_elevation: 'styles/svg/rack_elevation.scss',
      cable_trace: 'styles/svg/cable_trace.scss',
    };
    const pluginOptions = { outputStyle: 'compressed' };
    // Allow cache disabling.
    if (ARGS.includes('--no-cache')) {
      pluginOptions.cache = false;
    }
    let result = await esbuild.build({
      ...options,
      // Disable sourcemaps for CSS/SCSS files, see #7068
      sourcemap: false,
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
        console.log(`✅ Bundled source file '${sourceName}' to '${targetName}.css'`);
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
