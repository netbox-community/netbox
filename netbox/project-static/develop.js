const { exec, execSync } = require('child_process');
const chokidar = require('chokidar');

const sassWatcher = chokidar.watch('styles/**/*.scss');
const tsWatcher = chokidar.watch('src/**/*.ts');

const collectStatic = type => {
  console.log('[*] bundling..');
  execSync(`node bundle.js ${type && `--${type}`}`);

  console.log('[*] collecting..');
  exec('../../venv/bin/python3 ../manage.py collectstatic --no-input', (err, stdout, stderr) => {
    err && console.error(`[**] Error: ${err}`);
    stdout && console.log(`[*] ${stdout.trim()}`);
    stderr && console.log(`[**] Python Err: ${stderr.trim()}`);
    console.log('[*] waiting..\n');
  });
};

sassWatcher.on('change', path => {
  console.log(`[*] '${path}' has changed`);
  collectStatic('styles');
});

tsWatcher.on('change', path => {
  console.log(`[*] '${path}' has changed`);
  collectStatic('scripts');
});
