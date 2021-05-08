import asyncio
import logging
import configparser
from vojp.audio_processor import get_all_devices
from vojp.client import UdpClient
from vojp.server import AsyncUdpServer
import tkinter as tk
import tkinter.ttk as ttk


class Gui:

    def __init__(self):
        self.gui = tk.Tk(className='Vojp', baseName='Vojp', screenName='Vojp')
        self.frame = ttk.Frame(master=self.gui)
        self.right_frame = ttk.Frame(master=self.frame, borderwidth=25)

        style = ttk.Style()
        style.map('TButton',
                  foreground=[('disabled', 'green')])

        self.ip_address_input = ttk.Entry(master=self.frame)
        self.port_input = ttk.Entry(master=self.frame)

        debug_level_options = ['INFO', 'DEBUG']
        self.debug_level_var = tk.StringVar(master=self.frame,
                                            value=debug_level_options[0])

        self.debug_level_select = ttk.OptionMenu(self.frame,
                                                 self.debug_level_var,
                                                 debug_level_options[0],
                                                 *debug_level_options)

        self.input_sample_rate_var = tk.IntVar(master=self.frame, name='input_sample_rate', value=48000)
        self.output_sample_rate_var = tk.IntVar(master=self.frame, name='output_sample_rate', value=48000)

        sample_rate_options = [48000, 32000, 16000, 12000, 8000]

        self.input_sample_rate_select = ttk.OptionMenu(self.frame,
                                                       self.input_sample_rate_var,
                                                       sample_rate_options[0],
                                                       *sample_rate_options)
        self.output_sample_rate_select = ttk.OptionMenu(self.frame,
                                                        self.output_sample_rate_var,
                                                        sample_rate_options[0],
                                                        *sample_rate_options)

        sound_devices = get_all_devices()
        self.device_id_name_dict = {device['device_index']: device['name'] for device in sound_devices}
        self.device_name_id_dict = {device['name']: device['device_index'] for device in sound_devices}
        input_devices = [str(sound_device['device_index']) + '. ' + sound_device['name'] for sound_device in
                         sound_devices if sound_device['max_input_channels'] > 0]
        output_devices = [str(sound_device['device_index']) + '. ' + sound_device['name'] for sound_device in
                          sound_devices if sound_device['max_output_channels'] > 0]

        self.input_device_var = tk.StringVar(master=self.frame,
                                             value=input_devices[0])
        self.output_device_var = tk.StringVar(master=self.frame,
                                              value=output_devices[0])

        self.input_device_select = ttk.OptionMenu(self.frame,
                                                  self.input_device_var,
                                                  input_devices[0],
                                                  *input_devices)

        self.output_device_select = ttk.OptionMenu(self.frame,
                                                   self.output_device_var,
                                                   output_devices[0],
                                                   *output_devices)

        self.connect_button = ttk.Button(master=self.frame, command=self.connect_client, text='Connect',
                                         width=10)

        self.packet_length = ttk.Entry(master=self.right_frame)
        self.buffer_size = ttk.Entry(master=self.right_frame)

        self.start_server_var = tk.BooleanVar(master=self.right_frame, value=False)
        self.start_server_checkbox = ttk.Checkbutton(master=self.right_frame, text='start server',
                                                     variable=self.start_server_var)
        self.echo_mode_var = tk.BooleanVar(master=self.right_frame, value=False)
        self.echo_mode_checkbox = ttk.Checkbutton(master=self.right_frame, text='echo mode',
                                                  variable=self.echo_mode_var)

        self.record_var = tk.BooleanVar(master=self.right_frame, value=False)
        self.record_checkbox = ttk.Checkbutton(master=self.right_frame, text='record',
                                               variable=self.record_var)

        self.latency_var = tk.StringVar(master=self.right_frame, value=0)
        self.read_config()

    def read_config(self):
        config = configparser.ConfigParser()
        config.read('vojp_config.ini')
        default_settings = config['DEFAULT']
        self.ip_address_input.insert(0, default_settings['ip'])
        self.port_input.insert(0, default_settings['port'])
        self.input_device_var.set(self.device_id_name_dict.get(int(default_settings['audio_input_device_id'])))
        self.output_device_var.set(self.device_id_name_dict.get(int(default_settings['audio_output_device_id'])))

    def save_config(self):
        config = configparser.ConfigParser()
        default_settings = config['DEFAULT']
        default_settings['ip'] = self.ip_address_input.get()
        default_settings['port'] = self.port_input.get()
        bla = self.input_device_var.get()
        default_settings['audio_input_device_id'] = str(self.device_name_id_dict.get(self.input_device_var.get().lstrip('0123456789. ')))
        default_settings['audio_output_device_id'] = str(self.device_name_id_dict.get(self.output_device_var.get().lstrip('0123456789. ')))
        with open('vojp_config.ini', 'w') as configfile:
            config.write(configfile)

    def start_gui(self):
        self.frame.pack()
        self.right_frame.pack(side='right')

        vojp_label = ttk.Label(master=self.frame, text='Vojp', font='Helvetica, 30')
        vojp_label.pack()

        ip_label = ttk.Label(master=self.frame, text='IP Address')
        ip_label.pack()
        self.ip_address_input.pack()

        port_label = ttk.Label(master=self.frame, text='Port')
        port_label.pack()
        self.port_input.pack()

        debug_level_label = ttk.Label(master=self.frame, text='Set Debug Level')
        debug_level_label.pack()
        self.debug_level_select.pack()

        input_device_label = ttk.Label(master=self.frame, text='Select Input Device')
        input_device_label.pack()
        self.input_device_select.pack()

        input_sample_rate_label = ttk.Label(master=self.frame, text='Select Input Sample Rate')
        input_sample_rate_label.pack()
        self.input_sample_rate_select.pack()

        output_device_label = ttk.Label(master=self.frame, text='Select Output Device')
        output_device_label.pack()
        self.output_device_select.pack()

        output_sample_rate_label = ttk.Label(master=self.frame, text='Select Output Sample Rate')
        output_sample_rate_label.pack()
        self.output_sample_rate_select.pack()

        packet_length_label = ttk.Label(master=self.right_frame, text='Set Packet Length (ms)')
        packet_length_label.pack()
        self.packet_length.pack()
        self.packet_length.insert(0, '10')

        buffer_size_label = ttk.Label(master=self.right_frame, text='Set Buffer Size (ms)')
        buffer_size_label.pack()
        self.buffer_size.pack()
        self.buffer_size.insert(0, '10')

        self.connect_button.pack()
        self.start_server_checkbox.pack()
        self.echo_mode_checkbox.pack()
        self.record_checkbox.pack()

        latency_label = ttk.Label(master=self.right_frame, text='Latency (ms)')
        latency_label.pack()
        latency_var = ttk.Label(master=self.right_frame, textvariable=self.latency_var)
        latency_var.pack()

        self.gui.mainloop()

    def connect_client(self):
        ip = self.ip_address_input.get()
        port = int(self.port_input.get())
        debug_level = self.debug_level_var.get()
        audio_input_device_id = self.device_name_id_dict.get(self.input_device_var.get())
        audio_output_device_id = self.device_name_id_dict.get(self.output_device_var.get())
        input_sample_rate = self.input_sample_rate_var.get()
        output_sample_rate = self.output_sample_rate_var.get()
        start_server = self.start_server_var.get()
        echo_mode = self.echo_mode_var.get()
        record_audio = self.record_var.get()

        self.save_config()

        logging.getLogger().setLevel(level=debug_level)
        logging.info(msg='Application started')
        logging.info(msg='Input device id: ' + str(audio_input_device_id))
        logging.info(msg='Output device id: ' + str(audio_output_device_id))

        self.client = UdpClient(ip=ip,
                                port=port,
                                input_sample_rate=input_sample_rate,
                                output_sample_rate=output_sample_rate,
                                audio_input_device_id=audio_input_device_id,
                                audio_output_device_id=audio_output_device_id,
                                record_audio=record_audio)

        # Start Server if asked
        if start_server:
            server = AsyncUdpServer(echo_mode=echo_mode)
            asyncio.gather(server.start_server())

        asyncio.gather(self.client.start_client(),
                       self.run_gui_async())

        self.gui.quit()

    async def show_connected_state(self):
        self.connect_button.state(['disabled'])
        self.connect_button['text'] = 'Connected'

    async def run_gui_async(self):
        await self.show_connected_state()
        while True:
            try:
                logging.debug(msg='Gui updating')
                self.latency_var.set(self.client.latency)
                self.gui.update()
                logging.debug(msg='Gui update finished')
                await asyncio.sleep(0.1)
            except:
                from vojp.main import shutdown
                await shutdown()
