import asyncio
import server
from client import UdpClient
from audio_processor import AudioProcessor
from gui import Gui


async def main():
    # Start Server
    asyncio.create_task(server.start_server())
    # Show Gui
    gui = Gui()
    gui.start_gui()
    # Start Client with audioprocessor class
    audio_processor = AudioProcessor()
    # Create audio processor and start streaming
    mic_input_stream = audio_processor.convert_stream_to_opus()
    async for input_packet in mic_input_stream:
        await server.broadcast_message(input_packet)

asyncio.run(main(), debug=False)
