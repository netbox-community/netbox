// Upgrade every direct dependency to its latest release (except those held below), then refresh
// transitive dependencies within their declared ranges. Run as part of each release.
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

// Dependencies that must stay below their latest release. Remove an entry once its blocker is gone.
// A range of 'patch' allows only patch releases of the version currently in package.json.
const REVIEW_SEPARATELY = 'Minor and major upgrades are reviewed separately';
const HELD = {
  '@tabler/core': { range: 'patch', reason: REVIEW_SEPARATELY },
  bootstrap: { range: 'patch', reason: REVIEW_SEPARATELY },
  '@graphiql/plugin-explorer': { range: '4.x', reason: 'v5 drops the UMD build we copy' },
  graphiql: { range: '4.x', reason: 'v5 drops the UMD build we copy' },
  graphql: { range: '16.x', reason: 'Peer range of the GraphiQL 4 explorer plugin' },
  'htmx.org': { range: '2.x', reason: 'htmx 4 renames events that plugins listen for' },
  react: { range: '18.x', reason: 'React 19 ships no UMD build' },
  'react-dom': { range: '18.x', reason: 'React 19 ships no UMD build' },
  sass: { range: '<3', reason: 'Dart Sass 3 removes @import, which our SCSS still uses' },
  typescript: { range: '6.0.x', reason: 'typescript-eslint supports TypeScript < 6.1' },
};

// Resolve package.json relative to this directory, regardless of where the script is invoked from.
process.chdir(dirname(fileURLToPath(import.meta.url)));

// Run npm via the same CLI script that launched `npm run upgrade` (npm_execpath), falling back to
// `npm` on the PATH. On Windows, `npm` is a .cmd shim, which execFileSync() can't run directly.
const npmCli = process.env.npm_execpath;
const npm = (...args) =>
  execFileSync(npmCli ? process.execPath : 'npm', npmCli ? [npmCli, ...args] : args, {
    encoding: 'utf8',
    stdio: ['inherit', 'pipe', 'inherit'],
  });
const pkg = JSON.parse(readFileSync('package.json', 'utf8'));
const specFor = (name, version) => {
  const range = HELD[name]?.range ?? 'latest';
  return `${name}@${range === 'patch' ? `~${version.replace(/^[\^~]/, '')}` : range}`;
};
const specs = deps => Object.entries(deps).map(([name, version]) => specFor(name, version));

npm('install', ...specs(pkg.dependencies));
npm('install', '--save-dev', ...specs(pkg.devDependencies));
npm('update');

// Report anything still behind its latest release. `npm outdated` exits 1 when it lists packages.
let outdated = {};
try {
  npm('outdated', '--json');
} catch (error) {
  // Any exit status other than 1 means npm outdated itself failed
  if (error.status !== 1) throw error;
  outdated = JSON.parse(error.stdout);
}
if (outdated.error) {
  console.error(`npm outdated failed: ${outdated.error.summary ?? outdated.error.code}`);
  process.exit(1);
}
for (const [name, { current = 'missing', latest = 'unknown' }] of Object.entries(outdated)) {
  const why = HELD[name]?.reason ?? 'not held, but was not upgraded; investigate';
  console.log(`${name.padEnd(28)} ${current.padEnd(9)} latest ${latest.padEnd(9)} ${why}`);
}
