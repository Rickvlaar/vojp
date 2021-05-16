const {readline} = require('readline')

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

process.argv.forEach((val, index) => {
    console.log(`${index}: ${val}`)
    if(val === '-l' || val === '--latency'){
        updateLatency()
    }
})

rl.on('line', (input) => {
  console.log(`Received: ${input}`);
});

function updateLatency(latency){
    console.log('yes updaitng lat')
    // console.log(remote.getCurrentWindow());
    // ipcRenderer.send('update_latency', 10)
}