const {spawn, execSync} = require('child_process');
const path = require('path')

const vojpPath = path.join(__dirname, '../')
const commandPath =  path.normalize('venv/bin/python')


module.exports = {
    getVojpSettings: function () {
        const vojpSettings = execSync(commandPath + ' vojp_cli.py -s', {
                cwd: vojpPath
            })
        return JSON.parse(vojpSettings.toString())
    },

    startVojp: function (settings) {
        let vojpPath = path.join(__dirname, '../')
        let commandPath =  path.normalize('venv/bin/python')

        const jsonSettings = JSON.stringify(settings)
        const vojp = spawn(commandPath, ['main.py', '-s', jsonSettings], {
            cwd: vojpPath
        })

        vojp.on("error", function (error) {
            console.log("Error!!! : " + error);
            throw error;
        })

        vojp.stdout.on('data', function (data) {
            console.log("data: ", data.toString('utf8'));
        });
        vojp.stderr.on('data', function (data) {
            console.log("data: ", data.toString('utf8'));
        });
    }
}