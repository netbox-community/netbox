const { execSync } = require('child_process');
const chokidar = require('chokidar');

const sassWatcher = chokidar.watch('styles/**/*.scss');
const tsWatcher = chokidar.watch('src/**/*.ts');

const collectStatic = type => {
  console.log('[*] bundling..');
  execSync(`node bundle.js ${type && `--${type}`}`);
  console.log('[*] waiting..\n');
};

sassWatcher.on('change', path => {
  console.log(`[*] '${path}' has changed`);
  collectStatic('styles');
});

tsWatcher.on('change', path => {
  console.log(`[*] '${path}' has changed`);
  collectStatic('scripts');
});
