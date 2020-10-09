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
    asyncio.get_running_loop().run_forever()


async def shutdown():
    loop = asyncio.get_running_loop()
    tasks = [task for task in asyncio.all_tasks() if task != asyncio.current_task()]
    [task.cancel() for task in tasks]
    done, pending = await asyncio.wait(await asyncio.gather(*tasks, return_exceptions=True))
    loop.stop()


if __name__ == '__main__':

    try:
        asyncio.run(main(), debug=True)
    except:
        # asyncio.get_running_loop().create_task(shutdown())
        print('Loop has been stopped successfully')
