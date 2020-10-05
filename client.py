import asyncio
import numpy as np
import soundfile as sf
from audio_processor import AudioProcessor


class UdpClient(asyncio.DatagramProtocol):
    def __init__(self, ip, port, audio_input_device_name, audio_output_device_name):
        self.loop = asyncio.get_running_loop()
        self.transport = asyncio.BaseTransport()
        self.audio_input_buffer = asyncio.Queue()
        self.audio_output_buffer = asyncio.Queue()
        self.audio_processor = AudioProcessor(audio_input_device_name=audio_input_device_name,
                                              audio_output_device_name=audio_output_device_name)
        self.server_address = (ip, port)
        self.recording = False
        self.recording_file = sf.SoundFile(file='test.wav', mode='w', samplerate=48000, channels=1)
        asyncio.create_task(self.start_client())

    def datagram_received(self, data, addr):
        # print("Client Received:", data)
        self.audio_input_buffer.put_nowait(data)

    async def decode_audio(self):
        while True:
            encoded_audio_packet = await self.audio_input_buffer.get()
            decoded_audio_packet = await self.audio_processor.convert_opus_to_stream(encoded_audio_packet)
            self.audio_output_buffer.put_nowait(decoded_audio_packet)

    async def output_audio(self):
        print('Starting Output')
        while True:
            async for audio_packet in self.audio_processor.generate_output_stream(self.audio_output_buffer):
                if self.recording:
                    await self.record_audio_stream(audio_packet)

    async def stream_mic_input(self):
        while True:
            async for input_packet in self.audio_processor.convert_stream_to_opus():
                self.transport.sendto(input_packet, self.server_address)

    async def record_audio_stream(self, audio_packet):
        with self.recording_file as file:
            file.buffer_write(audio_packet, dtype='int16')

    async def start_client(self):
        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
                protocol_factory=lambda: self,
                remote_addr=self.server_address)
        await asyncio.gather(self.stream_mic_input(),
                             self.decode_audio(),
                             self.output_audio())
        # asyncio.create_task(self.stream_mic_input())
        # asyncio.create_task(self.decode_audio())
        # asyncio.create_task(self.output_audio())


async def start_client(ip, port, audio_input_device_name='bla', audio_output_device_name='bla'):
    print('starting client')
    UdpClient(ip=ip, port=port, audio_input_device_name=audio_input_device_name,
              audio_output_device_name=audio_output_device_name)
