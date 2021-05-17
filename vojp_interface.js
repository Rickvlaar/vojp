const {spawn, execSync} = require('child_process');
const path = require('path')
const os = require('os')


const vojpPath = __dirname
let commandPath
if (os.type() !== 'Darwin') {
    commandPath = path.normalize('venv/scripts/python')
} else {
    commandPath = path.normalize('venv/bin/python')
}


module.exports = {
    getVojpSettings: function () {
        const vojpSettings = execSync(commandPath + ' vojp_cli.py -s', {
            cwd: vojpPath
        })
        return JSON.parse(vojpSettings.toString())
    },

    startVojp: function (settings) {
        const jsonSettings = JSON.stringify(settings)
        const vojp = spawn(commandPath, ['main.py', '-s', jsonSettings], {
            cwd: vojpPath
        })
        vojp.stdout.on('data', function (data) {
            console.log("data: ", data.toString('utf8'));
        });
        vojp.stderr.on('data', function (data) {
            console.log("data: ", data.toString('utf8'));
        });
        return vojp
    }
}