import asyncio
import logging
from gui import Gui


logging.basicConfig(filename='logs/voip.log', format='%(asctime)s  %(levelname)s:%(message)s', level=logging.DEBUG)


async def main():
    # Show Gui
    gui = Gui()
    gui.start_gui()

    while True:
        await asyncio.sleep(50000)


async def shutdown():
    logging.info(msg='Shutting down asyncio event loop')
    loop = asyncio.get_running_loop()
    tasks = [task for task in asyncio.all_tasks() if task != asyncio.current_task()]
    [task.cancel() for task in tasks]
    done, pending = await asyncio.wait(await asyncio.gather(*tasks, return_exceptions=True))
    loop.stop()


if __name__ == '__main__':

    try:
        asyncio.run(main(), debug=False)
    except:
        logging.info(msg='Asyncio event loop has been stopped successfully')
        print('Loop has been stopped successfully')
