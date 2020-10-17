import asyncio
import pickle
import numpy as np
import time
import audioop
import opuslib
import soundfile as sf
from audio_processor import AudioProcessor


class UdpClient(asyncio.DatagramProtocol):
    started_at = time.monotonic()

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
        self.new_client_event = asyncio.Event()
        self.sent = 0
        self.received = 0

    async def start_client(self):
        print('starting client')
        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
                protocol_factory=lambda: self,
                remote_addr=self.server_address)
        await asyncio.gather(self.stream_mic_input(),
                             self.output_audio())

    def datagram_received(self, data, addr):
        """
        Incoming data packets are put on the queue to be processed for output later

        :param data: incoming data packet
        :param addr: IP address and port of sender
        """

        # print("Client Received:", data)
        udp_object = pickle.loads(data)
        self.audio_input_buffer.put_nowait((addr, udp_object))
        self.received += 1
        if addr not in self.logged_in_clients:
            new_client = ListeningClient(address=addr,
                                         sample_rate=udp_object.sample_rate,
                                         frame_size=udp_object.frame_size,
                                         parent_frame_size=self.frame_size)

            self.logged_in_clients[addr] = new_client
            asyncio.create_task(new_client.decode_audio())
            print('Logged in Clients: ' + str(len(self.logged_in_clients)))
            self.new_client_event.set()
        else:
            this_client = self.logged_in_clients.get(addr)
            this_client.encoded_audio_packet_queue.put_nowait(udp_object.audio_packet)

    async def stream_mic_input(self):
        """
        Streams the clients microphone input to the server
        """
        while True:
            async for input_packet in self.audio_processor.convert_stream_to_opus():
                # input_time_start = time.monotonic()
                # print('streaming')
                self.audio_udp_object.audio_packet = input_packet
                upd_object = pickle.dumps(self.audio_udp_object)
                # print(upd_object)
                self.sent += 1
                self.transport.sendto(upd_object, self.server_address)

                # input_time_end = time.monotonic()
                # delta_time = input_time_end - input_time_start
                # print('streaming time = ' + str(delta_time))

    async def decode_audio(self):
        while True:
            input_time_start = time.monotonic()
            # print('decoding')

            client_data_tuple = await self.audio_input_buffer.get()
            encoded_audio_packet = client_data_tuple[1].audio_packet
            current_decoder = self.logged_in_clients.get(client_data_tuple[0]).opus_decoder
            decoded_audio_packet = await self.audio_processor.convert_opus_to_stream(opus_decoder=current_decoder,
                                                                                     opus_data=encoded_audio_packet)
            # print(decoded_audio_packet)
            self.audio_output_buffer.put_nowait(decoded_audio_packet)
            input_time_end = time.monotonic()
            delta_time = input_time_end - input_time_start
            print('decoding time = ' + str(delta_time))

    async def sync_streams(self):
        await self.new_client_event.wait()  # release the loop while waiting for clients
        wait_time = 0.005
        while True:
            # input_time_start = time.monotonic()
            await asyncio.sleep(wait_time)  # reduce cpu usage and free up thread
            # print('Now syncing this number of clients: ' + str(len(self.logged_in_clients)))
            combined_fragment = bytes(self.frame_size * 2)
            for client in self.logged_in_clients.values():
                if len(client.decoded_audio_packet_queue) > 0 and self.audio_output_buffer.qsize() < 2:  # Allow buffer to empty to prevent packages piling
                    fragment = client.decoded_audio_packet_queue.pop(0)
                    combined_fragment = audioop.add(combined_fragment, fragment, 2)
                    # self.audio_output_buffer.put_nowait(combined_fragment)
                    await self.audio_output_buffer.put(combined_fragment)
            if self.recording:
                await self.record_audio_stream(combined_fragment)
            # input_time_end = time.monotonic()
            # delta_time = input_time_end - input_time_start
            # print('sync time = ' + str(delta_time))

    async def output_audio(self):
        print('Starting Output')
        print(time.monotonic())
        asyncio.create_task(self.sync_streams())
        asyncio.create_task(self.audio_processor.generate_output_stream(self.audio_output_buffer))

    async def record_audio_stream(self, audio_packet):
        self.recording_file.buffer_write(audio_packet, dtype='int16')


class AudioUDPObject(object):

    def __init__(self, sample_rate, frame_size, audio_packet=b''):
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.audio_packet = audio_packet


class ListeningClient:

    def __init__(self, address, sample_rate, frame_size, parent_frame_size):
        self.address = address
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.parent_frame_size = parent_frame_size
        self.encoded_audio_packet_queue = asyncio.Queue()
        self.decoded_audio_packet_queue = list()
        self.opus_decoder = opuslib.Decoder(fs=sample_rate, channels=1)

    async def decode_audio(self):
        while True:
            # print(time.monotonic())
            # print('decoding')
            encoded_audio_packet = await self.encoded_audio_packet_queue.get()
            decoded_audio_packet = self.opus_decoder.decode(opus_data=encoded_audio_packet, frame_size=self.frame_size)
            if self.frame_size > self.parent_frame_size:
                split_factor = self.frame_size % self.parent_frame_size
                decoded_audio_packet = decoded_audio_packet.split(maxsplit=split_factor)

            self.decoded_audio_packet_queue.append(decoded_audio_packet)
            # print(time.monotonic())
            # print('decoding finished')


async def start_client(ip, port, input_sample_rate, output_sample_rate, audio_input_device_id,
                       audio_output_device_id):
    client = UdpClient(ip=ip,
                       port=port,
                       input_sample_rate=input_sample_rate,
                       output_sample_rate=output_sample_rate,
                       audio_input_device_id=audio_input_device_id,
                       audio_output_device_id=audio_output_device_id)
    await client.start_client()
