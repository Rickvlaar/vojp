import asyncio
from server import AsyncUdpServer
from client import UdpClient
from audio_processor import AudioProcessor
from gui import Gui


async def main():
    # Start Server
    server = AsyncUdpServer()
    asyncio.create_task(server.start_server())
    # Show Gui
    gui = Gui()
    gui.start_gui()
    # audio_processor = AudioProcessor()
    # Create audio processor and start streaming
    # mic_input_stream = audio_processor.convert_stream_to_opus()
    # async for input_packet in mic_input_stream:
    #     await server.broadcast_message(input_packet)
    await asyncio.sleep(50000)

asyncio.run(main(), debug=False)
