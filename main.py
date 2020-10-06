import asyncio
from server import AsyncUdpServer
from gui import Gui


async def main():

    # Show Gui
    gui = Gui()
    gui.start_gui()
    await gui.do_some_thing_gui()  # Check if the window has not closed, otherwise stop application

    # Start Server
    server = AsyncUdpServer()
    await asyncio.create_task(server.start_server())


    # audio_processor = AudioProcessor()
    # Create audio processor and start streaming
    # mic_input_stream = audio_processor.convert_stream_to_opus()
    # async for input_packet in mic_input_stream:
    #     await server.broadcast_message(input_packet)
    asyncio.get_running_loop().run_forever()

try:
    asyncio.run(main(), debug=True)
except asyncio.CancelledError:
    print('Loop has been stopped successfully')
