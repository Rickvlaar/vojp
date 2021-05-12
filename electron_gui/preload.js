const {ipcRenderer} = require('electron')

ipcRenderer.on('new_settings', (event, settings) => {
    console.log('settings received')

    let div = document.createElement('div')

    settings.forEach(setting => {
        div.innerHTML += setting
    })
    document.getElementById('column-1').insertAdjacentElement("beforeend", div)
})

