import queue
import asyncio
import opuslib
import logging
import opuslib.api.encoder
import opuslib.api.ctl
import sounddevice as sd
import numpy as np


class AudioProcessor:

    def __init__(self,
                 input_sample_rate=48000,
                 output_sample_rate=48000,
                 packet_length=0.01,
                 channels=1,
                 audio_input_device_id='default',
                 audio_output_device_id='default'):
        """
        Parameters
        ----------
        :param input_sample_rate: integer, optional; Defaults to 48000
             the audio sample rate in hertz
        :param packet_length: float, optional; Defaults to 0.01 which equals 10 milliseconds
            audio fragment length in seconds
        :param channels: integer, optional; Defaults to 1
            number of channels, either 1 for mono or 2 for stereo.
        :param audio_input_device_id: string, optional;  Defaults to system default
            the selected audio input device name
        :param audio_output_device_id: string, optional; Defaults to system default
            the selected audio output device name
        """
        self.input_sample_rate = input_sample_rate
        self.output_sample_rate = output_sample_rate
        self.packet_length = packet_length
        self.channels = channels
        self.frame_size = int(input_sample_rate * packet_length * channels)  # Synonymous to block size
        self.opus_encoder = opuslib.Encoder(fs=self.input_sample_rate,
                                            channels=self.channels,
                                            application=opuslib.APPLICATION_VOIP)
        # opuslib.api.encoder.encoder_ctl(self.opus_encoder.encoder_state, opuslib.api.ctl.set_inband_fec, 1)
        # opuslib.api.encoder.encoder_ctl(self.opus_encoder.encoder_state, opuslib.api.ctl.set_packet_loss_perc, 30)

        self.input_buffer = queue.Queue()
        self.output_buffer = list()
        self.max_buffer_size = 0.05 / packet_length  # allow a buffer size of 50ms

        if audio_input_device_id != 'default':
            sd.default.device[0] = int(audio_input_device_id)
        if audio_output_device_id != 'default':
            sd.default.device[1] = int(audio_output_device_id)

    async def get_mic_input(self):
        queue_in = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def process_input_stream(indata, frame_count, time_info, status):
            raw_indata = indata.copy().tobytes()
            loop.call_soon_threadsafe(queue_in.put_nowait, (raw_indata, status))

        with sd.InputStream(callback=process_input_stream,
                            samplerate=self.input_sample_rate,
                            channels=self.channels,
                            blocksize=self.frame_size,
                            latency='low',
                            dtype='int16'):
            while True:
                indata, status = await queue_in.get()
                logging.debug(msg='Microphone input packet created')

                yield indata, status


    async def convert_stream_to_opus(self):
        async for indata, status in self.get_mic_input():
            logging.debug(msg='Converting microphone audio packet to opus')
            audio_frame = self.opus_encoder.encode(pcm_data=indata, frame_size=self.frame_size)
            yield audio_frame

    async def convert_opus_to_stream(self, opus_decoder, opus_data):
        return opus_decoder.decode(opus_data=opus_data, frame_size=self.frame_size)

    async def generate_output_stream(self, audio_stream):

        # Create buffer for starting the audio stream. Prevents beeping sound
        packet_of_silence = bytes(self.frame_size * 2)
        self.output_buffer = [packet_of_silence]

        def process_output_stream(outdata, frame_count, time_info, status):
            # If the buffer is empty, play silence
            logging.debug(msg='Playing audio')
            if len(self.output_buffer) > 0:
                outdata[:] = self.output_buffer.pop(0)
            else:
                outdata[:] = packet_of_silence

        output_stream = sd.RawOutputStream(callback=process_output_stream,
                                           samplerate=self.output_sample_rate,
                                           channels=self.channels,
                                           blocksize=self.frame_size,
                                           latency='low',
                                           dtype='int16')

        with output_stream:
            while True:
                # input_time_start = time.monotonic()
                audio_packet = await audio_stream.get()
                self.output_buffer.append(audio_packet)
                logging.debug(msg='Outputting audio packet. Current buffersize is ' + str(len(self.output_buffer)))
                # input_time_end = time.monotonic()
                # delta_time = input_time_end - input_time_start
                # print('output time = ' + str(delta_time))

    def get_buffer_size(self):
        return len(self.output_buffer)


def set_default_device():
    sound_devices = sd.query_devices()
    for device in sound_devices:
        if device.get('max_input_channels') > 0:
            sd.default.device = device.get('name')
            break


def get_all_devices():
    sound_devices = sd.query_devices()
    logging.info(msg='Audio devices available on system:\n' + str(sound_devices))
    for index, device in enumerate(sound_devices):
        device['device_index'] = index
    return sound_devices
