const { exec, execSync } = require('child_process');
const chokidar = require('chokidar');

const sassWatcher = chokidar.watch('styles/**/*.scss');
const tsWatcher = chokidar.watch('src/**/*.ts');

const collectStatic = type => {
  console.log('[*] bundling..');
  let args = '';
  if (type === 'style') args += '--styles';
  if (type === 'script') args += '--scripts';
  execSync(`node bundle.js ${args}`);

  console.log('[*] collecting..');
  exec('../../venv/bin/python3 ../manage.py collectstatic --no-input', (err, stdout, stderr) => {
    err && console.error(err);
    stdout && console.log(`[*] ${stdout.trim()}`);
    stderr && console.log('[**] Python Err:', stderr);
    console.log('[*] waiting..\n');
  });
};

sassWatcher.on('change', path => {
  console.log(`[*] '${path}' has changed`);
  collectStatic('style');
});

tsWatcher.on('change', path => {
  console.log(`[*] '${path}' has changed`);
  collectStatic('script');
});
