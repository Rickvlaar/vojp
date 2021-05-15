const {app, ipcMain, webContents, BrowserWindow, Menu} = require('electron')
const path = require('path')
const vojp = require('./vojp_interface')
const inputTemplates = require('./templates/input_templates')

function createWindow() {
    const win = new BrowserWindow({
        title: 'vojp',
        width: 1200,
        height: 800,
        frame: false,
        hasShadow: true,
        backgroundColor: '#282C34',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            // nodeIntegration: true,
            // contextIsolation: false
        }
    })

    win.loadFile('index.html')
    win.toggleDevTools()
    return win
}

function createMenu() {
    let template = [{
        label: 'Electron',
        submenu: [
            {label: 'yes'},
            {label: 'no'}
        ]
    }, {
        label: 'lemalin',
        submenu: [
            {label: 'oui'},
            {label: 'non'}
        ]
    }, {
        label: 'gangstu',
        submenu: [
            {label: 'aight'},
            {label: 'nggggon'}
        ]
    }]

    const menu = Menu.buildFromTemplate(
        template
    )
    Menu.setApplicationMenu(menu)
}

app.commandLine.appendSwitch('remote-debugging-port', '9222')

app.whenReady().then(() => {
    let mainWin = createWindow()
    createMenu()
    const vojpSettings = vojp.getVojpSettings()

    Object.entries(vojpSettings).forEach((setting) => {
        if (setting[1].input_type === 'datalist') {
            setting[1].htmlString = inputTemplates.datalist(setting[0], setting[1].options, setting[1].default)
        } else if (setting[1].input_type === 'input') {
            setting[1].htmlString = inputTemplates.textInput(setting[0], setting[1].default)
        } else if (setting[1].input_type === 'checkbox') {
            setting[1].htmlString = inputTemplates.checkboxInput(setting[0], setting[1].default)
        }
    })

    mainWin.webContents.send('new_settings', vojpSettings)

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow()
        }
    })

})

ipcMain.on('connect-to-vojp', (event, settings) => {
        console.log('connecting to backend')
        vojp.startVojp(settings)
    }
)

app.on('window-all-closed', () => {
    // if (process.platform !== 'darwin') {
    app.quit()
    // }
})