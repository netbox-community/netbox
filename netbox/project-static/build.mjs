// Compile NetBox's TypeScript and SCSS sources into dist/. Exits non-zero on any failure.
import { rename, rm } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as esbuild from 'esbuild';
import { sassPlugin } from 'esbuild-sass-plugin';

// Resolve all paths relative to this directory, regardless of where the script is invoked from.
// Both are needed: chdir() covers the file operations below, but esbuild resolves entry points
// against `absWorkingDir`, which does not follow process.chdir().
const ROOT = dirname(fileURLToPath(import.meta.url));
process.chdir(ROOT);

const USAGE = 'Usage: node build.mjs [--styles | --scripts]';
const args = process.argv.slice(2);
if (args.length > 1 || args.some(arg => arg !== '--styles' && arg !== '--scripts')) {
  console.error(USAGE);
  process.exit(2);
}

// A full build is written to a staging directory, which replaces dist/ only once the build has
// succeeded. This removes any stale hashed assets without leaving dist/ empty after a failure.
const fullBuild = args.length === 0;
const STAGING_DIR = '.dist-build';
const BACKUP_DIR = '.dist-backup';
const outdir = fullBuild ? STAGING_DIR : 'dist';
const common = { absWorkingDir: ROOT, outdir, bundle: true, minify: true, logLevel: 'warning' };

// GraphiQL's editor (Monaco) runs its language services in web workers, which src/graphiql.ts
// loads from beside its own bundle. Resolve them through @graphiql/react, so that they always match
// the version of Monaco it pins.
const requireFrom = (require, name) => createRequire(require.resolve(`${name}/package.json`));
const graphiqlReact = requireFrom(
  requireFrom(createRequire(import.meta.url), 'graphiql'),
  '@graphiql/react',
);
const monacoWorkers = {
  'editor.worker': graphiqlReact.resolve('monaco-editor/esm/vs/editor/editor.worker.js'),
  'json.worker': graphiqlReact.resolve('monaco-editor/esm/vs/language/json/json.worker.js'),
  'graphql.worker': graphiqlReact.resolve('monaco-graphql/esm/graphql.worker.js'),
};

async function buildScripts() {
  await Promise.all([
    esbuild.build({
      ...common,
      entryPoints: { netbox: 'src/index.ts' },
      sourcemap: 'linked',
      target: 'es2016',
    }),
    // An ES module, so that it can locate the workers via import.meta.url. The CSS it imports
    // (including Monaco's, which references the codicon font) is written to graphiql.css.
    esbuild.build({
      ...common,
      outdir: `${outdir}/graphiql`,
      entryPoints: { graphiql: 'src/graphiql.ts' },
      format: 'esm',
      loader: { '.ttf': 'file' },
    }),
    // Classic (non-module) workers
    esbuild.build({
      ...common,
      outdir: `${outdir}/graphiql`,
      entryPoints: monacoWorkers,
      format: 'iife',
    }),
  ]);
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
        // Hide deprecation warnings raised by third-party stylesheets (Bootstrap, Tabler, etc.)
        quietDeps: true,
        // NetBox's own SCSS still relies on @import, which Dart Sass 3 will remove
        silenceDeprecations: ['import'],
      }),
    ],
    loader: { '.woff2': 'file', '.svg': 'file' },
  });
}

/**
 * Swap the staging directory into place as dist/. The previous dist/ is set aside first and
 * restored if the swap fails, so that dist/ is never left missing.
 */
async function replaceDist() {
  await rm(BACKUP_DIR, { recursive: true, force: true });
  let hasBackup = false;
  try {
    await rename('dist', BACKUP_DIR);
    hasBackup = true;
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  try {
    await rename(STAGING_DIR, 'dist');
  } catch (error) {
    if (hasBackup) {
      try {
        await rename(BACKUP_DIR, 'dist');
      } catch (restoreError) {
        throw new Error(
          `${error.message}; the previous dist/ could not be restored and remains in ${BACKUP_DIR}/`,
          { cause: restoreError },
        );
      }
    }
    throw error;
  }
  await rm(BACKUP_DIR, { recursive: true, force: true }).catch(error => {
    console.warn(`Could not remove ${BACKUP_DIR}/: ${error.message}`);
  });
}

try {
  if (fullBuild) {
    await rm(STAGING_DIR, { recursive: true, force: true });
  }
  if (!args.includes('--scripts')) await buildStyles();
  if (!args.includes('--styles')) await buildScripts();
  if (fullBuild) {
    await replaceDist();
  }
} catch (error) {
  // esbuild prints its own errors before throwing; report anything else (e.g. a failed copy)
  if (!error?.errors) {
    console.error(error);
  }
  if (fullBuild) {
    await rm(STAGING_DIR, { recursive: true, force: true });
  }
  process.exit(1);
}
