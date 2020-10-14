import queue
import asyncio
import opuslib
import time
import sounddevice as sd
import numpy as np


class AudioProcessor:

    def __init__(self,
                 input_sample_rate=48000,
                 output_sample_rate=48000,
                 audio_per_packet=0.01,
                 channels=1,
                 audio_input_device_id='default',
                 audio_output_device_id='default'):
        """
        Parameters
        ----------
        :param input_sample_rate: integer, optional; Defaults to 48000
             the audio sample rate in hertz
        :param audio_per_packet: float, optional; Defaults to 0.01 which equals 10 milliseconds
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
        self.audio_per_packet = audio_per_packet
        self.channels = channels
        self.frame_size = int(input_sample_rate * audio_per_packet * channels)  # Synonymous to block size
        self.opus_encoder = opuslib.Encoder(fs=self.input_sample_rate,
                                            channels=self.channels,
                                            application=opuslib.APPLICATION_VOIP)
        self.input_buffer = queue.Queue()
        self.output_buffer = queue.Queue()


        if audio_input_device_id != 'default':
            sd.default.device[0] = int(audio_input_device_id)
        if audio_output_device_id != 'default':
            sd.default.device[1] = int(audio_output_device_id)

    async def get_mic_input(self):
        queue_in = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def process_input_stream(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(queue_in.put_nowait, (indata.copy(), status))

        with sd.InputStream(callback=process_input_stream,
                            samplerate=self.input_sample_rate,
                            channels=self.channels,
                            blocksize=self.frame_size,
                            latency='low',
                            dtype='int16'):
            while True:
                indata, status = await queue_in.get()
                print(time.monotonic())
                print('in ' + str(self.input_buffer.qsize()))
                yield indata, status

    async def convert_stream_to_opus(self):
        async for indata, status in self.get_mic_input():
            # print('converting')
            audio_frame = self.opus_encoder.encode(pcm_data=indata.tobytes(), frame_size=self.frame_size)
            yield audio_frame

    async def convert_opus_to_stream(self, opus_decoder, opus_data):
        return opus_decoder.decode(opus_data=opus_data, frame_size=self.frame_size)

    async def generate_output_stream(self, audio_stream):

        queue_out = queue.Queue()

        # Create buffer for starting the audio stream. Prevents beeping sound
        buffer = bytes(self.frame_size * 2)
        queue_out.put_nowait(buffer)

        audio_packet_list = [buffer]

        def process_output_stream(outdata, frame_count, time_info, status):
            print(time.monotonic())
            if len(audio_packet_list) > 0:
                outdata[:] = audio_packet_list.pop(0)
            else:
                outdata[:] = buffer
            print(time.monotonic())
            print('output done')

        output_stream = sd.RawOutputStream(callback=process_output_stream,
                                           samplerate=self.output_sample_rate,
                                           channels=self.channels,
                                           blocksize=self.frame_size,
                                           latency='low',
                                           dtype='int16')

        with output_stream:
            while True:
                # print(time.monotonic())
                # print('out 1 - ' + str(len(audio_packet_list)))
                audio_packet = await audio_stream.get()
                audio_packet_list.append(audio_packet)
                # print(time.monotonic())
                # print('out 2 - ' + str(len(audio_packet_list)))


def set_default_device():
    sound_devices = sd.query_devices()
    for device in sound_devices:
        if device.get('max_input_channels') > 0:
            sd.default.device = device.get('name')
            break


def get_all_devices():
    sound_devices = sd.query_devices()
    for index, device in enumerate(sound_devices):
        device['device_index'] = index
    return sound_devices
