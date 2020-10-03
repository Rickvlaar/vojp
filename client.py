import asyncio
import numpy as np
import soundfile as sf
from audio_processor import AudioProcessor

class UdpClient(asyncio.DatagramProtocol):
    def __init__(self, ip, port, audio_input_device_name, audio_output_device_name):
        self.loop = asyncio.get_running_loop()
        self.transport = None
        self.audio_input_buffer = asyncio.Queue()
        self.audio_output_buffer = asyncio.Queue()
        self.audio_processor = AudioProcessor(audio_input_device_name=audio_input_device_name, audio_output_device_name=audio_output_device_name)
        self.address = (ip, port)
        asyncio.create_task(self.start_client())

    def connection_made(self, transport):
        print('Client connection made')
        self.transport = transport
        transport.sendto(b'here I am', self.address)

    def datagram_received(self, data, addr):
        # print("Client Received:", data)
        self.audio_input_buffer.put_nowait(data)

    async def encode_audio(self):
        while True:
            decoded_audio_packet = await self.audio_input_buffer.get()
            encoded_audio_packet = await self.audio_processor.convert_opus_to_stream(decoded_audio_packet)
            self.audio_output_buffer.put_nowait(encoded_audio_packet)

    async def output_audio(self):
        print('Starting Output')
        async for output in self.audio_processor.generate_output_stream(self.audio_output_buffer):
            await asyncio.sleep(0)

    async def record_audio_stream(self):
        with sf.SoundFile(file='test.wav', mode='w', samplerate=48000, channels=1) as file:
            audio_packet = await self.audio_input_buffer.get()
            # print(len(audio_packet))
            file.buffer_write(await self.audio_processor.convert_opus_to_stream(audio_packet), dtype='int16')

    async def start_client(self):
        loop = asyncio.get_running_loop()
        await loop.create_datagram_endpoint(
                protocol_factory=lambda: self,
                remote_addr=self.address)
        asyncio.create_task(self.encode_audio())
        asyncio.create_task(self.output_audio())


async def start_client(ip, port, audio_input_device_name='bla', audio_output_device_name='bla'):
    print('starting client')
    UdpClient(ip=ip, port=port, audio_input_device_name=audio_input_device_name, audio_output_device_name=audio_output_device_name)