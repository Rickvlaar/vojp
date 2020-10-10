import asyncio
from audio_processor import get_all_devices
from client import UdpClient, start_client
import tkinter as tk


class Gui:

    def __init__(self):
        self.gui = tk.Tk(className='Vojp', baseName='Vojp', screenName='Vojp')
        self.frame = tk.Frame(master=self.gui)
        self.ip_address_input = tk.Entry(master=self.frame)
        self.port_input = tk.Entry(master=self.frame)

        self.input_sample_rate_var = tk.IntVar(master=self.frame, name='input_sample_rate', value=48000)
        self.output_sample_rate_var = tk.IntVar(master=self.frame, name='output_sample_rate', value=48000)

        sample_rate_options = [48000, 32000, 16000, 12000, 8000]

        self.input_sample_rate_select = tk.OptionMenu(self.frame,
                                                      self.input_sample_rate_var,
                                                      sample_rate_options[0],
                                                      *sample_rate_options[1:])
        self.output_sample_rate_select = tk.OptionMenu(self.frame,
                                                       self.output_sample_rate_var,
                                                       sample_rate_options[0],
                                                       *sample_rate_options[1:])

        sound_devices = get_all_devices()
        input_devices = [str(sound_device['device_index']) + '. ' + sound_device['name'] for sound_device in sound_devices if sound_device['max_input_channels'] > 0]
        output_devices = [str(sound_device['device_index']) + '. ' + sound_device['name'] for sound_device in sound_devices if sound_device['max_output_channels'] > 0]

        self.input_device_var = tk.StringVar(master=self.frame,
                                             value=input_devices[0])
        self.output_device_var = tk.StringVar(master=self.frame,
                                              value=output_devices[0])

        self.input_device_select = tk.OptionMenu(self.frame,
                                                 self.input_device_var,
                                                 input_devices[0],
                                                 *tuple(input_devices)[1:])

        self.output_device_select = tk.OptionMenu(self.frame,
                                                  self.output_device_var,
                                                  output_devices[0],
                                                  *tuple(output_devices)[1:])

        self.connect_button = tk.Button(master=self.frame, command=self.connect_client, text='Connect', height=2,
                                        width=10, fg='black',
                                        activeforeground='white')

    def start_gui(self):
        self.frame.pack()

        vojp_label = tk.Label(master=self.frame, text='Vojp', font='Helvetica, 30')
        vojp_label.pack()

        ip_label = tk.Label(master=self.frame, text='IP Address')
        ip_label.pack()
        self.ip_address_input.pack()
        self.ip_address_input.insert(0, '31.151.58.233')

        port_label = tk.Label(master=self.frame, text='Port')
        port_label.pack()
        self.port_input.pack()
        self.port_input.insert(0, '5000')

        input_device_label = tk.Label(master=self.frame, text='Select Input Device')
        input_device_label.pack()
        self.input_device_select.pack()

        input_sample_rate_label = tk.Label(master=self.frame, text='Select Input Sample Rate')
        input_sample_rate_label.pack()
        self.input_sample_rate_select.pack()

        output_device_label = tk.Label(master=self.frame, text='Select Output Device')
        output_device_label.pack()
        self.output_device_select.pack()

        output_sample_rate_label = tk.Label(master=self.frame, text='Select Output Sample Rate')
        output_sample_rate_label.pack()
        self.output_sample_rate_select.pack()

        self.connect_button.pack()

        self.gui.mainloop()

    def connect_client(self):
        ip = self.ip_address_input.get()
        port = int(self.port_input.get())
        audio_input_device_id = self.input_device_var.get()[0]
        audio_output_device_id = self.output_device_var.get()[0]
        input_sample_rate = self.input_sample_rate_var.get()
        output_sample_rate = self.output_sample_rate_var.get()

        print('clicked!')
        print('input: ' + audio_input_device_id)
        print('output: ' + audio_output_device_id)

        asyncio.gather(start_client(ip=ip,
                                    port=port,
                                    input_sample_rate=input_sample_rate,
                                    output_sample_rate=output_sample_rate,
                                    audio_input_device_id=audio_input_device_id,
                                    audio_output_device_id=audio_output_device_id),
                       self.run_gui_async())

        self.gui.quit()

    async def show_connected_state(self):
        self.connect_button['state'] = 'disabled'
        self.connect_button['text'] = 'Connected'
        self.connect_button['bg'] = 'green'

    async def run_gui_async(self):
        await self.show_connected_state()
        while True:
            try:
                self.gui.update()
                await asyncio.sleep(0.1)
            except:
                from main import shutdown
                await shutdown()
