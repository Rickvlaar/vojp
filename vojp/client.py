import logging
import asyncio
import pickle
import time
import audioop
import opuslib
import soundfile as sf
from datetime import datetime
from vojp.audio_processor import AudioProcessor
from vojp.config import Config


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
        self.max_buffer_size = 5  # buffer size in packets
        self.record_audio = record_audio
        self.recording_file = sf.SoundFile(
            file=Config.RECORDING_DIR + '/' + str(datetime.now()).replace(':', '_') + '.wav',
            mode='w',
            samplerate=output_sample_rate,
            channels=1) if record_audio else None
        self.new_client_event = asyncio.Event()
        self.gui_socket_connection = None
        self.latency = 0
        self.sent = 0
        self.received = 0

    async def start_client(self):
        logging.info(msg='Starting client')
        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
                protocol_factory=lambda: self,
                remote_addr=self.server_address)
        try:
            self.gui_socket_connection, _ = await loop.create_connection(
                protocol_factory=lambda: self,
                host='127.0.0.1',
                port=1337)
        except ConnectionError:
            logging.warning(msg='Unable to connect to Electron GUI socket')
            pass

        await asyncio.gather(self.stream_mic_input(),
                             self.output_audio(),
                             self.update_gui())

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
            logging.info(
                    msg='New client registered. Currently listening to ' + str(
                        len(self.logged_in_clients)) + ' clients')
            self.new_client_event.set()
        else:
            this_client = self.logged_in_clients.get(udp_object.client_id)
            if latency < this_client.latency + self.max_buffer_size * 10:
                this_client.audio_object_queue.put_nowait(udp_object)
            else:
                logging.warning(msg='Dropping packet due to latency. Latency was: ' + str(latency) + 'ms')

    async def stream_mic_input(self):
        """
        Streams the clients microphone input to the server
        """
        while True:
            async for audio_object in self.audio_processor.convert_stream_to_opus():
                logging.debug(msg='Streaming microphone input')
                audio_object.sent_at = time.time_ns()
                upd_object = pickle.dumps(audio_object)
                self.sent += 1
                self.transport.sendto(upd_object, self.server_address)

    async def sync_streams(self):
        logging.info(msg='Starting client audio stream sync coroutine')
        wait_time = self.packet_length * 0.1
        while True:
            logging.debug(msg='Syncing client audio streams')
            await asyncio.sleep(wait_time)  # reduce cpu usage and free up thread
            audio_object = await self.read_audio_output_buffer()
            if self.record_audio and audio_object and audio_object.audio_packet:
                await self.record_audio_stream(audio_object.audio_packet)
            logging.debug(msg='Sync finished')

    async def update_gui(self):
        while True:
            await asyncio.sleep(0.1)
            if self.audio_processor.end_to_end_latency and self.gui_socket_connection:
                self.gui_socket_connection.write(bytes(str(self.audio_processor.end_to_end_latency), 'utf-8'))

    async def read_audio_output_buffer(self):
        combined_fragment = None
        audio_object = None
        if self.audio_processor.get_buffer_size() < self.max_buffer_size:
            for client in self.logged_in_clients.values():
                if len(client.decoded_audio_object_queue) > 0:
                    audio_object = client.decoded_audio_object_queue.pop(0)
                    if combined_fragment is None:
                        combined_fragment = audio_object.audio_packet
                    combined_fragment = audioop.add(combined_fragment, audio_object.audio_packet, 2)
                if len(client.decoded_audio_object_queue) > 5:
                    logging.warning(msg='Buffer overload. Skipping packet. Buffer size is ' + str(
                            len(client.decoded_audio_object_queue)))
                    client.decoded_audio_object_queue.pop(0)
            if combined_fragment:
                audio_object.audio_packet = combined_fragment
                self.audio_output_buffer.put_nowait(audio_object)
        return audio_object

    async def output_audio(self):
        logging.info(msg='Starting audio output coroutines')

        await asyncio.gather(self.sync_streams(),
                             self.audio_processor.generate_output_stream(self.audio_output_buffer))

    async def record_audio_stream(self, audio_packet):
        self.recording_file.buffer_write(audio_packet, dtype='int16')


class ListeningClient:

    def __init__(self, address, sample_rate, frame_size, parent_frame_size):
        self.address = address
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.parent_frame_size = parent_frame_size
        self.latency = 0
        self.audio_object_queue = asyncio.Queue()
        self.decoded_audio_object_queue = list()
        self.opus_decoder = opuslib.Decoder(fs=sample_rate, channels=1)

    async def decode_audio(self):
        logging.info(msg='Client ' + str(self.address) + ' latency is ' + str(self.latency) + ' ms')
        while True:
            logging.debug(msg='Decoding client ' + str(self.address) + ' audio packet')
            audio_object = await self.audio_object_queue.get()
            decoded_audio_packet = self.opus_decoder.decode(opus_data=audio_object.audio_packet, frame_size=self.frame_size)
            if self.frame_size > self.parent_frame_size:
                split_factor = self.frame_size % self.parent_frame_size
                decoded_audio_packet = decoded_audio_packet.split(maxsplit=split_factor)

            audio_object.audio_packet = decoded_audio_packet
            self.decoded_audio_object_queue.append(audio_object)
