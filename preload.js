const {ipcRenderer} = require('electron')

let vojp_settings

ipcRenderer.on('new_settings', (event, settings) => {
    let connectionSettingsDiv = document.createElement('div')
    let deviceSettingsDiv = document.createElement('div')
    let sessionSettingsDiv = document.createElement('div')

    Object.entries(settings).forEach(setting => {
        if (setting[1].setting_type === 'connection') {
            connectionSettingsDiv.innerHTML += setting[1].htmlString
        } else if (setting[1].setting_type === 'device') {
            deviceSettingsDiv.innerHTML += setting[1].htmlString
        } else if (setting[1].setting_type === 'session') {
            sessionSettingsDiv.innerHTML += setting[1].htmlString
        }
    })
    vojp_settings = settings

    document.getElementById('connection-settings').insertAdjacentElement("beforeend", connectionSettingsDiv)
    document.getElementById('device-settings').insertAdjacentElement("beforeend", deviceSettingsDiv)
    document.getElementById('session-settings').insertAdjacentElement("beforeend", sessionSettingsDiv)
})

ipcRenderer.on('update_latency', (event, latency) => {
    document.getElementById('latency').innerHTML = latency
})

window.addEventListener('DOMContentLoaded', () => {
    const closeButton = document.getElementById('close-vojp-button')
    closeButton.addEventListener('click', () => {
        console.log('quitting')
        window.close()
    })

    const connectButton = document.getElementById('connect-vojp-button')
    connectButton.addEventListener('click', () => {
        console.log('starting vojp backend');
        updateConnectButtonState(connectButton) // disable the button after click
        let newSettings = processSettings() // update settings to match user input
        ipcRenderer.send('connect-to-vojp', newSettings)
    })

    function updateConnectButtonState(connectButton){
        connectButton.checked = true
        connectButton.disabled = true
        connectButton.innerHTML = 'connected'
        connectButton.className = 'btn btn-info vojp_text'
    }

    function processSettings(){
        let newSettings = {}
        let inputs = document.getElementsByTagName('input')
        let selects = document.getElementsByTagName('select')
        for (let i = 0; i < inputs.length; i++){
            let this_input = inputs[i]
            if(this_input.checked === true){
                this_input.value = 'true'
            }
            newSettings[this_input.id] = this_input.value
        }
        for (let i = 0; i < selects.length; i++){
            let this_select = selects[i]
            newSettings[this_select.id] = this_select.value
        }
        return newSettings
    }
})

