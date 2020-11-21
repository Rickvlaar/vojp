import asyncio
import logging

# Port 0 means to select an arbitrary unused port
dev_server_address = '127.0.0.1', 5000
this_server_address = '192.168.50.3', 5000
public_server_address = '0.0.0.0', 5000


class AsyncUdpServer:

    def __init__(self, echo_mode=False):
        self.echo_mode = echo_mode
        self.transport = asyncio.BaseTransport()
        self.request_handler = AsyncUdpServer.AsyncUDPRequestHandler()
        self.logged_in_clients = self.request_handler.logged_in_clients
        self.audio_input_buffer = self.request_handler.input_buffer
        self.sent = 0
        self.received = 0

    async def broadcast_message(self):
        # Filter out packets from client sending the packet
        while True:
            received_packet_tuple = await self.audio_input_buffer.get()
            self.received += 1
            for listening_client in self.logged_in_clients:
                data = received_packet_tuple[0]
                sender = received_packet_tuple[1]
                if listening_client != sender or self.echo_mode:
                    self.transport.sendto(data, listening_client)
                    self.sent += 1

    async def start_server(self):
        logging.info(msg='Server starting')
        loop = asyncio.get_running_loop()

        self.transport, self.protocol = await loop.create_datagram_endpoint(
            protocol_factory=lambda: self.request_handler,
            local_addr=public_server_address)
        await self.broadcast_message()

    class AsyncUDPRequestHandler(asyncio.DatagramProtocol):

        def __init__(self):
            self.transport = asyncio.BaseTransport()
            self.logged_in_clients = set()
            self.input_buffer = asyncio.Queue()

        def connection_made(self, transport):
            self.transport = transport

        def datagram_received(self, data, ip_address):
            self.logged_in_clients.add(ip_address)
            received_packet_tuple = (data, ip_address)
            self.input_buffer.put_nowait(received_packet_tuple)
