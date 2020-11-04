import logging
import asyncio
import pickle
import uuid
import numpy as np
import time
import audioop
import opuslib
import soundfile as sf
from datetime import datetime
from audio_processor import AudioProcessor
from os import path


class UdpClient(asyncio.DatagramProtocol):
    started_at = time.monotonic()

    def __init__(self, ip, port, input_sample_rate, output_sample_rate, audio_input_device_id,
                 audio_output_device_id, packet_length=0.01, record_audio=False):
        self.loop = asyncio.get_running_loop()
        self.transport = asyncio.BaseTransport()
        self.server_address = (ip, port)
        self.logged_in_clients = dict()
        self.audio_output_buffer = asyncio.Queue()
        self.packet_length = packet_length
        self.input_sample_rate = input_sample_rate
        self.output_sample_rate = output_sample_rate
        self.audio_processor = AudioProcessor(input_sample_rate=self.input_sample_rate,
                                              packet_length=self.packet_length,
                                              audio_input_device_id=audio_input_device_id,
                                              audio_output_device_id=audio_output_device_id)
        self.frame_size = self.audio_processor.frame_size
        self.max_buffer_size = 1
        self.record_audio = record_audio
        # TODO: Fix the recording path bug on windows
        # self.recording_file = sf.SoundFile(file=str(datetime.now()) + '.wav',
        #                                    mode='w',
        #                                    samplerate=output_sample_rate,
        #                                    channels=1)
        self.audio_udp_object = AudioUDPObject(sample_rate=self.input_sample_rate,
                                               frame_size=self.frame_size,
                                               sent_at=time.time_ns())
        self.new_client_event = asyncio.Event()
        self.latency = 0
        self.sent = 0
        self.received = 0

    async def start_client(self):
        logging.info(msg='Starting client')
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

        udp_object = pickle.loads(data)
        latency = (time.time_ns() - udp_object.sent_at) / 1000000
        self.latency = round(latency, 1)
        self.received += 1
        if udp_object.client_id not in self.logged_in_clients:
            new_client = ListeningClient(address=addr,
                                         sample_rate=udp_object.sample_rate,
                                         frame_size=udp_object.frame_size,
                                         parent_frame_size=self.frame_size)
            new_client.latency = latency
            self.logged_in_clients[udp_object.client_id] = new_client
            asyncio.create_task(new_client.decode_audio())
            logging.info(msg='New client registered. Currently listening to ' + str(len(self.logged_in_clients)) + ' clients')
            print('Logged in Clients: ' + str(len(self.logged_in_clients)))
            self.new_client_event.set()
        else:
            this_client = self.logged_in_clients.get(udp_object.client_id)
            if this_client.latency < latency + 100:
                this_client.encoded_audio_packet_queue.put_nowait(udp_object.audio_packet)

    async def stream_mic_input(self):
        """
        Streams the clients microphone input to the server
        """
        while True:
            async for input_packet in self.audio_processor.convert_stream_to_opus():
                logging.debug(msg='Streaming microphone input')
                # input_time_start = time.monotonic()
                # print('streaming')
                self.audio_udp_object.audio_packet = input_packet
                self.audio_udp_object.sent_at = time.time_ns()
                upd_object = pickle.dumps(self.audio_udp_object)
                self.sent += 1
                self.transport.sendto(upd_object, self.server_address)

                # input_time_end = time.monotonic()
                # delta_time = input_time_end - input_time_start
                # print('streaming time = ' + str(delta_time))

    async def sync_streams(self):
        logging.info(msg='Starting client audio stream sync coroutine')
        await self.new_client_event.wait()  # release the loop while waiting for clients
        wait_time = self.packet_length * 0.5
        while True:
            logging.debug(msg='Syncing client audio streams')
            # input_time_start = time.monotonic()
            await asyncio.sleep(wait_time)  # reduce cpu usage and free up thread
            if self.audio_processor.get_buffer_size() < self.max_buffer_size:
                combined_fragment = None
                for client in self.logged_in_clients.values():
                    if len(client.decoded_audio_packet_queue) > 0:
                        fragment = client.decoded_audio_packet_queue.pop(0)
                        if combined_fragment is None:
                            combined_fragment = fragment
                        combined_fragment = audioop.add(combined_fragment, fragment, 2)
                    if len(client.decoded_audio_packet_queue) > 5:
                        client.decoded_audio_packet_queue.pop(0)
                if combined_fragment:
                    self.audio_output_buffer.put_nowait(combined_fragment)
                    if self.record_audio:
                        await self.record_audio_stream(combined_fragment)

            # input_time_end = time.monotonic()
            # delta_time = input_time_end - input_time_start
            # print('sync time = ' + str(delta_time))

    async def output_audio(self):
        logging.info(msg='Starting audio output coroutines')

        print('Starting Output')
        asyncio.create_task(self.sync_streams())
        asyncio.create_task(self.audio_processor.generate_output_stream(self.audio_output_buffer))

    async def record_audio_stream(self, audio_packet):
        print('wtf')
        # self.recording_file.buffer_write(audio_packet, dtype='int16')


class AudioUDPObject(object):

    def __init__(self, sample_rate, frame_size, sent_at, audio_packet=b''):
        self.client_id = uuid.uuid4()
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.sent_at = sent_at
        self.audio_packet = audio_packet


class ListeningClient:

    def __init__(self, address, sample_rate, frame_size, parent_frame_size):
        self.address = address
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.parent_frame_size = parent_frame_size
        self.latency = 0
        self.encoded_audio_packet_queue = asyncio.Queue()
        self.decoded_audio_packet_queue = list()
        self.opus_decoder = opuslib.Decoder(fs=sample_rate, channels=1)

    async def decode_audio(self):
        logging.info(msg='Client ' + str(self.address) + ' latency is ' + str(self.latency) + ' ms')
        while True:
            logging.debug(msg='Decoding client ' + str(self.address) + ' audio packet')
            encoded_audio_packet = await self.encoded_audio_packet_queue.get()
            decoded_audio_packet = self.opus_decoder.decode(opus_data=encoded_audio_packet, frame_size=self.frame_size)
            if self.frame_size > self.parent_frame_size:
                split_factor = self.frame_size % self.parent_frame_size
                decoded_audio_packet = decoded_audio_packet.split(maxsplit=split_factor)

            self.decoded_audio_packet_queue.append(decoded_audio_packet)
            # input_time_end = time.monotonic()
            # delta_time = (input_time_end - input_time_start) * 1000
            # delta_time = round(delta_time, 1)
            # print('Decoding time = ' + str(delta_time) + ' ms')
