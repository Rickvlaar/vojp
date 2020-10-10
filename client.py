import asyncio
import pickle
import numpy as np
import opuslib
import soundfile as sf
from audio_processor import AudioProcessor


class UdpClient(asyncio.DatagramProtocol):
    def __init__(self, ip, port, input_sample_rate, output_sample_rate, audio_input_device_id,
                 audio_output_device_id):
        self.loop = asyncio.get_running_loop()
        self.transport = asyncio.BaseTransport()
        self.server_address = (ip, port)
        self.logged_in_clients = dict()
        self.audio_input_buffer = asyncio.Queue()
        self.audio_output_buffer = asyncio.Queue()
        self.input_sample_rate = input_sample_rate
        self.output_sample_rate = output_sample_rate
        self.audio_processor = AudioProcessor(input_sample_rate=self.input_sample_rate,
                                              audio_input_device_id=audio_input_device_id,
                                              audio_output_device_id=audio_output_device_id)
        self.frame_size = self.audio_processor.frame_size
        self.recording = False
        self.recording_file = sf.SoundFile(file='test.wav', mode='w', samplerate=output_sample_rate, channels=1)
        self.audio_udp_object = AudioUDPObject(sample_rate=self.input_sample_rate, frame_size=self.frame_size)

        asyncio.create_task(self.start_client())

    def datagram_received(self, data, addr):
        """
        Incoming data packets are put on the queue to be processed for output later

        :param data: incoming data packet
        :param addr: IP address and port of sender
        """

        # print("Client Received:", data)
        udp_object = pickle.loads(data)
        self.audio_input_buffer.put_nowait((addr, udp_object))

        if addr not in self.logged_in_clients:
            self.logged_in_clients[addr] = ListeningClient(address=addr,
                                                           sample_rate=udp_object.sample_rate,
                                                           frame_size=udp_object.frame_size)

    async def decode_audio(self):
        while True:
            client_data_tuple = await self.audio_input_buffer.get()
            encoded_audio_packet = client_data_tuple[1].audio_packet
            current_decoder = self.logged_in_clients.get(client_data_tuple[0]).opus_decoder
            decoded_audio_packet = await self.audio_processor.convert_opus_to_stream(opus_decoder=current_decoder,
                                                                                     opus_data=encoded_audio_packet)
            # print(decoded_audio_packet)
            self.audio_output_buffer.put_nowait(decoded_audio_packet)

    async def output_audio(self):
        print('Starting Output')
        while True:
            async for audio_packet in self.audio_processor.generate_output_stream(self.audio_output_buffer):
                # print(audio_packet)
                if self.recording:
                    await self.record_audio_stream(audio_packet)

    async def stream_mic_input(self):
        """
        Streams the clients microphone input to the server
        """
        while True:
            async for input_packet in self.audio_processor.convert_stream_to_opus():
                self.audio_udp_object.audio_packet = input_packet
                upd_object = pickle.dumps(self.audio_udp_object)
                # print(upd_object)
                self.transport.sendto(upd_object, self.server_address)

    async def record_audio_stream(self, audio_packet):
        self.recording_file.buffer_write(audio_packet, dtype='int16')

    async def start_client(self):
        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
                protocol_factory=lambda: self,
                remote_addr=self.server_address)
        await asyncio.gather(self.stream_mic_input(),
                             self.decode_audio(),
                             self.output_audio())


class AudioUDPObject(object):

    def __init__(self, sample_rate, frame_size, audio_packet=b''):
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.audio_packet = audio_packet


class ListeningClient:

    def __init__(self, address, sample_rate, frame_size):
        self.address = address
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.opus_decoder = opuslib.Decoder(fs=sample_rate, channels=1)


async def start_client(ip, port, input_sample_rate, output_sample_rate, audio_input_device_id,
                       audio_output_device_id):
    print('starting client')
    UdpClient(ip=ip, port=port, input_sample_rate=input_sample_rate, output_sample_rate=output_sample_rate,
              audio_input_device_id=audio_input_device_id,
              audio_output_device_id=audio_output_device_id)
