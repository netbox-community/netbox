// Upgrade every direct dependency to its latest release (except those held below), then refresh
// transitive dependencies within their declared ranges. Run as part of each release.
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

// Dependencies that must stay below their latest release. Remove an entry once its blocker is gone.
const HELD = {
  '@tabler/core': { range: '1.4.x', reason: 'Upgrade tracked in #23184' },
  '@graphiql/plugin-explorer': { range: '4.x', reason: 'v5 drops the UMD build we copy' },
  graphiql: { range: '4.x', reason: 'v5 drops the UMD build we copy' },
  graphql: { range: '16.x', reason: 'Peer range of the GraphiQL 4 explorer plugin' },
  'htmx.org': { range: '2.x', reason: 'htmx 4 renames events that plugins listen for' },
  react: { range: '18.x', reason: 'React 19 ships no UMD build' },
  'react-dom': { range: '18.x', reason: 'React 19 ships no UMD build' },
  sass: { range: '<3', reason: 'Dart Sass 3 removes @import, which our SCSS still uses' },
  typescript: { range: '<7', reason: 'typescript-eslint does not support TypeScript 7' },
};

const npm = (...args) =>
  execFileSync('npm', args, { encoding: 'utf8', stdio: ['inherit', 'pipe', 'inherit'] });
const pkg = JSON.parse(readFileSync('package.json', 'utf8'));
const specs = deps => Object.keys(deps).map(name => `${name}@${HELD[name]?.range ?? 'latest'}`);

npm('install', ...specs(pkg.dependencies));
npm('install', '--save-dev', ...specs(pkg.devDependencies));
npm('update');

// Report anything still behind its latest release. `npm outdated` exits 1 when it lists packages.
let outdated = {};
try {
  npm('outdated', '--json');
} catch (error) {
  outdated = JSON.parse(error.stdout || '{}');
}
for (const [name, { current, latest }] of Object.entries(outdated)) {
  const why = HELD[name]?.reason ?? 'newest release is inside the min-release-age window';
  console.log(`${name.padEnd(28)} ${current.padEnd(9)} latest ${latest.padEnd(9)} ${why}`);
}
