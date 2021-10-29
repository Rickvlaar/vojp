const {spawn, execSync} = require('child_process');
const path = require('path')
const os = require('os')


let commandPath
if (os.type() !== 'Darwin') {
    commandPath = path.join(process.resourcesPath, "main")
} else {
    commandPath = path.join(process.resourcesPath, "main")
}


module.exports = {
    getVojpSettings: function () {
        // const vojpSettings = execSync(commandPath + ' -m vojp.vojp_cli -s', {
        //     cwd: vojpPath
        // })
        console.log(commandPath)
        const vojpSettings = execSync('./main -g', {
            cwd: commandPath
        })
        console.log(vojpSettings.toString())
        console.log(JSON.parse(vojpSettings.toString()))
        return JSON.parse(vojpSettings.toString())
    },

    startVojp: function (settings) {
        const jsonSettings = JSON.stringify(settings)
        // const vojp = spawn(commandPath, ['-m', 'vojp.main', '-s', jsonSettings], {
        //     cwd: vojpPath
        // })

        const vojp = spawn('./main', ['-s', jsonSettings], {
            cwd: commandPath
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