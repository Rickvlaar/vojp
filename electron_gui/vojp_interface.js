const {spawn, execSync} = require('child_process');
const {path} = require('path')

module.exports = {

    getVojpSettings: function () {
        const vojpSettings = execSync('venv/bin/python vojp_cli.py -s', {
                cwd: '/Users/rickforce/PycharmProjects/vojp'
            })
        return JSON.parse(vojpSettings.toString())
    },

    startVojp: function (settings) {
        const jsonSettings = JSON.stringify(settings)
        const vojp = spawn('venv/bin/python', ['main.py', '-s', jsonSettings], {
            cwd: '/Users/rickforce/PycharmProjects/vojp/'
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