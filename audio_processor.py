import queue
import asyncio
import opuslib
import sounddevice as sd
import soundfile as sf
import numpy as np


class AudioProcessor:

    def __init__(self, sample_rate=48000, audio_per_packet=0.0025, channels=1, audio_input_device_name='default',
                 audio_output_device_name='default'):
        """
        Parameters
        ----------
        sample_rate: integer, optional; Defaults to 48000
             the audio sample rate in hertz
        audio_per_packet: float, optional; Defaults to 0.01 which equals 10 milliseconds
            audio fragment length in seconds
        channels: integer, optional; Defaults to 1
            number of channels, either 1 for mono or 2 for stereo.
        """
        self.sample_rate = sample_rate
        self.audio_per_packet = audio_per_packet
        self.channels = channels
        self.frame_size = int(sample_rate * audio_per_packet * channels)  # Synonymous to block size
        print(self.frame_size)
        self.opus_encoder = opuslib.Encoder(fs=self.sample_rate,
                                            channels=self.channels,
                                            application=opuslib.APPLICATION_VOIP)
        self.opus_decoder = opuslib.Decoder(fs=self.sample_rate,
                                            channels=self.channels)
        self.output_buffer = queue.Queue()

        if audio_input_device_name != 'default':
            sd.default.device[0] = audio_input_device_name
            print(sd.default.device)
        if audio_output_device_name != 'default':
            sd.default.device[1] = audio_output_device_name
            print(sd.default.device)

    async def get_mic_input(self):
        queue_in = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def process_input_stream(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(queue_in.put_nowait, (indata.copy(), status))

        with sd.InputStream(callback=process_input_stream,
                            samplerate=self.sample_rate,
                            channels=self.channels,
                            blocksize=self.frame_size,
                            dtype='int16'):
            while True:
                indata, status = await queue_in.get()
                yield indata, status

    async def convert_stream_to_opus(self):
        async for indata, status in self.get_mic_input():
            audio_frame = self.opus_encoder.encode(pcm_data=indata.tobytes(), frame_size=self.frame_size)
            yield audio_frame

    async def convert_opus_to_stream(self, opus_data):
        return self.opus_decoder.decode(opus_data=opus_data, frame_size=self.frame_size)

    async def generate_output_stream(self, audio_stream):

        queue_out = queue.Queue()

        # Create buffer for starting the audio stream. Prevents beeping sound
        buffer = b'\x00' * self.frame_size * sd.default.channels[1]
        queue_out.put_nowait(buffer)

        def proces_output_stream(outdata, frame_count, time_info, status):
            if queue_out.qsize() != 0:
                outdata[:] = queue_out.get_nowait()


        output_stream = sd.RawOutputStream(callback=proces_output_stream,
                                           samplerate=self.sample_rate,
                                           channels=self.channels,
                                           blocksize=self.frame_size,
                                           dtype='int16')

        with output_stream:
            while True:
                audio_packet = await audio_stream.get()
                queue_out.put_nowait(audio_packet)
                yield audio_packet


def set_default_device():
    sound_devices = sd.query_devices()
    print(sd.default.device)
    for device in sound_devices:
        if device.get('max_input_channels') > 0:
            sd.default.device = device.get('name')
            break


def get_all_devices():
    sound_devices = sd.query_devices()
    return sound_devices
