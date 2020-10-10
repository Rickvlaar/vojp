import asyncio
from audio_processor import get_all_devices
from client import UdpClient, start_client
import tkinter as tk
import signal


class Gui:

    def __init__(self):
        self.gui = tk.Tk(screenName='Vojp')
        self.frame = tk.Frame()
        self.ip_address_input = tk.Entry()
        self.port_input = tk.Entry()

        self.input_sample_rate_var = tk.IntVar(name='input_sample_rate', value=48000)
        self.output_sample_rate_var = tk.IntVar(name='output_sample_rate', value=48000)

        sample_rate_options = [48000, 32000, 16000, 12000, 8000]

        self.input_sample_rate_select = tk.OptionMenu(self.gui,
                                                      self.input_sample_rate_var,
                                                      sample_rate_options[0],
                                                      *sample_rate_options[1:])
        self.output_sample_rate_select = tk.OptionMenu(self.gui,
                                                       self.output_sample_rate_var,
                                                       sample_rate_options[0],
                                                       *sample_rate_options[1:])

        sound_devices = get_all_devices()
        input_devices = list("")
        output_devices = list("")
        for sound_device in sound_devices:
            if sound_device['max_input_channels'] > 0:
                input_devices.append(sound_device['name'])
            if sound_device['max_output_channels'] > 0:
                output_devices.append(sound_device['name'])
        self.input_device_var = tk.StringVar(name=input_devices[0], value=input_devices[0])
        self.output_device_var = tk.StringVar(name=output_devices[0], value=output_devices[0])

        self.input_device_select = tk.OptionMenu(self.gui,
                                                 self.input_device_var,
                                                 input_devices[0],
                                                 *tuple(input_devices)[1:])

        self.output_device_select = tk.OptionMenu(self.gui,
                                                  self.output_device_var,
                                                  output_devices[0],
                                                  *tuple(output_devices)[1:])

    def start_gui(self):
        self.frame.pack()

        vojp_label = tk.Label(text='Vojp', font='Helvetica, 30')
        vojp_label.pack()

        ip_label = tk.Label(text='IP Address')
        ip_label.pack()
        self.ip_address_input.pack()
        self.ip_address_input.insert(0, '31.151.58.233')

        port_label = tk.Label(text='Port')
        port_label.pack()
        self.port_input.pack()
        self.port_input.insert(0, '5000')

        input_device_label = tk.Label(text='Select Input Device')
        input_device_label.pack()
        self.input_device_select.pack()

        input_sample_rate_label = tk.Label(text='Select Input Sample Rate')
        input_sample_rate_label.pack()
        self.input_sample_rate_select.pack()

        output_device_label = tk.Label(text='Select Output Device')
        output_device_label.pack()
        self.output_device_select.pack()

        output_sample_rate_label = tk.Label(text='Select Output Sample Rate')
        output_sample_rate_label.pack()
        self.output_sample_rate_select.pack()

        button = tk.Button(command=self.connect_client, text='Connect', height=2, width=10, fg='green', bg='black',
                           activeforeground='white')
        button.pack()

        self.gui.mainloop()

    def connect_client(self):
        ip = self.ip_address_input.get()
        port = int(self.port_input.get())
        audio_input_device_name = self.input_device_var.get()
        audio_output_device_name = self.output_device_var.get()
        input_sample_rate = self.input_sample_rate_var.get()
        output_sample_rate = self.output_sample_rate_var.get()

        print('clicked!')
        print('input: ' + audio_input_device_name)
        print('output: ' + audio_output_device_name)

        asyncio.gather(start_client(ip=ip,
                                    port=port,
                                    input_sample_rate=input_sample_rate,
                                    output_sample_rate=output_sample_rate,
                                    audio_input_device_name=audio_input_device_name,
                                    audio_output_device_name=audio_output_device_name),
                       self.run_gui_async())

        self.gui.quit()

    async def run_gui_async(self):
        while True:
            try:
                self.gui.update()
                await asyncio.sleep(0.1)
            except:
                from main import shutdown
                await shutdown()
