import json
import argparse
import sys
import audio_processor
import configparser
from config import Config


class ElectronGuiSettings:
    debug_level_options = ['INFO', 'DEBUG']
    sample_rate_options = [48000, 32000, 16000, 12000, 8000]
    input_devices_dict = {device['device_index']: device['name'] for device in audio_processor.get_all_devices() if device['max_input_channels'] > 0}
    output_devices_dict = {device['device_index']: device['name'] for device in audio_processor.get_all_devices() if device['max_output_channels'] > 0}

    def __init__(self):
        self.ip_address = self.Setting(input_type='input')
        self.port = self.Setting(input_type='input', default=5000)
        self.debug_level = self.Setting(input_type='datalist', options=self.debug_level_options, default='INFO')
        self.input_sample_rate = self.Setting(input_type='datalist', options=self.sample_rate_options, default=48000)
        self.output_sample_rate = self.Setting(input_type='datalist', options=self.sample_rate_options, default=48000)
        self.input_device = self.Setting(input_type='datalist', options=self.input_devices_dict)
        self.output_device = self.Setting(input_type='datalist', options=self.output_devices_dict)
        self.packet_length = self.Setting(input_type='input', default=10)
        self.buffer_size = self.Setting(input_type='input', default=10)
        self.host_server = self.Setting(input_type='checkbox', default=False)
        self.echo_mode = self.Setting(input_type='checkbox', default=False)
        self.record = self.Setting(input_type='checkbox', default=False)
        self.read_config()

    def read_config(self):
        parser = configparser.ConfigParser()
        parser.read(Config.CONFIG_FILE)
        default_settings = parser['DEFAULT']
        self.ip_address.default = default_settings.get('ip')
        self.port.default = default_settings.get('port') if default_settings.get('port') else 5000
        self.input_device.default = self.input_devices_dict.get(int(default_settings['audio_input_device_id']))
        self.output_device.default = self.output_devices_dict.get(int(default_settings['audio_output_device_id']))

    # def save_config(self):
    #     parser = configparser.ConfigParser()
    #     default_settings = parser['DEFAULT']
    #     default_settings['ip'] = self.ip_address_input.get()
    #     default_settings['port'] = self.port_input.get()
    #     default_settings['audio_input_device_id'] = str(
    #         self.device_name_id_dict.get(self.input_device_var.get().lstrip('0123456789. ')))
    #     default_settings['audio_output_device_id'] = str(
    #         self.device_name_id_dict.get(self.output_device_var.get().lstrip('0123456789. ')))
    #     with open(Config.CONFIG_FILE, 'w') as configfile:
    #         parser.write(configfile)


    def to_json(self):
        return json.dumps({key: value.__dict__ for key, value in self.__dict__.items()})

    class Setting:
        def __init__(self, input_type, options=None, default=None):
            self.input_type = input_type
            self.options = options
            self.default = default

        def to_json(self):
            return json.dumps({key: value for key, value in self.__dict__.items()})


cli_parser = argparse.ArgumentParser(prog='gui')
cli_parser.add_argument('-s', '--settings', help='returns default vojp settings', action='store_true')

args = cli_parser.parse_args()
if args.settings:
    print(ElectronGuiSettings().to_json())
    sys.stdout.flush()




