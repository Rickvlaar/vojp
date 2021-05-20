import json
import configparser
import logging
from audio_processor import get_all_devices
from config import Config


class ElectronGuiSettings:
    debug_level_options = {value: value for value in ['INFO', 'DEBUG']}
    sample_rate_options = {value: value for value in [48000, 32000, 16000, 12000, 8000]}
    all_devices = get_all_devices()
    input_devices_dict = {device['device_index']: device['name'] for device in all_devices if device['max_input_channels'] > 0}
    output_devices_dict = {device['device_index']: device['name'] for device in all_devices if device['max_output_channels'] > 0}

    def __init__(self):
        self.ip_address = self.Setting(input_type='input', setting_type='connection')
        self.port = self.Setting(input_type='input', setting_type='connection', value=5000)
        self.input_sample_rate = self.Setting(input_type='datalist', setting_type='device', options=self.sample_rate_options, value=[48000, 48000])
        self.output_sample_rate = self.Setting(input_type='datalist', setting_type='device', options=self.sample_rate_options, value=[48000, 48000])
        self.debug_level = self.Setting(input_type='datalist', setting_type='connection', options=self.debug_level_options, value=['INFO', 'INFO'])
        self.input_device = self.Setting(input_type='datalist', setting_type='device', options=self.input_devices_dict)
        self.output_device = self.Setting(input_type='datalist', setting_type='device',  options=self.output_devices_dict)
        self.packet_length = self.Setting(input_type='input', setting_type='connection', value=10)
        self.buffer_size = self.Setting(input_type='input', setting_type='connection', value=10)
        self.host_server = self.Setting(input_type='checkbox', setting_type='session', value=False)
        self.echo_mode = self.Setting(input_type='checkbox', setting_type='session', value=False)
        self.record = self.Setting(input_type='checkbox', setting_type='session', value=False)
        self.read_config_ini()
        self.log_devices()

    def read_config_ini(self):
        parser = configparser.ConfigParser()
        parser.read(Config.CONFIG_FILE)
        default_settings = parser['DEFAULT']
        self.ip_address.value = default_settings.get('ip_address')
        self.port.value = default_settings.get('port') if default_settings.get('port') else 5000
        self.input_device.value = [default_settings['input_device'], self.input_devices_dict.get(int(default_settings['input_device']))]
        self.output_device.value = [default_settings['output_device'], self.output_devices_dict.get(int(default_settings['output_device']))]

    def save_config_ini(self):
        parser = configparser.ConfigParser()
        default_settings = parser['DEFAULT']
        for setting_name, setting in self.__dict__.items():
            default_settings[setting_name] = str(setting.value)
        with open(Config.CONFIG_FILE, 'w') as configfile:
            parser.write(configfile)

    def to_json(self):
        return json.dumps({key: value.__dict__ for key, value in self.__dict__.items()})

    def read_from_electron(self, json_string):
        settings_dict = json.loads(json_string)
        for setting_name, setting in self.__dict__.items():
            setting_value = settings_dict.get(setting_name)
            if setting_value.isdigit():
                setting.value = int(setting_value)
            elif setting_value == 'true':
                setting.value = True
            elif setting_value == 'false':
                setting.value = False
            else:
                setting.value = setting_value
        return settings_dict

    def log_devices(self):
        logging.info(msg='Available devices:\n' + str(self.all_devices))

    def __repr__(self):
        return str({key: value for key, value in self.__dict__.items()})

    class Setting:
        def __init__(self, input_type, setting_type, options=None, value=None):
            self.input_type = input_type
            self.setting_type = setting_type
            self.options = options
            self.value = value

        def to_json(self):
            return json.dumps({key: value for key, value in self.__dict__.items()})

        def __repr__(self):
            return str({key: value for key, value in self.__dict__.items()})
