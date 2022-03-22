const write = require('write')
const { exec } = require('child_process')

exec('git rev-parse HEAD', function(err, stdout) {
  write.sync('dist/commitHash.txt', 'This is a build of commit: ' + stdout);
})