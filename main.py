import asyncio
from server import AsyncUdpServer
from gui import Gui


async def main():
    # Show Gui
    gui = Gui()
    gui.start_gui()

    # Start Server
    server = AsyncUdpServer()
    await asyncio.create_task(server.start_server())
    # audio_processor = AudioProcessor()
    # Create audio processor and start streaming
    # mic_input_stream = audio_processor.convert_stream_to_opus()
    # async for input_packet in mic_input_stream:
    #     await server.broadcast_message(input_packet)
    # asyncio.get_running_loop().run_forever()


asyncio.run(main(), debug=False)
