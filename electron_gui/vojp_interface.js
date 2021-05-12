const {spawn, execSync} = require('child_process');


module.exports = {

    getVojpSettings: function () {
        const vojpSettings = execSync('venv/bin/python vojp/electron_gui_interface.py -s', {
                cwd: '/Users/rickforce/PycharmProjects/vojp'
            })
        return JSON.parse(vojpSettings.toString())
    },

    startVojp: function () {
        const vojp = spawn('venv/bin/python', ['main.py'], {
            // detached: true,
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
    }
}