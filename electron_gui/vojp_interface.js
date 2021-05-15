const {spawn, execSync} = require('child_process');


module.exports = {

    getVojpSettings: function () {
        const vojpSettings = execSync('venv/bin/python vojp/electron_gui_interface.py -s', {
                cwd: '/Users/rickforce/PycharmProjects/vojp'
            })
        return JSON.parse(vojpSettings.toString())
    },

    startVojp: function (settings) {
        const jsonSettings = JSON.stringify(settings)
        const vojp = spawn('venv/bin/python', ['main.py', '-s',jsonSettings], {
            cwd: '/Users/rickforce/PycharmProjects/vojp/',
            env: {
                PATH: process.env.PATH
            }
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