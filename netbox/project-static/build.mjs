// Compile NetBox's TypeScript and SCSS sources into dist/. Exits non-zero on any failure.
import { copyFile, mkdir, rm } from 'node:fs/promises';
import * as esbuild from 'esbuild';
import { sassPlugin } from 'esbuild-sass-plugin';

const args = process.argv.slice(2);
const common = { outdir: 'dist', bundle: true, minify: true, logLevel: 'warning' };

async function buildScripts() {
  await esbuild.build({
    ...common,
    entryPoints: { netbox: 'src/index.ts' },
    sourcemap: 'linked',
    target: 'es2016',
  });
  // GraphiQL ships prebuilt UMD bundles; copy them as-is.
  const graphiql = {
    'react/umd/react.production.min.js': 'react.production.min.js',
    'react-dom/umd/react-dom.production.min.js': 'react-dom.production.min.js',
    'js-cookie/dist/js.cookie.min.js': 'js.cookie.min.js',
    'graphiql/graphiql.min.js': 'graphiql.min.js',
    'graphiql/graphiql.min.css': 'graphiql.min.css',
    '@graphiql/plugin-explorer/dist/index.umd.js': 'index.umd.js',
    '@graphiql/plugin-explorer/dist/style.css': 'plugin-explorer-style.css',
  };
  await mkdir('dist/graphiql', { recursive: true });
  await Promise.all(
    Object.entries(graphiql).map(([src, dest]) =>
      copyFile(`node_modules/${src}`, `dist/graphiql/${dest}`),
    ),
  );
}

async function buildStyles() {
  await esbuild.build({
    ...common,
    entryPoints: {
      'netbox-external': 'styles/external.scss',
      netbox: 'styles/netbox.scss',
      rack_elevation: 'styles/svg/rack_elevation.scss',
      cable_trace: 'styles/svg/cable_trace.scss',
    },
    // Sourcemaps are disabled for CSS (see #7068)
    sourcemap: false,
    plugins: [
      sassPlugin({
        // Tabler 1.4 and Bootstrap 5 require @import-era Sass; silence those known deprecations only
        quietDeps: true,
        silenceDeprecations: ['import', 'global-builtin', 'color-functions', 'if-function'],
      }),
    ],
    loader: { '.eot': 'file', '.woff': 'file', '.woff2': 'file', '.svg': 'file', '.ttf': 'file' },
  });
}

try {
  // A full build starts clean so that stale hashed assets show up as deletions
  if (!args.length) await rm('dist', { recursive: true, force: true });
  if (!args.includes('--scripts')) await buildStyles();
  if (!args.includes('--styles')) await buildScripts();
} catch {
  // esbuild has already printed the error details
  process.exit(1);
}
