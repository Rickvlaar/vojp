import threading
import asyncio
import socketserver
import socket
import time

# Port 0 means to select an arbitrary unused port
dev_server_address = '127.0.0.1', 5000
this_server_address = '192.168.50.3', 5000
public_server_address = '0.0.0.0', 5000


logged_in_clients = set()
server_transport = None


class AsyncPoepChatUDPRequestHandler(asyncio.DatagramProtocol):

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('Server Received %r from %s' % (message, addr))
        logged_in_clients.add(addr)
        print(logged_in_clients)


async def broadcast_message(message):
        # print('casting')
        for listening_client in logged_in_clients:
            # print('casting to')
            # print(listening_client)
            # print(message)
            # server_transport.sendto(bytes(message, 'utf-8'), listening_client)
            server_transport.sendto(message, listening_client)


async def start_server():
    print('server starting')

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
            protocol_factory=lambda: AsyncPoepChatUDPRequestHandler(),
            local_addr=public_server_address)

    global server_transport
    server_transport = transport


#
#
#
# Synchronous server from here on
#
#
#
def run_sync_server():
    server = socketserver.ThreadingUDPServer(server_address=public_server_address,
                                             RequestHandlerClass=PoepChatUDPRequestHandler)

    with server:
        server.serve_forever()
        # server_thread = threading.Thread(target=server.serve_forever, args=logged_in_clients)
        # server_thread.daemon = True
        # server_thread.start()

def client(ip, port, message):
    # SOCK_DGRAM is the socket type to use for UDP sockets
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # data = "".join(sys.argv[1:])
        data = message
        # As you can see, there is no connect() call; UDP has no connections.
        # Instead, data is directly sent to the recipient via sendto().
        sock.sendto(bytes(data + "\n", "utf-8"), (ip, port))
        received = str(sock.recv(1024), "utf-8")
        print("Sent:     {}".format(data))
        print("Received:     {}".format(received))


class PoepChatUDPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        print(self.request)
        print(self.client_address)
        print(data)
        cur_thread = threading.current_thread()
        # logged_in_clients[self.client_address] = socket
        socket.sendto(data.upper(), self.client_address)
        # broadcast_message('gaatielekaaaahhh')


if __name__ == "__main__":
    server = socketserver.ThreadingUDPServer(server_address=public_server_address, RequestHandlerClass=PoepChatUDPRequestHandler)

    with server:
        server.serve_forever()
        # print(server.server_address)
        # ip, port = dev_server_address
        # print(socket.gethostname())
        # print(socket.gethostbyname('RickForce'))
        # # Start a thread with the server -- that thread will then start one
        # # more thread for each request
        # server_thread = threading.Thread(target=server.serve_forever)
        #
        # # Exit the server thread when the main thread terminates
        # server_thread.daemon = False
        # server_thread.start()
        # print("Server loop running in thread:", server_thread.name)
        # print(server_thread.ident)
        #
        # cli1 = client(ip, port, '1')
        # cli2 = client(ip, port, '2')
        # cli3 = client(ip, port, '3')
        #
        #
        # index = 0
        # # server.shutdown()
