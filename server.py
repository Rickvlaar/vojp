import asyncio

# Port 0 means to select an arbitrary unused port
dev_server_address = '127.0.0.1', 5000
this_server_address = '192.168.50.3', 5000
public_server_address = '0.0.0.0', 5000


class AsyncUdpServer:

    def __init__(self):
        self.transport = asyncio.BaseTransport()
        self.request_handler = AsyncUdpServer.AsyncUDPRequestHandler()
        self.logged_in_clients = self.request_handler.logged_in_clients
        self.audio_input_buffer = self.request_handler.input_buffer

    async def broadcast_message(self):
        # Filter out packets from client sending the packet
        while True:
            received_packet_map = await self.audio_input_buffer.get()
            for listening_client in self.logged_in_clients:
                # print('casting to')
                # print(listening_client)
                self.transport.sendto(received_packet_map[listening_client], listening_client)

                # if listening_client not in received_packet_map:
                #     self.transport.sendto(received_packet_map[listening_client], listening_client)

    async def start_server(self):
        print('server starting')
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
            received_packet_map = {ip_address: data}
            self.input_buffer.put_nowait(received_packet_map)
